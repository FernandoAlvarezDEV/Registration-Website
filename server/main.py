"""
ENO Portal - Backend API V2 (Hardened)
======================================
FastAPI + PostgreSQL (Supabase) con:
  - Magic Link authentication (sin contraseñas)
  - Envío de correo automático (Resend API)
  - Compresión y almacenamiento de imágenes (Supabase Storage)
  - Security headers, rate limiting, admin auth

Ejecutar con:
    uvicorn main:app --host 0.0.0.0 --port 8000
"""

import secrets
import re
import logging
import hashlib
import hmac
import unicodedata
from pathlib import Path
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import settings
from database import get_db, init_db
from models import Registro, RegistroCreate, RegistroResponse, RegistroOut
from storage_service import upload_comprobante

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# 🔒 SECURITY: Rate Limiter (Vulnerabilidad #6)
# ─────────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


# ─────────────────────────────────────────────────────────────────
# 🔒 SECURITY: Headers de Seguridad Middleware (Vulnerabilidad #2.2)
# ─────────────────────────────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Agrega headers de seguridad HTTP a todas las respuestas."""
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        return response


# ── Utilidad: Limpiar teléfono y normalizar texto ───────────────
def clean_phone(phone: str) -> str:
    """Elimina espacios, guiones, paréntesis, puntos y el prefijo +1."""
    if not phone:
        return ""
    cleaned = re.sub(r'[\s\-().]+', '', phone)
    if cleaned.startswith('+1'):
        cleaned = cleaned[2:]
    return cleaned


def normalize_str(s: str) -> str:
    """Elimina acentos, espacios extras y convierte a minúsculas para comparaciones insensibles."""
    if not s:
        return ""
    normalized = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('utf-8')
    return re.sub(r'\s+', ' ', normalized).strip().lower()


def generar_codigo_registro(db_id: int) -> str:
    """
    Asigna un código de registro secuencial:
    ENO-A001 a ENO-A100 para los primeros 100
    ENO-B001 a ENO-B100 para los siguientes 100
    ...
    Hasta ENO-Z100 (26 letras * 100 = 2600 máximo)
    """
    try:
        raw_id = int(str(db_id).replace("ENO-", "").replace("ONDA-", ""))
    except Exception:
        raw_id = 1
    idx = max(0, raw_id - 1)
    letra_idx = min(25, idx // 100)
    letra = chr(ord('A') + letra_idx)
    num = (idx % 100) + 1
    return f"ENO-{letra}{num:03d}"



# ─────────────────────────────────────────────────────────────────
# 🔒 SECURITY: Admin Token Authentication (Vulnerabilidad #2)
# ─────────────────────────────────────────────────────────────────
_ADMIN_SECRET = secrets.token_urlsafe(48)  # Generado al iniciar el servidor

def _generate_admin_token() -> str:
    """
    Genera un token de sesión admin firmado con HMAC.
    El token contiene un timestamp y una firma para verificar autenticidad.
    """
    timestamp = str(int(datetime.utcnow().timestamp()))
    signature = hmac.new(
        _ADMIN_SECRET.encode(),
        timestamp.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{timestamp}.{signature}"


def _verify_admin_token(token: str) -> bool:
    """Verifica que un token admin sea válido y no haya expirado (8 horas)."""
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return False
        timestamp_str, signature = parts
        # Verificar firma HMAC
        expected_sig = hmac.new(
            _ADMIN_SECRET.encode(),
            timestamp_str.encode(),
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return False
        # Verificar expiración (8 horas)
        token_time = datetime.utcfromtimestamp(int(timestamp_str))
        if datetime.utcnow() - token_time > timedelta(hours=8):
            return False
        return True
    except (ValueError, TypeError):
        return False


def require_admin(request: Request):
    """
    Dependency de FastAPI que verifica autenticación de admin.
    Espera el header: Authorization: Bearer <admin_token>
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Acceso no autorizado. Se requiere autenticación de administrador.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header.replace("Bearer ", "")
    if not _verify_admin_token(token):
        raise HTTPException(
            status_code=401,
            detail="Token de administrador inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True


# ── Modelos de Request/Response ─────────────────────────────────
class AdminLoginRequest(BaseModel):
    email: str
    phone: str

class VerificarRegistroRequest(BaseModel):
    nombre: str
    telefono: str
    distrito: str = ""
    email: str = ""

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

# Registrar rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 🔒 SECURITY: Middleware de headers de seguridad
app.add_middleware(SecurityHeadersMiddleware)

# 🔒 SECURITY: CORS configurado con allow_origins y regex para subdominios legítimos
cleaned_origins = [o.strip() for o in settings.ALLOWED_ORIGINS if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cleaned_origins,
    allow_origin_regex=r"https?://(([a-zA-Z0-9-]+\.)*(onrender\.com|railway\.app|vercel\.app|github\.io|ondafest\.com|localhost)|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Servir archivos estáticos de comprobantes subidos
uploads_dir = Path(__file__).parent / "uploads"
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.on_event("startup")
def on_startup():
    # 🔒 SECURITY: No loguear detalles de conexión en producción (Vulnerabilidad #5)
    logger.info("[OK] Iniciando ENO Portal API V2...")
    logger.info(f"[DB] Conectando a base de datos en puerto {settings.DB_PORT}")
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
    }


# ─────────────────────────────────────────────────────────────────
# 📋 REGISTROS
# ─────────────────────────────────────────────────────────────────

@app.post("/api/registros", response_model=RegistroResponse, tags=["Registros"])
@limiter.limit("5/minute")  # 🔒 SECURITY: Rate limit en registros (Vulnerabilidad #6)
def crear_registro(
    request: Request,
    registro: RegistroCreate,
    db: Session = Depends(get_db),
):
    """
    Registra un nuevo participante.
    Limitado a 5 registros por minuto por IP.
    """
    telefono_limpio = clean_phone(registro.telefono)

    # Verificar duplicado por teléfono
    if db.query(Registro).filter(Registro.telefono == telefono_limpio).first():
        raise HTTPException(
            status_code=409,
            detail="Ya existe una inscripción con este número de teléfono.",
        )

    comida_elegida = (registro.opcionComida or "Comida 1").strip()

    nuevo_registro = Registro(
        nombre_completo=registro.nombreCompleto,
        edad=registro.edad,
        telefono=telefono_limpio,
        email=registro.email.strip().lower() if registro.email else None,
        municipio=registro.municipio,
        talla_camiseta=registro.tallaCamiseta,
        no_onda=registro.noOnda,
        contacto_emergencia=registro.contactoEmergencia,
        parentesco=registro.parentesco,
        opcion_comida=comida_elegida,
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
        logger.error(f"[REGISTRO] Error interno al crear registro: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Error interno del servidor.")

    # Asignar código secuencial ENO-A001 a ENO-Z100 (0 correos, 0 magic links)
    codigo = generar_codigo_registro(nuevo_registro.id)
    logger.info(f"[REGISTRO] Nuevo participante registrado | ID: {nuevo_registro.id} -> Código: {codigo}")

    return RegistroResponse(
        success=True,
        message="¡Registro exitoso! Guarda tu código de registro y realiza tu transferencia bancaria.",
        data={
            "id": codigo,
            "codigoRegistro": codigo,
            "numericId": nuevo_registro.id,
            "nombreCompleto": nuevo_registro.nombre_completo,
            "telefono": nuevo_registro.telefono,
            "email": nuevo_registro.email,
            "municipio": nuevo_registro.municipio,
            "opcionComida": nuevo_registro.opcion_comida,
        },
    )


# 🔒 SECURITY: Endpoint protegido con autenticación admin (Vulnerabilidad #2)
@app.get("/api/registros", response_model=list[RegistroOut], tags=["Registros"])
def listar_registros(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _admin: bool = Depends(require_admin),
):
    """Lista todos los registros (paginado). Solo para Admin autenticado."""
    return db.query(Registro).order_by(Registro.fecha_registro.desc()).offset(skip).limit(limit).all()


@app.get("/api/registros/buscar", response_model=RegistroResponse, tags=["Registros"])
@limiter.limit("10/minute")  # 🔒 Rate limit en búsquedas
def buscar_por_telefono(
    request: Request,
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



# 🔒 SECURITY: Endpoint protegido con autenticación admin (Vulnerabilidad #2)
@app.get("/api/registros/stats", tags=["Registros"])
def estadisticas(
    request: Request,
    db: Session = Depends(get_db),
    _admin: bool = Depends(require_admin),
):
    """Estadísticas generales (para Admin dashboard). Solo Admin autenticado."""
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


# 🔒 SECURITY: Endpoint protegido con autenticación admin (Vulnerabilidad #2)
@app.delete("/api/registros/{registro_id}", tags=["Registros"])
def eliminar_registro(
    request: Request,
    registro_id: int,
    db: Session = Depends(get_db),
    _admin: bool = Depends(require_admin),
):
    """Elimina un registro por ID. Solo Admin autenticado."""
    registro = db.query(Registro).filter(Registro.id == registro_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado.")
    db.delete(registro)
    db.commit()
    logger.info(f"[ADMIN] Registro ENO-{registro_id} eliminado por administrador.")
    return {"success": True, "message": f"Registro ENO-{registro_id} eliminado."}


# ─────────────────────────────────────────────────────────────────
# 🔐 AUTENTICACIÓN Y VERIFICACIÓN DE ASISTENTES
# ─────────────────────────────────────────────────────────────────


@app.post("/api/registros/verificar", tags=["Auth"])
@limiter.limit("15/minute")
def verificar_registro(
    request: Request,
    body: VerificarRegistroRequest,
    db: Session = Depends(get_db),
):
    """
    Verifica el registro de un asistente mediante Nombre, Teléfono y Distrito/Municipio.
    Devuelve los datos del participante para mostrar su panel y permitir subir el comprobante.
    """
    nombre_input = normalize_str(body.nombre)
    phone_clean = clean_phone(body.telefono)
    distrito_input = normalize_str(body.distrito)

    if not phone_clean or len(phone_clean) < 7:
        raise HTTPException(status_code=400, detail="Por favor ingresa un número de teléfono válido.")
    if not nombre_input or len(nombre_input) < 2:
        raise HTTPException(status_code=400, detail="Por favor ingresa tu nombre completo.")

    registros = db.query(Registro).all()

    # 1. Filtrar por teléfono (últimos 7 a 10 dígitos)
    target_digits = phone_clean[-10:] if len(phone_clean) >= 10 else phone_clean[-7:]
    phone_matches = []
    for r in registros:
        r_phone = clean_phone(r.telefono or "")
        if r_phone and (r_phone.endswith(target_digits) or phone_clean.endswith(r_phone[-7:] if len(r_phone) >= 7 else r_phone)):
            phone_matches.append(r)

    if not phone_matches:
        raise HTTPException(status_code=404, detail="No se encontró ninguna inscripción con este número de teléfono.")

    # 2. Filtrar por nombre
    name_matches = []
    input_words = set(nombre_input.split())
    for r in phone_matches:
        r_name = normalize_str(r.nombre_completo or "")
        r_words = set(r_name.split())
        if nombre_input in r_name or r_name in nombre_input or bool(input_words.intersection(r_words)):
            name_matches.append(r)

    if not name_matches:
        raise HTTPException(status_code=404, detail="El nombre ingresado no coincide con el registrado para este número telefónico.")

    # 3. Filtrar por distrito/municipio si se suministró
    final_match = None
    if distrito_input:
        for r in name_matches:
            r_dist = normalize_str(r.municipio or "")
            if (
                distrito_input in r_dist
                or r_dist in distrito_input
                or distrito_input == "otro"
                or (distrito_input == "san francisco" and "francisco" in r_dist)
                or (distrito_input == "higuey" and "higuey" in r_dist)
            ):
                final_match = r
                break
        if not final_match:
            raise HTTPException(status_code=400, detail="El distrito/municipio seleccionado no coincide con los datos de tu registro.")
    else:
        final_match = name_matches[0]

    registro = final_match

    # 4. Validar correo electrónico obligatorio para acceder al panel
    email_input = normalize_str(body.email)
    if not email_input:
        raise HTTPException(status_code=400, detail="Por favor ingresa tu correo electrónico registrado para acceder al panel.")

    if registro.email and normalize_str(registro.email) != email_input:
        raise HTTPException(
            status_code=400,
            detail="El correo electrónico ingresado no coincide con el registrado para esta inscripción."
        )

    talla_val = registro.talla_camiseta.value if hasattr(registro.talla_camiseta, 'value') else str(registro.talla_camiseta or "")
    codigo = generar_codigo_registro(registro.id)

    return {
        "success": True,
        "message": f"Registro encontrado para {registro.nombre_completo}.",
        "data": {
            "id": registro.id,
            "idLabel": codigo,
            "codigoRegistro": codigo,
            "nombreCompleto": registro.nombre_completo,
            "edad": registro.edad,
            "telefono": registro.telefono,
            "email": registro.email,
            "municipio": registro.municipio,
            "tallaCamiseta": talla_val,
            "noOnda": registro.no_onda,
            "contactoEmergencia": registro.contacto_emergencia,
            "parentesco": registro.parentesco,
            "fechaRegistro": str(registro.fecha_registro) if registro.fecha_registro else None,
            "comprobantePago": registro.comprobante_pago,
            "estadoPago": registro.estado_pago,
            "opcionComida": getattr(registro, "opcion_comida", "Comida 1") or "Comida 1",
        },
    }



@app.post("/api/auth/admin", tags=["Auth"])
@limiter.limit("5/minute")  # 🔒 Rate limit estricto en login admin (Vulnerabilidad #6)
def admin_login(
    request: Request,
    credentials: AdminLoginRequest,
    db: Session = Depends(get_db),
):
    """
    Login manual solo para administradores.
    Devuelve un token de sesión admin firmado con HMAC.
    """
    if (
        credentials.email.strip().upper() == settings.ADMIN_EMAIL.strip().upper()
        and clean_phone(credentials.phone) == settings.ADMIN_PHONE
    ):
        admin_token = _generate_admin_token()
        logger.info("[AUTH] Inicio de sesión de administrador exitoso.")
        return {
            "success": True,
            "role": "admin",
            "message": "Bienvenido, Administrador.",
            "token": admin_token,  # Token para usar en endpoints protegidos
            "data": {"nombreCompleto": "Administrador ENO", "isAdmin": True},
        }
    # 🔒 SECURITY: Loguear intentos fallidos sin exponer credenciales
    logger.warning(f"[AUTH] Intento de login admin fallido desde IP: {request.client.host}")
    raise HTTPException(status_code=401, detail="Credenciales de administrador incorrectas.")


# ─────────────────────────────────────────────────────────────────
# 💳 PAGOS Y COMPROBANTES
# ─────────────────────────────────────────────────────────────────

@app.post("/api/registros/{registro_id}/comprobante", tags=["Pagos"])
@limiter.limit("3/minute")  # 🔒 Rate limit en subida de archivos
async def subir_comprobante_endpoint(
    request: Request,
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


# 🔒 SECURITY: Endpoint protegido con autenticación admin (Vulnerabilidad #2)
@app.patch("/api/registros/{registro_id}/estado-pago", tags=["Pagos"])
def actualizar_estado_pago(
    request: Request,
    registro_id: int,
    body: UpdateEstadoPago,
    db: Session = Depends(get_db),
    _admin: bool = Depends(require_admin),
):
    """Actualiza el estado de pago de un registro. Solo Admin autenticado."""
    estados_validos = ["pendiente", "en revisión", "verificado", "rechazado"]
    if body.estado_pago not in estados_validos:
        raise HTTPException(status_code=400, detail=f"Estado no válido. Opciones: {', '.join(estados_validos)}")

    registro = db.query(Registro).filter(Registro.id == registro_id).first()
    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado.")

    registro.estado_pago = body.estado_pago
    db.commit()
    db.refresh(registro)

    logger.info(f"[ADMIN] Estado de pago de ENO-{registro_id} actualizado a '{body.estado_pago}'.")

    return {
        "success": True,
        "message": f"Estado de pago actualizado a '{body.estado_pago}'.",
        "data": {"id": registro.id, "estadoPago": registro.estado_pago},
    }


# ─────────────────────────────────────────────────────────────────
# 🔒 SECURITY: Endpoint /api/test-email ELIMINADO (Vulnerabilidad #1)
# Anteriormente exponía credenciales SMTP y permitía envío arbitrario.
# ─────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────
# ▶️ EJECUCIÓN DIRECTA
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.SERVER_HOST, port=settings.SERVER_PORT, reload=True)
