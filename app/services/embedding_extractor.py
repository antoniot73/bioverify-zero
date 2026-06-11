"""Extracción de características faciales.

El extractor incluido es de demostración y no biométrico. Reemplazar por un modelo
validado para uso real.
"""

from __future__ import annotations

import logging

import cv2
import numpy as np

from app.config import settings

logger = logging.getLogger(__name__)


def _l2_normalize(vector: np.ndarray) -> np.ndarray:
    """Normaliza un vector con norma L2."""
    norm = float(np.linalg.norm(vector))
    if norm <= 1e-12:
        return vector
    return vector / norm


class SimpleDemoEmbeddingExtractor:
    """Extractor de demostración basado en intensidad.

    Este componente permite probar el pipeline sin descargar modelos externos.
    No debe usarse como verificador biométrico real.
    """

    model_mode = "demo_non_biometric"

    def extract(self, face_bgr: np.ndarray) -> np.ndarray:
        """Extrae un vector simple normalizado desde un recorte facial."""
        gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(
            gray,
            (settings.normalized_face_size, settings.normalized_face_size),
            interpolation=cv2.INTER_AREA,
        )
        equalized = cv2.equalizeHist(resized)
        vector = equalized.astype(np.float32).reshape(-1) / 255.0
        return _l2_normalize(vector)


def create_embedding_extractor() -> SimpleDemoEmbeddingExtractor:
    """Fábrica del extractor configurado."""
    if settings.app_mode.lower() != "demo":
        logger.warning("APP_MODE no es demo, pero no hay extractor biométrico configurado.")
    return SimpleDemoEmbeddingExtractor()
