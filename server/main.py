"""
ENO Portal - Backend API con FastAPI y MySQL
=============================================
Servidor principal que maneja las inscripciones al evento ENO.

Ejecutar con:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
import re
import os
import uuid
from pathlib import Path

from config import settings
from database import get_db, init_db
from models import Registro, RegistroCreate, RegistroResponse, RegistroOut


# ── Utilidad: Limpiar teléfono ──
def clean_phone(phone: str) -> str:
    """Elimina espacios, guiones, paréntesis, puntos y el prefijo +1."""
    cleaned = re.sub(r'[\s\-().]+', '', phone)
    if cleaned.startswith('+1'):
        cleaned = cleaned[2:]
    return cleaned


# ── Modelo de Login ──
class LoginRequest(BaseModel):
    nombreCompleto: str
    telefono: str


# ─────────────────────────────────────────────
# 🚀 INICIALIZACIÓN DE LA APP
# ─────────────────────────────────────────────

app = FastAPI(
    title="ENO Portal API",
    description="API para la inscripción al evento ENO del grupo religioso Onda - 7 de Diciembre, 2026",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI en /docs
    redoc_url="/redoc",     # ReDoc en /redoc
)

# ── CORS: Permitir peticiones desde el frontend ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Crear tablas al iniciar el servidor ──
@app.on_event("startup")
def on_startup():
    print("🟢 Iniciando ENO Portal API...")
    print(f"📡 Base de datos: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    init_db()


# ─────────────────────────────────────────────
# 📌 ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/", tags=["General"])
def root():
    """Endpoint de bienvenida / health check."""
    return {
        "message": "🎉 ENO Portal API está funcionando",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.post("/api/registros", response_model=RegistroResponse, tags=["Registros"])
def crear_registro(registro: RegistroCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo participante para el evento ENO.

    Recibe los datos del formulario del frontend y los guarda en MySQL.
    Si el teléfono ya existe, devuelve un error 409 (Conflict).
    """
    # Limpiar teléfono antes de guardar
    telefono_limpio = clean_phone(registro.telefono)

    # Verificar si ya existe un registro con ese teléfono
    existente_tel = db.query(Registro).filter(Registro.telefono == telefono_limpio).first()
    if existente_tel:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una inscripción con este número de teléfono. Si ya te inscribiste, inicia sesión para ver tu perfil.",
        )

    # Verificar si ya existe un registro con ese correo
    existente_email = db.query(Registro).filter(Registro.email == registro.email.strip().lower()).first()
    if existente_email:
        raise HTTPException(
            status_code=409,
            detail="Ya existe una inscripción con este correo electrónico. Si ya te inscribiste, inicia sesión para ver tu perfil.",
        )

    # Crear el modelo de base de datos a partir de los datos del frontend
    nuevo_registro = Registro(
        nombre_completo=registro.nombreCompleto,
        edad=registro.edad,
        telefono=telefono_limpio,
        email=registro.email.strip().lower(),
        municipio=registro.municipio,
        talla_camiseta=registro.tallaCamiseta,
    )

    try:
        db.add(nuevo_registro)
        db.commit()
        db.refresh(nuevo_registro)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ya existe una inscripción con estos datos. Si ya te inscribiste, inicia sesión para ver tu perfil.",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}",
        )

    return RegistroResponse(
        success=True,
        message="¡Registro exitoso! Te esperamos en el evento.",
        data={
            "id": f"ENO-{nuevo_registro.id}",
            "nombreCompleto": nuevo_registro.nombre_completo,
            "edad": nuevo_registro.edad,
            "telefono": nuevo_registro.telefono,
            "email": nuevo_registro.email,
            "municipio": nuevo_registro.municipio,
            "tallaCamiseta": nuevo_registro.talla_camiseta.value,
            "fechaRegistro": str(nuevo_registro.fecha_registro),
        },
    )


@app.get("/api/registros", response_model=list[RegistroOut], tags=["Registros"])
def listar_registros(
    skip: int = Query(0, ge=0, description="Registros a omitir (paginación)"),
    limit: int = Query(50, ge=1, le=200, description="Máximo de registros a devolver"),
    db: Session = Depends(get_db),
):
    """
    Lista todos los registros (con paginación).
    Útil para un panel de administración.
    """
    registros = db.query(Registro).order_by(Registro.fecha_registro.desc()).offset(skip).limit(limit).all()
    return registros


@app.get("/api/registros/buscar", response_model=RegistroResponse, tags=["Registros"])
def buscar_por_telefono(
    telefono: str = Query(..., description="Número de teléfono a buscar"),
    db: Session = Depends(get_db),
):
    """
    Busca si un teléfono ya está registrado.
    El frontend usa esto para verificar duplicados antes de enviar.
    """
    registro = db.query(Registro).filter(Registro.telefono == telefono).first()

    if registro:
        return RegistroResponse(
            success=True,
            message="Este teléfono ya está registrado.",
            data={
                "exists": True,
                "id": f"ENO-{registro.id}",
                "nombreCompleto": registro.nombre_completo,
            },
        )

    return RegistroResponse(
        success=True,
        message="Teléfono no registrado.",
        data={"exists": False},
    )


@app.get("/api/registros/stats", tags=["Registros"])
def estadisticas(db: Session = Depends(get_db)):
    """
    Devuelve estadísticas generales de los registros.
    Útil para un dashboard de administración.
    """
    from sqlalchemy import func

    total = db.query(func.count(Registro.id)).scalar()
    promedio_edad = db.query(func.avg(Registro.edad)).scalar()

    # Conteo por talla
    tallas = (
        db.query(Registro.talla_camiseta, func.count(Registro.id))
        .group_by(Registro.talla_camiseta)
        .all()
    )

    # Conteo por municipio (top 10)
    municipios = (
        db.query(Registro.municipio, func.count(Registro.id))
        .group_by(Registro.municipio)
        .order_by(func.count(Registro.id).desc())
        .limit(10)
        .all()
    )

    return {
        "totalRegistros": total or 0,
        "promedioEdad": round(promedio_edad, 1) if promedio_edad else 0,
        "porTalla": {t.value: c for t, c in tallas},
        "topMunicipios": {m: c for m, c in municipios},
    }


@app.delete("/api/registros/{registro_id}", tags=["Registros"])
def eliminar_registro(registro_id: int, db: Session = Depends(get_db)):
    """Elimina un registro por su ID."""
    registro = db.query(Registro).filter(Registro.id == registro_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado.")

    db.delete(registro)
    db.commit()
    return {"success": True, "message": f"Registro ENO-{registro_id} eliminado."}


@app.post("/api/login", tags=["Auth"])
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login con nombre completo y teléfono.
    """
    telefono_limpio = clean_phone(credentials.telefono)

    # Check admin credentials
    if credentials.nombreCompleto.strip().upper() == settings.ADMIN_EMAIL.strip().upper() and telefono_limpio == settings.ADMIN_PHONE:
        return {
            "success": True,
            "role": "admin",
            "message": "Bienvenido, Administrador.",
            "data": {
                "nombreCompleto": "Administrador ENO",
                "telefono": "8498888888",
                "isAdmin": True,
            },
        }

    # Buscar el registro por teléfono
    registro = db.query(Registro).filter(Registro.telefono == telefono_limpio).first()

    if not registro:
        raise HTTPException(
            status_code=404,
            detail="No se encontró un registro con ese número de teléfono.",
        )

    # Verificar que el nombre coincida (case-insensitive)
    if registro.nombre_completo.strip().lower() != credentials.nombreCompleto.strip().lower():
        raise HTTPException(
            status_code=401,
            detail="El nombre no coincide con el registro asociado a ese teléfono.",
        )

    return {
        "success": True,
        "role": "user",
        "message": f"Bienvenido, {registro.nombre_completo}.",
        "data": {
            "id": f"ENO-{registro.id}",
            "nombreCompleto": registro.nombre_completo,
            "edad": registro.edad,
            "telefono": registro.telefono,
            "email": registro.email,
            "municipio": registro.municipio,
            "tallaCamiseta": registro.talla_camiseta.value,
            "fechaRegistro": str(registro.fecha_registro),
            "comprobantePago": registro.comprobante_pago,
            "estadoPago": registro.estado_pago,
            "isAdmin": False,
        },
    }


@app.post("/api/registros/{registro_id}/comprobante", tags=["Pagos"])
async def subir_comprobante(
    registro_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Sube la imagen del comprobante de pago para un registro.
    Acepta imágenes JPG, PNG y WebP.
    """
    registro = db.query(Registro).filter(Registro.id == registro_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado.")

    # Validar tipo de archivo
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Formato no permitido. Solo se aceptan imágenes JPG, PNG o WebP.",
        )

    # Leer archivo y validar tamaño máximo (5 MB = 5 * 1024 * 1024 bytes)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="El archivo es demasiado grande. El máximo permitido es 5 MB.",
        )

    # Crear directorio de uploads si no existe
    uploads_dir = Path(__file__).parent / "uploads"
    uploads_dir.mkdir(exist_ok=True)

    # Generar nombre único para el archivo
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"comprobante_{registro_id}_{uuid.uuid4().hex[:8]}.{file_ext}"
    file_path = uploads_dir / filename

    # Guardar archivo
    with open(file_path, "wb") as f:
        f.write(content)

    # Actualizar registro en la base de datos
    registro.comprobante_pago = f"/uploads/{filename}"
    registro.estado_pago = "en revisión"
    db.commit()
    db.refresh(registro)

    return {
        "success": True,
        "message": "Comprobante subido exitosamente. Tu pago será verificado pronto.",
        "data": {
            "comprobantePago": registro.comprobante_pago,
            "estadoPago": registro.estado_pago,
        },
    }


class UpdateEstadoPago(BaseModel):
    estado_pago: str


@app.patch("/api/registros/{registro_id}/estado-pago", tags=["Pagos"])
def actualizar_estado_pago(
    registro_id: int,
    body: UpdateEstadoPago,
    db: Session = Depends(get_db),
):
    """Actualiza el estado de pago de un registro (Admin)."""
    estados_validos = ["pendiente", "en revisión", "verificado", "rechazado"]
    if body.estado_pago not in estados_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Estado no válido. Opciones: {', '.join(estados_validos)}",
        )

    registro = db.query(Registro).filter(Registro.id == registro_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado.")

    registro.estado_pago = body.estado_pago
    db.commit()
    db.refresh(registro)

    return {
        "success": True,
        "message": f"Estado de pago actualizado a '{body.estado_pago}'.",
        "data": {
            "id": registro.id,
            "estadoPago": registro.estado_pago,
        },
    }


# ─────────────────────────────────────────────
# 📁 ARCHIVOS ESTÁTICOS (uploads)
# ─────────────────────────────────────────────
uploads_path = Path(__file__).parent / "uploads"
uploads_path.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")


# ─────────────────────────────────────────────
# ▶️ EJECUCIÓN DIRECTA
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
    )
