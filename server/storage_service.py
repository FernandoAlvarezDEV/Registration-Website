"""
Storage Service — ENO Portal
Sube imágenes comprimidas a Supabase Storage usando Pillow.
"""

import io
import uuid
import logging
from PIL import Image
from supabase import create_client, Client
from config import settings

logger = logging.getLogger(__name__)

_supabase: Client | None = None


def get_supabase_client() -> Client | None:
    """Retorna el cliente de Supabase Storage (singleton)."""
    global _supabase
    if _supabase is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            logger.warning("⚠️  SUPABASE_URL o SUPABASE_SERVICE_KEY no configurados.")
            return None
        _supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    return _supabase


def compress_image(image_bytes: bytes, max_width: int = 1200, quality: int = 80) -> bytes:
    """
    Comprime una imagen con Pillow:
    - Reduce a max_width píxeles de ancho manteniendo proporción.
    - Convierte a JPEG con calidad 80.
    - Retorna los bytes comprimidos.
    """
    img = Image.open(io.BytesIO(image_bytes))

    # Convertir RGBA/P a RGB (JPEG no soporta transparencia)
    if img.mode in ("RGBA", "P", "LA"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # Redimensionar si excede el ancho máximo
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    # Comprimir a JPEG
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=quality, optimize=True)
    compressed_bytes = output.getvalue()

    original_kb = len(image_bytes) / 1024
    compressed_kb = len(compressed_bytes) / 1024
    logger.info(f"🖼️  Imagen comprimida: {original_kb:.1f}KB → {compressed_kb:.1f}KB")

    return compressed_bytes


def upload_comprobante(registro_id: int, image_bytes: bytes, bucket: str = "comprobantes") -> str | None:
    """
    Comprime la imagen y la sube a Supabase Storage.
    Retorna la URL pública del archivo o None si falla.
    """
    client = get_supabase_client()
    if not client:
        return None

    try:
        # Comprimir imagen antes de subir
        compressed = compress_image(image_bytes)

        # Nombre único para evitar colisiones
        filename = f"comprobante_{registro_id}_{uuid.uuid4().hex[:8]}.jpg"
        file_path = f"{registro_id}/{filename}"

        # Subir a Supabase Storage
        client.storage.from_(bucket).upload(
            path=file_path,
            file=compressed,
            file_options={"content-type": "image/jpeg", "upsert": "true"},
        )

        # Obtener URL pública
        public_url = client.storage.from_(bucket).get_public_url(file_path)
        logger.info(f"☁️  Comprobante subido: {public_url}")
        return public_url

    except Exception as e:
        logger.error(f"☁️  Error subiendo imagen a Supabase Storage: {e}")
        return None
