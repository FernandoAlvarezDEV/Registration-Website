"""
ENO Portal - Backend API V2
===========================
FastAPI + PostgreSQL (Supabase) con:
  - Magic Link authentication (sin contraseñas)
  - Envío de correo automático (Gmail SMTP)
  - Compresión y almacenamiento de imágenes (Supabase Storage)

Ejecutar con:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

import secrets
import re
import logging
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel

from config import settings
from database import get_db, init_db
from models import Registro, RegistroCreate, RegistroResponse, RegistroOut
from email_service import send_confirmation_email
from storage_service import upload_comprobante

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Utilidad: Limpiar teléfono ──────────────────────────────────
def clean_phone(phone: str) -> str:
    """Elimina espacios, guiones, paréntesis, puntos y el prefijo +1."""
    cleaned = re.sub(r'[\s\-().]+', '', phone)
    if cleaned.startswith('+1'):
        cleaned = cleaned[2:]
    return cleaned


# ── Modelos de Request/Response ─────────────────────────────────
class AdminLoginRequest(BaseModel):
    email: str
    phone: str

class UpdateEstadoPago(BaseModel):
    estado_pago: str


# ─────────────────────────────────────────────────────────────────
# 🚀 INICIALIZACIÓN DE LA APP
# ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ENO Portal API V2",
    description="API para la inscripción al evento ENO del grupo religioso Onda - 13 de Diciembre, 2026",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    print("[OK] Iniciando ENO Portal API V2...")
    print(f"[DB] Base de datos: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    init_db()


# ─────────────────────────────────────────────────────────────────
# 📌 ENDPOINTS GENERALES
# ─────────────────────────────────────────────────────────────────

@app.get("/", tags=["General"])
def root():
    """Health check."""
    return {
        "message": "🎉 ENO Portal API V2 está funcionando",
        "version": "2.0.0",
        "docs": "/docs",
    }


# ─────────────────────────────────────────────────────────────────
# 📋 REGISTROS
# ─────────────────────────────────────────────────────────────────

@app.post("/api/registros", response_model=RegistroResponse, tags=["Registros"])
def crear_registro(
    registro: RegistroCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Registra un nuevo participante.
    Genera un magic_token y envía correo de confirmación en background.
    """
    telefono_limpio = clean_phone(registro.telefono)
    email_limpio = registro.email.strip().lower()

    # Verificar duplicado por teléfono
    if db.query(Registro).filter(Registro.telefono == telefono_limpio).first():
        raise HTTPException(
            status_code=409,
            detail="Ya existe una inscripción con este número de teléfono.",
        )

    # Verificar duplicado por correo
    if db.query(Registro).filter(Registro.email == email_limpio).first():
        raise HTTPException(
            status_code=409,
            detail="Ya existe una inscripción con este correo electrónico.",
        )

    # Generar magic token (expira en 72 horas)
    token = secrets.token_urlsafe(64)
    token_expires = datetime.utcnow() + timedelta(hours=72)

    nuevo_registro = Registro(
        nombre_completo=registro.nombreCompleto,
        edad=registro.edad,
        telefono=telefono_limpio,
        email=email_limpio,
        municipio=registro.municipio,
        talla_camiseta=registro.tallaCamiseta,
        no_onda=registro.noOnda,
        contacto_emergencia=registro.contactoEmergencia,
        parentesco=registro.parentesco,
        magic_token=token,
        token_expires=token_expires,
    )

    try:
        db.add(nuevo_registro)
        db.commit()
        db.refresh(nuevo_registro)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Ya existe una inscripción con estos datos.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    # Enviar correo de confirmación en background (no bloquea la respuesta)
    background_tasks.add_task(
        send_confirmation_email,
        to_email=nuevo_registro.email,
        nombre=nuevo_registro.nombre_completo,
        token=token,
    )

    logger.info(f"[REGISTRO] Nuevo participante: {nuevo_registro.nombre_completo} | ID: {nuevo_registro.id}")

    return RegistroResponse(
        success=True,
        message="¡Registro exitoso! Revisa tu correo para acceder a tu portal.",
        data={
            "id": f"ENO-{nuevo_registro.id}",
            "nombreCompleto": nuevo_registro.nombre_completo,
            "email": nuevo_registro.email,
        },
    )


@app.get("/api/registros", response_model=list[RegistroOut], tags=["Registros"])
def listar_registros(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Lista todos los registros (paginado). Solo para Admin."""
    return db.query(Registro).order_by(Registro.fecha_registro.desc()).offset(skip).limit(limit).all()


@app.get("/api/registros/buscar", response_model=RegistroResponse, tags=["Registros"])
def buscar_por_telefono(
    telefono: str = Query(..., description="Número de teléfono a buscar"),
    db: Session = Depends(get_db),
):
    """Verifica si un teléfono ya está registrado."""
    registro = db.query(Registro).filter(Registro.telefono == telefono).first()
    if registro:
        return RegistroResponse(
            success=True,
            message="Este teléfono ya está registrado.",
            data={"exists": True, "id": f"ENO-{registro.id}", "nombreCompleto": registro.nombre_completo},
        )
    return RegistroResponse(success=True, message="Teléfono no registrado.", data={"exists": False})


@app.get("/api/registros/stats", tags=["Registros"])
def estadisticas(db: Session = Depends(get_db)):
    """Estadísticas generales (para Admin dashboard)."""
    from sqlalchemy import func

    total = db.query(func.count(Registro.id)).scalar()
    promedio_edad = db.query(func.avg(Registro.edad)).scalar()
    tallas = db.query(Registro.talla_camiseta, func.count(Registro.id)).group_by(Registro.talla_camiseta).all()
    municipios = (
        db.query(Registro.municipio, func.count(Registro.id))
        .group_by(Registro.municipio)
        .order_by(func.count(Registro.id).desc())
        .limit(10)
        .all()
    )
    verificados = db.query(func.count(Registro.id)).filter(Registro.estado_pago == "verificado").scalar()

    return {
        "totalRegistros": total or 0,
        "promedioEdad": round(promedio_edad, 1) if promedio_edad else 0,
        "pagosVerificados": verificados or 0,
        "porTalla": {t.value: c for t, c in tallas},
        "topMunicipios": {m: c for m, c in municipios},
    }


@app.delete("/api/registros/{registro_id}", tags=["Registros"])
def eliminar_registro(registro_id: int, db: Session = Depends(get_db)):
    """Elimina un registro por ID."""
    registro = db.query(Registro).filter(Registro.id == registro_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado.")
    db.delete(registro)
    db.commit()
    return {"success": True, "message": f"Registro ENO-{registro_id} eliminado."}


# ─────────────────────────────────────────────────────────────────
# 🔐 AUTENTICACIÓN
# ─────────────────────────────────────────────────────────────────

@app.get("/api/auth/verify", tags=["Auth"])
def verify_magic_token(
    token: str = Query(..., description="Magic token recibido por correo"),
    db: Session = Depends(get_db),
):
    """
    Valida el magic token del enlace del correo.
    Si es válido, devuelve los datos del participante.
    """
    registro = db.query(Registro).filter(Registro.magic_token == token).first()

    if not registro:
        raise HTTPException(status_code=401, detail="Enlace inválido o ya utilizado.")

    if registro.token_expires and datetime.utcnow() > registro.token_expires:
        raise HTTPException(status_code=401, detail="Este enlace ha expirado. Contacta al administrador.")

    return {
        "success": True,
        "message": f"Bienvenido, {registro.nombre_completo}.",
        "role": "user",
        "data": {
            "id": registro.id,
            "idLabel": f"ENO-{registro.id}",
            "nombreCompleto": registro.nombre_completo,
            "edad": registro.edad,
            "telefono": registro.telefono,
            "email": registro.email,
            "municipio": registro.municipio,
            "tallaCamiseta": registro.talla_camiseta.value,
            "noOnda": registro.no_onda,
            "contactoEmergencia": registro.contacto_emergencia,
            "parentesco": registro.parentesco,
            "fechaRegistro": str(registro.fecha_registro),
            "comprobantePago": registro.comprobante_pago,
            "estadoPago": registro.estado_pago,
        },
    }


@app.post("/api/auth/admin", tags=["Auth"])
def admin_login(credentials: AdminLoginRequest, db: Session = Depends(get_db)):
    """Login manual solo para administradores."""
    if (
        credentials.email.strip().upper() == settings.ADMIN_EMAIL.strip().upper()
        and clean_phone(credentials.phone) == settings.ADMIN_PHONE
    ):
        return {
            "success": True,
            "role": "admin",
            "message": "Bienvenido, Administrador.",
            "data": {"nombreCompleto": "Administrador ENO", "isAdmin": True},
        }
    raise HTTPException(status_code=401, detail="Credenciales de administrador incorrectas.")


# ─────────────────────────────────────────────────────────────────
# 💳 PAGOS Y COMPROBANTES
# ─────────────────────────────────────────────────────────────────

@app.post("/api/registros/{registro_id}/comprobante", tags=["Pagos"])
async def subir_comprobante_endpoint(
    registro_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Sube y comprime el comprobante de pago.
    Almacena en Supabase Storage (con fallback a disco local si Storage no está configurado).
    """
    registro = db.query(Registro).filter(Registro.id == registro_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado.")

    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Solo se aceptan imágenes JPG, PNG o WebP.")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # Aumentado a 10MB (Pillow comprimirá)
        raise HTTPException(status_code=400, detail="El archivo excede el límite de 10 MB.")

    # Intentar subir a Supabase Storage (con compresión automática)
    public_url = upload_comprobante(registro_id, content)

    if public_url:
        # Guardado en Supabase Storage ✅
        registro.comprobante_pago = public_url
    else:
        # Fallback: guardar localmente si Supabase no está configurado
        import uuid
        from pathlib import Path
        from storage_service import compress_image
        uploads_dir = Path(__file__).parent / "uploads"
        uploads_dir.mkdir(exist_ok=True)
        compressed = compress_image(content)
        filename = f"comprobante_{registro_id}_{uuid.uuid4().hex[:8]}.jpg"
        with open(uploads_dir / filename, "wb") as f:
            f.write(compressed)
        registro.comprobante_pago = f"/uploads/{filename}"

    registro.estado_pago = "en revisión"
    db.commit()
    db.refresh(registro)

    return {
        "success": True,
        "message": "Comprobante subido exitosamente. Será verificado pronto.",
        "data": {
            "comprobantePago": registro.comprobante_pago,
            "estadoPago": registro.estado_pago,
        },
    }


@app.patch("/api/registros/{registro_id}/estado-pago", tags=["Pagos"])
def actualizar_estado_pago(
    registro_id: int,
    body: UpdateEstadoPago,
    db: Session = Depends(get_db),
):
    """Actualiza el estado de pago de un registro (Admin)."""
    estados_validos = ["pendiente", "en revisión", "verificado", "rechazado"]
    if body.estado_pago not in estados_validos:
        raise HTTPException(status_code=400, detail=f"Estado no válido. Opciones: {', '.join(estados_validos)}")

    registro = db.query(Registro).filter(Registro.id == registro_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado.")

    registro.estado_pago = body.estado_pago
    db.commit()
    db.refresh(registro)

    return {
        "success": True,
        "message": f"Estado de pago actualizado a '{body.estado_pago}'.",
        "data": {"id": registro.id, "estadoPago": registro.estado_pago},
    }


# ─────────────────────────────────────────────────────────────────
# ▶️ EJECUCIÓN DIRECTA
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.SERVER_HOST, port=settings.SERVER_PORT, reload=True)
