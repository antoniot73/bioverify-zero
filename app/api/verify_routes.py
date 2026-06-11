"""Ruta principal de verificación facial 1:1."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Request

from app.config import settings
from app.schemas.verify_response import QualityReport, VerifyRequest, VerifyResponse
from app.security.upload_guards import enforce_consent, enforce_content_length
from app.services.embedding_extractor import create_embedding_extractor
from app.services.face_detection import crop_face, detect_single_face
from app.services.face_quality import validate_face_quality
from app.services.face_verifier import cosine_similarity, decide_match
from app.services.image_decoder import decode_image_matrix
from app.services.image_validation import decode_base64_image
from app.services.memory_cleanup import collect_garbage, wipe_numpy_arrays

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["verification"])


@router.post("/verify", response_model=VerifyResponse)
async def verify_identity(request: Request, payload: VerifyRequest) -> VerifyResponse:
    """Ejecuta comparación facial 1:1 sin almacenamiento deliberado."""
    enforce_content_length(request)
    enforce_consent(payload.consent_accepted)

    document_image = None
    live_image = None
    document_face = None
    live_face = None
    document_embedding = None
    live_embedding = None

    try:
        logger.info("Inicio de verificación facial 1:1.")

        document_bytes = decode_base64_image(payload.document_image_b64, "document_image_b64")
        live_bytes = decode_base64_image(payload.live_image_b64, "live_image_b64")

        document_image = decode_image_matrix(document_bytes.data, "document_image_b64")
        live_image = decode_image_matrix(live_bytes.data, "live_image_b64")

        # En documentos oficiales pueden aparecer falsos positivos por hologramas,
        # microfotografías, sellos, reflejos o patrones impresos. Para este campo se
        # selecciona el rostro principal por área si hay más de un candidato.
        document_box = detect_single_face(
            document_image,
            "document_image_b64",
            allow_largest_on_multiple=True,
        )

        # En la captura viva sí se mantiene la restricción estricta: debe aparecer
        # una sola persona frente a la cámara.
        live_box = detect_single_face(live_image, "live_image_b64")

        document_face = crop_face(document_image, document_box)
        live_face = crop_face(live_image, live_box)

        validate_face_quality(document_face, "document_image_b64")
        validate_face_quality(live_face, "live_image_b64")

        extractor = create_embedding_extractor()
        document_embedding = extractor.extract(document_face)
        live_embedding = extractor.extract(live_face)

        score = cosine_similarity(document_embedding, live_embedding)
        verified, decision = decide_match(score, settings.similarity_threshold)

        logger.info("Verificación finalizada. Decisión=%s Score=%.4f", decision, score)

        return VerifyResponse(
            verified=verified,
            similarity_score=round(score, 6),
            threshold=settings.similarity_threshold,
            decision=decision,
            quality=QualityReport(
                document_face_detected=True,
                live_face_detected=True,
                single_face_per_image=True,
                minimum_quality_passed=True,
            ),
            retention="no intentional biometric storage",
            model_mode=extractor.model_mode,
            warning=(
                "Extractor de demostración no biométrico. "
                "No usar para decisiones reales de identidad."
                if extractor.model_mode == "demo_non_biometric"
                else None
            ),
        )
    finally:
        wipe_numpy_arrays(
            [
                document_image,
                live_image,
                document_face,
                live_face,
                document_embedding,
                live_embedding,
            ]
        )
        collect_garbage()
        logger.debug("Limpieza operativa best-effort terminada.")
