"""Controles básicos de calidad facial."""

from __future__ import annotations

import logging

import cv2
import numpy as np
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def estimate_blur_laplacian(image_bgr: np.ndarray) -> float:
    """Calcula nitidez aproximada mediante varianza del Laplaciano."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def validate_face_quality(face_bgr: np.ndarray, field_name: str, min_blur: float = 20.0) -> None:
    """Valida calidad mínima del recorte facial."""
    height, width = face_bgr.shape[:2]
    if height < 64 or width < 64:
        logger.info("Rostro demasiado pequeño en campo %s.", field_name)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"El rostro en {field_name} es demasiado pequeño.",
        )

    blur_score = estimate_blur_laplacian(face_bgr)
    if blur_score < min_blur:
        logger.info("Rostro con baja nitidez en campo %s. Score: %.2f", field_name, blur_score)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"El rostro en {field_name} no tiene nitidez suficiente.",
        )
