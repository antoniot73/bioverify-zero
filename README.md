---
title: BioVerify Zero
emoji: 🔐
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# BioVerify-Zero v0.1.0-mvp-demo

## Arquitectura de la integración tecnológica implementada

**Autor:** Antonio Nicolás Toro González  
**Programa:** Maestría en Inteligencia Artificial para la Transformación Digital  
**Landing Page:** https://skepsis-apps.github.io/landing_page/

---

## 1. Visión general

BioVerify-Zero es una aplicación web de verificación facial 1:1, desplegada como prototipo funcional en Hugging Face Spaces mediante Docker.

El sistema compara una imagen facial tomada de un documento con un fotograma capturado desde la cámara del usuario y responde:

```text
match / no_match
```

El procesamiento se ejecuta en backend sin almacenamiento deliberado de imágenes, documentos ni vectores.

```text
Usuario
  ↓
Navegador web
  ↓
Frontend HTML/CSS/JavaScript
  ↓
API FastAPI
  ↓
OpenCV + NumPy
  ↓
Detección facial + extracción demo + similitud
  ↓
Respuesta JSON + resultado visual match / no_match
```

La versión `v0.1.0-mvp-demo` corresponde a un prototipo académico y demostrativo. No debe utilizarse para decisiones reales de identidad.

---

## 2. Arquitectura por capas

### 2.1 Capa de presentación: Frontend web

La interfaz web está construida con:

- HTML
- JavaScript nativo
- API `getUserMedia`
- Canvas
- Fetch API

Funciones principales implementadas:

1. Declaración de mayoría de edad.
2. Aceptación de consentimiento.
3. Carga de imagen del documento.
4. Activación de cámara.
5. Captura de fotograma desde video.
6. Conversión local del fotograma a Base64/JPEG.
7. Envío de ambas imágenes al backend.
8. Visualización del resultado: `match / no_match`.
9. Visualización del JSON técnico.

Flujo en frontend:

```text
document_image → FileReader → Data URL Base64

camera video → canvas.drawImage()
             → canvas.toDataURL("image/jpeg", 0.8)
             → live_image_b64
```

El frontend no guarda archivos, no genera base de datos local y no envía información adicional de identidad.

---

### 2.2 Capa de API: Backend FastAPI

El backend está implementado con:

- Python
- FastAPI
- Uvicorn
- Pydantic

Endpoint principal:

```http
POST /api/v1/verify
```

Endpoint de salud:

```http
GET /health
```

El endpoint `/health` fue validado en producción con la siguiente respuesta:

```json
{
  "status": "ok",
  "service": "bioverify-zero"
}
```

La API recibe un JSON con esta estructura lógica:

```json
{
  "adult_declaration_accepted": true,
  "consent_accepted": true,
  "document_image_b64": "data:image/...",
  "live_image_b64": "data:image/..."
}
```

Y responde con una estructura como esta:

```json
{
  "verified": true,
  "similarity_score": 0.936275,
  "threshold": 0.92,
  "decision": "match",
  "quality": {
    "document_face_detected": true,
    "live_face_detected": true,
    "single_face_per_image": true,
    "minimum_quality_passed": true
  },
  "retention": "no intentional biometric storage",
  "model_mode": "demo_non_biometric",
  "warning": "Extractor de demostración no biométrico. No usar para decisiones reales de identidad."
}
```

---

### 2.3 Capa de procesamiento visual

La capa de percepción computacional usa:

- OpenCV Headless
- NumPy

Pipeline actual implementado:

1. Recepción de imagen de documento y fotograma vivo.
2. Validación de consentimiento.
3. Validación de formato y tamaño.
4. Decodificación Base64 → bytes → NumPy → imagen OpenCV.
5. Detección facial.
6. Selección del rostro principal en documento si hay múltiples candidatos.
7. Validación estricta de rostro único en cámara.
8. Recorte o normalización de región facial.
9. Extracción de vector demostrativo no biométrico.
10. Cálculo de similitud.
11. Comparación contra umbral.
12. Generación de decisión `match / no_match`.

Lógica de decisión actual:

```python
if similarity_score >= threshold:
    decision = "match"
    verified = True
else:
    decision = "no_match"
    verified = False
```

En la prueba desplegada:

```text
similarity_score = 0.936275
threshold = 0.92
decision = match
verified = true
```

---

## 3. Arquitectura modular del proyecto

```text
bioverify-zero/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── logging_config.py
│   │
│   ├── api/
│   │   ├── verify_routes.py
│   │   └── health_routes.py
│   │
│   ├── schemas/
│   │   ├── verify_response.py
│   │   └── error_response.py
│   │
│   ├── services/
│   │   ├── image_validation.py
│   │   ├── image_decoder.py
│   │   ├── face_detection.py
│   │   ├── face_quality.py
│   │   ├── embedding_extractor.py
│   │   ├── face_verifier.py
│   │   └── memory_cleanup.py
│   │
│   ├── security/
│   │   ├── upload_guards.py
│   │   ├── cors_policy.py
│   │   └── privacy_guards.py
│   │
│   └── legal/
│       ├── privacy_notice.md
│       ├── restricted_use.md
│       └── consent_text.md
│
├── frontend/
│   ├── index.html
│   └── app.js
│
├── tests/
│
├── Dockerfile
├── requirements.txt
├── README.md
└── .env.example
```

Separación de responsabilidades:

```text
api/        → rutas HTTP
schemas/    → contratos de entrada/salida
services/   → lógica de visión computacional
security/   → controles de carga, CORS y privacidad
legal/      → textos de consentimiento y uso restringido
frontend/   → interfaz de usuario
```

---

## 4. Flujo de datos implementado

### 4.1 Flujo de usuario

```text
Usuario
  ↓
Declara mayoría de edad
  ↓
Acepta consentimiento
  ↓
Carga imagen del documento
  ↓
Activa cámara
  ↓
Captura fotograma
  ↓
Presiona Verificar
  ↓
Obtiene Resultado: match / no_match
```

### 4.2 Flujo técnico

```text
frontend/app.js
  ↓
document_image_b64 + live_image_b64
  ↓
POST /api/v1/verify
  ↓
FastAPI
  ↓
validación de consentimiento
  ↓
validación de imagen
  ↓
decodificación OpenCV
  ↓
detección facial
  ↓
extracción demo
  ↓
similitud
  ↓
respuesta JSON
  ↓
resultado visual en navegador
```

---

## 5. Integración de privacidad y uso restringido

La integración tecnológica incluye controles explícitos de privacidad:

- [x] Declaración de mayoría de edad.
- [x] Consentimiento explícito.
- [x] No uso de base de datos.
- [x] No almacenamiento deliberado de imágenes.
- [x] No almacenamiento deliberado de embeddings.
- [x] No entrenamiento con imágenes del usuario.
- [x] Respuesta limitada a score, decisión y controles de calidad.
- [x] Advertencia visible de modelo demostrativo.

La aplicación declara:

```text
retention: no intentional biometric storage
model_mode: demo_non_biometric
```

Esto ubica correctamente el sistema como prototipo académico y demostrativo, no como sistema biométrico productivo.

---

## 6. Arquitectura de despliegue

El despliegue está integrado con:

- Git
- GitHub
- Hugging Face Spaces
- Docker
- SSH

Flujo DevOps implementado:

```text
Código local
  ↓
git commit
  ↓
push a GitHub
  ↓
push a Hugging Face Space
  ↓
Docker build automático
  ↓
contenedor público
  ↓
URL .hf.space
```

Arquitectura pública de ejecución:

```text
Usuario
  ↓
Navegador
  ↓
Hugging Face Spaces (.hf.space)
  ↓
Docker container
  ↓
FastAPI + OpenCV
  ↓
Resultado match / no_match
```

La versión pública `v0.1.0-mvp-demo` no requiere Cloudflare Tunnel.

Repositorios y servicios:

```text
GitHub:
https://github.com/antoniot73/bioverify-zero

Hugging Face Space:
https://huggingface.co/spaces/antoniot73/bioverify-zero

Aplicación pública:
https://antoniot73-bioverify-zero.hf.space

Health check:
https://antoniot73-bioverify-zero.hf.space/health
```

---

## 7. Contenerización

El sistema se ejecuta en un contenedor Docker basado en Python Slim.

Componentes del contenedor:

```text
Base image: python:3.11-slim
Servidor: uvicorn
Framework API: FastAPI
Puerto expuesto: 7860
Usuario no root: appuser
Dependencias visuales: libglib2.0-0, libgl1
Procesamiento: opencv-python-headless, numpy
```

Comando de arranque:

```dockerfile
CMD ["sh", "-c", "echo 'Starting BioVerify-Zero on port 7860...' && python -m uvicorn app.main:app --host 0.0.0.0 --port 7860"]
```

El puerto `7860` se alinea con Hugging Face Spaces.

---

## 8. Arquitectura funcional resumida

```text
┌────────────────────────────────────────────┐
│              Usuario final                 │
└─────────────────────┬──────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────┐
│        Frontend Web HTML + JS              │
│ - Mayoría de edad                          │
│ - Consentimiento                           │
│ - Carga de documento                       │
│ - Cámara con getUserMedia                  │
│ - Captura con canvas                       │
└─────────────────────┬──────────────────────┘
                      │ JSON Base64 HTTPS
                      ▼
┌────────────────────────────────────────────┐
│              FastAPI Backend               │
│ - /health                                  │
│ - /api/v1/verify                           │
│ - Validación de entrada                    │
│ - Control de consentimiento                │
└─────────────────────┬──────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────┐
│      Procesamiento OpenCV + NumPy          │
│ - Decodificación                           │
│ - Detección facial                         │
│ - Selección de rostro principal            │
│ - Extracción demo no biométrica            │
│ - Similitud por umbral                     │
└─────────────────────┬──────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────┐
│              Respuesta                     │
│ - verified                                 │
│ - similarity_score                         │
│ - threshold                                │
│ - decision: match / no_match               │
│ - quality checks                           │
│ - warning demo_non_biometric               │
└────────────────────────────────────────────┘
```

---

## 9. Estado de la integración

La integración tecnológica implementada se encuentra en estado:

```text
v0.1.0-mvp-demo
```

Con validación exitosa de:

- [x] Ejecución local
- [x] Captura de cámara
- [x] Carga de documento
- [x] Comparación funcional
- [x] Resultado match
- [x] Docker build en Hugging Face
- [x] Backend público activo
- [x] Endpoint `/health` operativo
- [x] Despliegue público funcional

---

## 10. Ejecución local

Crear entorno virtual:

```bash
py -3.12 -m venv .venv
```

Activar entorno en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar servidor local:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 7860 --reload
```

Abrir en navegador:

```text
http://localhost:7860
```

---

## 11. Despliegue

Push a GitHub:

```bash
git add .
git commit -m "docs: update README for v0.1.0-mvp-demo"
git push origin main
```

Push a Hugging Face Space:

```bash
git push hf main
```

Publicar tag de versión:

```bash
git tag v0.1.0-mvp-demo
git push origin refs/tags/v0.1.0-mvp-demo
git push hf refs/tags/v0.1.0-mvp-demo
```

---

## 12. Créditos

**Autor:** Antonio Nicolás Toro González  
**Maestría:** Maestría en Inteligencia Artificial para la Transformación Digital  
**Landing Page:** https://skepsis-apps.github.io/landing_page/

---

## 13. Conclusión técnica

La arquitectura implementada integra una aplicación web ligera, un backend FastAPI, procesamiento visual con OpenCV/NumPy, controles básicos de privacidad, contenerización Docker y despliegue público en Hugging Face Spaces.

El sistema funciona como prototipo de verificación facial 1:1 con extractor demostrativo no biométrico, respuesta visual `match / no_match`, endpoint de salud operativo y flujo completo validado desde navegador hasta backend.

---

## Aviso de uso restringido

BioVerify-Zero `v0.1.0-mvp-demo` es un prototipo académico y demostrativo.

No debe utilizarse para:

- decisiones reales de identidad,
- autenticación productiva,
- procesos legales,
- verificación financiera,
- control de acceso real,
- tratamiento biométrico productivo.

El extractor actual es demostrativo y no biométrico.
