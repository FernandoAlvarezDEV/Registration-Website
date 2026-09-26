"""
Configuración de la base de datos PostgreSQL con SQLAlchemy.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# Crear el motor de conexión a PostgreSQL
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
    Crea todas las tablas definidas en los modelos y asegura nuevas columnas.
    Se ejecuta al iniciar el servidor.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE registros DROP COLUMN IF EXISTS magic_token CASCADE;"))
            conn.execute(text("ALTER TABLE registros DROP COLUMN IF EXISTS token_expires CASCADE;"))
            conn.execute(text("ALTER TABLE registros ADD COLUMN IF NOT EXISTS email VARCHAR(255);"))
            conn.execute(text("ALTER TABLE registros ADD COLUMN IF NOT EXISTS opcion_comida VARCHAR(100) DEFAULT 'Comida 1';"))
            conn.commit()
    except Exception as e:
        print(f"[DB WARN] Error en migraciones: {e}")
    Base.metadata.create_all(bind=engine)
    print("[OK] Tablas de la base de datos creadas/verificadas.")
