"""
Configuración central del servidor ENO Portal.
Lee variables de entorno desde el archivo .env
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class Settings:
    # ── Base de Datos ──
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "6543"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "postgres")

    # ── Servidor ──
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))

    # ── Admin ──
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "ADMIN@ENO.COM")
    ADMIN_PHONE: str = os.getenv("ADMIN_PHONE", "8498888888")

    # ── CORS ──
    ALLOWED_ORIGINS: list[str] = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500"
    ).split(",")

    # ── Brevo (Envío de Correos via API HTTP) ──
    BREVO_API_KEY: str = os.getenv("BREVO_API_KEY", "")
    BREVO_FROM_EMAIL: str = os.getenv("BREVO_FROM_EMAIL", "no-reply@ondafest2026.com")

    # ── URLs ──
    # URL pública del frontend (usada en los enlaces de los correos)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5500")

    # ── Supabase Storage ──
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")

    @property
    def DATABASE_URL(self) -> str:
        import socket
        import re as _re
        
        # Obtener URL desde variable o construirla
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            db_url = (
                f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
            
        # SQLAlchemy requiere postgresql+psycopg2://
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        
        # Railway no puede conectar a Supabase via IPv6.
        # Resolvemos el hostname a IPv4 y lo sustituimos en la URL.
        host_match = _re.search(r"@([^:/]+)", db_url)
        if host_match:
            hostname = host_match.group(1)
            # Ignorar localhost o IPs ya numéricas
            if hostname != "localhost" and not _re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname):
                try:
                    ipv4 = socket.getaddrinfo(hostname, None, socket.AF_INET)[0][4][0]
                    db_url = db_url.replace(f"@{hostname}", f"@{ipv4}")
                    print(f"[DB] Resolved {hostname} -> {ipv4} (IPv4)")
                except Exception as e:
                    print(f"[DB WARN] No se pudo resolver IPv4 para {hostname}: {e}")
        
        return db_url


settings = Settings()
