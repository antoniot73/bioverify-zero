---
title: BioVerify Zero
emoji: 🧬
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# BioVerify-Zero Starter

Prototipo web de verificación facial 1:1 con minimización de datos, procesamiento efímero y uso restringido.

## Alcance

Este repositorio implementa la primera base técnica de BioVerify-Zero:

- Backend FastAPI.
- Frontend HTML/JavaScript mínimo.
- Aviso de privacidad, consentimiento y uso restringido.
- Validación estricta de imágenes en memoria mediante payload JSON Base64.
- Detección facial básica con OpenCV Haar Cascade.
- Extractor de características de demostración no biométrico para probar el flujo.
- Logs estructurados sin imágenes, documentos, embeddings ni nombres de archivo.

## Advertencia crítica

El extractor incluido por defecto es `SimpleDemoEmbeddingExtractor`. Sirve únicamente para validar el flujo técnico de extremo a extremo. No debe considerarse un modelo biométrico productivo ni usarse para decisiones reales de identidad.

Para un MVP biométrico más serio, reemplazar `SimpleDemoEmbeddingExtractor` por un extractor facial validado, por ejemplo SFace, ArcFace, MobileFaceNet u ONNX Runtime, con licencia revisada y umbral calibrado.

## Uso restringido

Queda prohibido usar este prototipo para:

- Identificación 1:N.
- Vigilancia.
- Reconocimiento facial masivo.
- Inferencia de edad, raza, salud, emociones, religión, ideología u otros atributos sensibles.
- Decisiones jurídicas, financieras, laborales, migratorias o de acceso a servicios esenciales.
- Procesamiento de imágenes de terceros sin autorización.

## Ejecución local

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload
```

Abrir:

```text
http://localhost:7860
```

## Docker

```bash
docker build -t bioverify-zero .
docker run --rm -p 7860:7860 --env-file .env.example bioverify-zero
```

## Variables principales

Ver `.env.example`.

## Criterio de privacidad

El prototipo no almacena deliberadamente imágenes, documentos, embeddings ni historial de verificaciones. Aun así, no promete destrucción criptográfica absoluta de memoria, porque el runtime de Python, el servidor ASGI, NumPy y OpenCV pueden crear copias temporales internas.
