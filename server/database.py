"""
Configuración de la base de datos MySQL con SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# Crear el motor de conexión a MySQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # Verifica conexión antes de usarla
    pool_size=10,              # Máximo de conexiones en el pool
    max_overflow=20,           # Conexiones extra permitidas
    echo=False,                # Cambiar a True para ver queries SQL en consola
)

# Sesión para interactuar con la DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db():
    """
    Dependency de FastAPI que provee una sesión de base de datos.
    Se cierra automáticamente al terminar cada request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Crea todas las tablas definidas en los modelos.
    Se ejecuta al iniciar el servidor.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas de la base de datos creadas/verificadas.")
