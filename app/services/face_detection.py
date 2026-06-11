"""Detección facial básica con OpenCV.

Este detector se incluye para el primer prototipo técnico. Para mejores resultados
se recomienda reemplazarlo por MediaPipe, SFace detector u otro detector moderno.

Ajuste operativo:
- En la imagen del documento puede haber falsos positivos por hologramas,
  miniaturas, sellos o fondos del documento.
- Para document_image_b64 se permite seleccionar el rostro principal por área.
- Para live_image_b64 se mantiene la restricción estricta de un solo rostro.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import cv2
import numpy as np
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FaceBox:
    """Caja delimitadora facial."""

    x: int
    y: int
    w: int
    h: int


def _load_haar_cascade() -> cv2.CascadeClassifier:
    """Carga el clasificador Haar frontal incluido en OpenCV."""
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    if detector.empty():
        raise RuntimeError("No se pudo cargar el clasificador Haar de OpenCV.")
    return detector


_DETECTOR = _load_haar_cascade()


def _detect_faces(image_bgr: np.ndarray) -> list[FaceBox]:
    """Detecta rostros candidatos y los convierte a FaceBox."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    gray = cv2.equalizeHist(gray)

    faces = _DETECTOR.detectMultiScale(
        gray,
        scaleFactor=1.08,
        minNeighbors=6,
        minSize=(48, 48),
    )

    return [
        FaceBox(x=int(x), y=int(y), w=int(w), h=int(h))
        for x, y, w, h in faces
    ]


def _face_area(face_box: FaceBox) -> int:
    """Calcula el área de la caja facial."""
    return int(face_box.w * face_box.h)


def _select_largest_face(faces: list[FaceBox]) -> FaceBox:
    """Selecciona el rostro candidato de mayor área."""
    return max(faces, key=_face_area)


def detect_single_face(
    image_bgr: np.ndarray,
    field_name: str,
    allow_largest_on_multiple: bool = False,
) -> FaceBox:
    """Detecta un rostro válido en una imagen.

    Args:
        image_bgr: Imagen en formato BGR.
        field_name: Nombre lógico del campo recibido.
        allow_largest_on_multiple: Si es True, permite seleccionar el rostro
            principal cuando hay múltiples candidatos. Este modo debe usarse
            solo para la imagen del documento, donde son frecuentes falsos
            positivos por hologramas o elementos impresos.

    Returns:
        FaceBox: Caja facial seleccionada.

    Raises:
        HTTPException: Si no hay rostro o si hay múltiples rostros y la política
        no permite seleccionar el principal.
    """
    faces = _detect_faces(image_bgr)
    count = len(faces)

    if count == 0:
        logger.info("No se detectó rostro en campo %s.", field_name)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No se detectó un rostro en {field_name}.",
        )

    if count > 1:
        if allow_largest_on_multiple:
            selected_face = _select_largest_face(faces)
            logger.info(
                "Se detectaron %s candidatos en %s. Se seleccionó el rostro principal por área.",
                count,
                field_name,
            )
            return selected_face

        logger.info("Se detectaron múltiples rostros en campo %s.", field_name)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Se detectaron múltiples rostros en {field_name}.",
        )

    return faces[0]


def crop_face(image_bgr: np.ndarray, face_box: FaceBox, margin_ratio: float = 0.20) -> np.ndarray:
    """Recorta el rostro con margen."""
    height, width = image_bgr.shape[:2]

    margin_x = int(face_box.w * margin_ratio)
    margin_y = int(face_box.h * margin_ratio)

    x1 = max(0, face_box.x - margin_x)
    y1 = max(0, face_box.y - margin_y)
    x2 = min(width, face_box.x + face_box.w + margin_x)
    y2 = min(height, face_box.y + face_box.h + margin_y)

    return image_bgr[y1:y2, x1:x2].copy()
