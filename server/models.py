"""
Modelos de SQLAlchemy (tablas de MySQL) y esquemas de Pydantic (validación).
"""

from datetime import datetime
from enum import Enum as PyEnum
import re

from sqlalchemy import Column, Integer, String, DateTime, Enum
from pydantic import BaseModel, Field, field_validator, EmailStr

from database import Base


# ─────────────────────────────────────────────
# 📦 MODELO DE BASE DE DATOS (SQLAlchemy)
# ─────────────────────────────────────────────

class TallaCamiseta(str, PyEnum):
    """Tallas disponibles para la camiseta del evento."""
    XS = "xs"
    S = "s"
    M = "m"
    L = "l"
    XL = "xl"


class Registro(Base):
    """Tabla 'registros' en MySQL."""
    __tablename__ = "registros"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre_completo = Column(String(255), nullable=False)
    edad = Column(Integer, nullable=False)
    telefono = Column(String(20), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    municipio = Column(String(255), nullable=False)
    talla_camiseta = Column(Enum(TallaCamiseta), nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    comprobante_pago = Column(String(512), nullable=True, default=None)
    estado_pago = Column(String(20), nullable=False, default="pendiente")

    def __repr__(self):
        return f"<Registro(id={self.id}, nombre='{self.nombre_completo}', telefono='{self.telefono}')>"


# ─────────────────────────────────────────────
# 📋 ESQUEMAS DE VALIDACIÓN (Pydantic)
# ─────────────────────────────────────────────

class RegistroCreate(BaseModel):
    """Esquema para crear un nuevo registro (datos que llegan del frontend)."""
    nombreCompleto: str = Field(..., min_length=3, max_length=255, description="Nombre completo del participante")
    edad: int = Field(..., ge=5, le=120, description="Edad del participante")
    telefono: str = Field(..., min_length=7, max_length=20, description="Número de teléfono")
    email: str = Field(..., max_length=255, description="Correo electrónico")
    municipio: str = Field(..., min_length=2, max_length=255, description="Municipio de residencia")
    tallaCamiseta: TallaCamiseta = Field(..., description="Talla de camiseta (xs, s, m, l, xl)")

    @field_validator("nombreCompleto")
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El nombre no puede estar vacío.")
        return v

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, v: str) -> str:
        cleaned = v.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "")
        if not cleaned.isdigit():
            raise ValueError("El teléfono solo debe contener dígitos.")
        if len(cleaned) < 7 or len(cleaned) > 15:
            raise ValueError("El teléfono debe tener entre 7 y 15 dígitos.")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validar_email(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', v):
            raise ValueError("Ingresa un correo electrónico válido.")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "nombreCompleto": "Juan Pérez",
                "edad": 25,
                "telefono": "+1 809 555 1234",
                "email": "juan@ejemplo.com",
                "municipio": "Santo Domingo",
                "tallaCamiseta": "m",
            }
        }


class RegistroResponse(BaseModel):
    """Esquema de respuesta al crear un registro exitosamente."""
    success: bool
    message: str
    data: dict | None = None


class RegistroOut(BaseModel):
    """Esquema para devolver un registro individual de la base de datos."""
    id: int
    nombre_completo: str
    edad: int
    telefono: str
    email: str
    municipio: str
    talla_camiseta: str
    fecha_registro: datetime
    comprobante_pago: str | None = None
    estado_pago: str = "pendiente"

    class Config:
        from_attributes = True
