"""Configuración central del prototipo BioVerify-Zero."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Agrupa la configuración cargada desde variables de entorno."""

    app_name: str
    app_env: str
    app_mode: str
    log_level: str
    max_image_bytes: int
    max_total_body_bytes: int
    max_image_side: int
    normalized_face_size: int
    similarity_threshold: float
    allowed_origins: list[str]
    disable_biometric_logging: bool


def _get_bool(name: str, default: bool) -> bool:
    """Convierte una variable de entorno a booleano."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_int(name: str, default: int) -> int:
    """Convierte una variable de entorno a entero con valor por defecto."""
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(f"La variable {name} debe ser entera.") from exc


def _get_float(name: str, default: float) -> float:
    """Convierte una variable de entorno a flotante con valor por defecto."""
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return float(raw_value)
    except ValueError as exc:
        raise ValueError(f"La variable {name} debe ser numérica.") from exc


def _get_allowed_origins() -> list[str]:
    """Obtiene los orígenes permitidos para CORS."""
    raw_value = os.getenv("ALLOWED_ORIGINS", "http://localhost:7860")
    origins = [origin.strip() for origin in raw_value.split(",") if origin.strip()]
    return origins


def load_settings() -> Settings:
    """Carga la configuración de ejecución del servicio."""
    return Settings(
        app_name=os.getenv("APP_NAME", "BioVerify-Zero"),
        app_env=os.getenv("APP_ENV", "development"),
        app_mode=os.getenv("APP_MODE", "demo"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        max_image_bytes=_get_int("MAX_IMAGE_BYTES", 1_572_864),
        max_total_body_bytes=_get_int("MAX_TOTAL_BODY_BYTES", 4_500_000),
        max_image_side=_get_int("MAX_IMAGE_SIDE", 1280),
        normalized_face_size=_get_int("NORMALIZED_FACE_SIZE", 112),
        similarity_threshold=_get_float("SIMILARITY_THRESHOLD", 0.92),
        allowed_origins=_get_allowed_origins(),
        disable_biometric_logging=_get_bool("DISABLE_BIOMETRIC_LOGGING", True),
    )


settings = load_settings()
