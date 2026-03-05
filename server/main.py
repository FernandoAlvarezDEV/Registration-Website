"""
ENO Portal - Backend API con FastAPI y MySQL
=============================================
Servidor principal que maneja las inscripciones al evento ENO.

Ejecutar con:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from config import settings
from database import get_db, init_db
from models import Registro, RegistroCreate, RegistroResponse, RegistroOut


# ─────────────────────────────────────────────
# 🚀 INICIALIZACIÓN DE LA APP
# ─────────────────────────────────────────────

app = FastAPI(
    title="ENO Portal API",
    description="API para la inscripción al evento corporativo ENO - 7 de Diciembre, 2026",
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
    # Crear el modelo de base de datos a partir de los datos del frontend
    nuevo_registro = Registro(
        nombre_completo=registro.nombreCompleto,
        edad=registro.edad,
        telefono=registro.telefono,
        email=registro.email,
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
            detail="Este número de teléfono ya está registrado para el evento.",
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
