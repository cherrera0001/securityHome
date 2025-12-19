# 🔍 ForensicVideo AI Platform
## Sistema SaaS de Análisis Forense de Video con IA

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue.svg)](https://kubernetes.io/)

Plataforma empresarial de análisis forense de video con capacidad de procesamiento distribuido, reconocimiento facial avanzado, detección de objetos con IA, y cadena de custodia digital certificada.

---

## 📋 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Stack Tecnológico](#-stack-tecnológico)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación Rápida](#-instalación-rápida)
- [Configuración](#-configuración)
- [Pipeline Forense](#-pipeline-forense)
- [Roles y Permisos (RBAC)](#-roles-y-permisos-rbac)
- [Escalado con Kubernetes](#-escalado-con-kubernetes)
- [API Endpoints](#-api-endpoints)
- [Módulos de IA](#-módulos-de-ia)
- [Seguridad](#-seguridad)
- [Monitoreo](#-monitoreo)
- [Mejores Prácticas](#-mejores-prácticas)

---

## 🚀 Características Principales

### Pipeline Forense Completo
- ✅ **Cadena de Custodia Digital**: Registro automático de cada operación con hashes SHA-256/512
- ✅ **Extracción de Metadatos EXIF**: Fecha/hora original, dispositivo, ubicación GPS
- ✅ **Certificados Criptográficos**: Generación de certificados de integridad forense

### Análisis de IA Avanzado
- 🔍 **Detección de Objetos (YOLOv10)**: Personas, vehículos, armas, objetos de interés
- 👤 **Reconocimiento Facial (DeepFace)**: Embeddings de 512 dimensiones para búsqueda biométrica
- 🎯 **Búsqueda de Similitud (pgvector)**: Encuentra al mismo sujeto en diferentes videos
- 🖼️ **Super-Resolution (Real-ESRGAN)**: Mejora rostros pixelados a 4K
- 📊 **Heatmaps de Movimiento**: Visualización de zonas de actividad

### Procesamiento Distribuido
- ⚡ **Celery + Redis**: Procesamiento asíncrono sin bloquear la UI
- 📈 **Escalado Horizontal**: Kubernetes HPA para procesar miles de cámaras
- 🔄 **Colas Priorizadas**: Diferentes queues para distintos tipos de análisis
- 💾 **Almacenamiento Cloud**: AWS S3 / Google Cloud Storage

### Dashboard Interactivo
- 📹 **Upload Drag & Drop**: Subida de videos con progress bar
- 🖼️ **Galería de Rostros**: Grid interactivo con búsqueda de similares
- 🗺️ **Visualización de Heatmaps**: Canvas HTML5 con zonas de calor
- 📊 **Reportes Periciales**: Generación automática de informes PDF

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js 14)                    │
│  Dashboard | Video Upload | Face Gallery | Heatmaps | Reports   │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTPS/REST API
┌─────────────────────────▼───────────────────────────────────────┐
│                    API GATEWAY (FastAPI)                         │
│  Authentication | Video Upload | Face Search | Reports          │
└─────┬────────────────────────────────────────┬──────────────────┘
      │                                        │
      │ PostgreSQL + pgvector                 │ Celery Tasks
      ▼                                        ▼
┌─────────────────────┐          ┌──────────────────────────────┐
│   DATABASE          │          │   WORKERS (Celery + Redis)   │
│  ┌───────────────┐  │          │  ┌─────────────────────────┐ │
│  │ Users         │  │          │  │ Video Processing        │ │
│  │ Videos        │  │          │  │  ├─ Frame Extraction   │ │
│  │ FaceEmbedding │  │◄─────────┼──┤  ├─ YOLO Detection     │ │
│  │ (Vector 512)  │  │          │  │  ├─ DeepFace Analysis  │ │
│  │ ChainOfCustody│  │          │  │  └─ Super-Resolution   │ │
│  │ Alerts        │  │          │  └─────────────────────────┘ │
│  └───────────────┘  │          └──────────────────────────────┘
└─────────────────────┘                        │
                                               │ S3/GCS
                                               ▼
                                    ┌────────────────────┐
                                    │  CLOUD STORAGE     │
                                    │  Videos | Faces    │
                                    │  Thumbnails        │
                                    └────────────────────┘
```

### Flujo de Procesamiento

1. **Upload**: Usuario sube video → API calcula hashes → Guarda en S3 → Crea registro en DB
2. **Processing**: Celery worker descarga video → Extrae frames → Ejecuta YOLO + DeepFace
3. **Storage**: Caras detectadas → Generan embeddings 512D → Almacena en pgvector
4. **Search**: Usuario busca cara → Query con pgvector → Retorna matches similares
5. **Enhancement**: Caras de bajo res → Real-ESRGAN → Mejora a 4K → Guarda en S3
6. **Report**: Investigador genera reporte → Compila datos → Genera PDF → Firma digital

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Propósito |
|-----------|-----------|-----------|
| **Frontend** | Next.js 14 + Tailwind CSS | UI reactiva con Server Components |
| **Backend** | FastAPI (Python 3.11) | API REST de alto rendimiento |
| **Workers** | Celery + Redis | Procesamiento asíncrono distribuido |
| **Database** | PostgreSQL 16 + pgvector | Base de datos con búsqueda vectorial |
| **AI - Detection** | YOLOv10 (Ultralytics) | Detección de objetos en tiempo real |
| **AI - Faces** | DeepFace (Facenet512) | Embeddings faciales de 512 dims |
| **AI - Enhancement** | Real-ESRGAN | Super-resolution de imágenes |
| **Storage** | AWS S3 / GCS | Almacenamiento de archivos |
| **Auth** | OAuth2 + JWT | Autenticación y autorización |
| **Container** | Docker + Docker Compose | Contenerización |
| **Orchestration** | Kubernetes + HPA | Orquestación y escalado |
| **Monitoring** | Prometheus + Grafana | Métricas y visualización |

---

## ✅ Requisitos Previos

### Para Docker Compose (Desarrollo)
- Docker 20.10+
- Docker Compose 2.0+
- 16GB RAM mínimo (recomendado 32GB)
- GPU NVIDIA con CUDA 11.8+ (opcional pero recomendado)

### Para Kubernetes (Producción)
- Kubernetes 1.28+
- Helm 3.0+
- kubectl configurado
- Cluster con GPU nodes (para workers de IA)
- Persistent Volume provisioner
- Ingress Controller

### Cuentas Cloud (Opcional)
- AWS Account con S3 habilitado
- O Google Cloud Account con Cloud Storage

---

## 🚀 Instalación Rápida

### 1. Clonar Repositorio

```bash
git clone https://github.com/cherrera0001/securityHome.git
cd securityHome
```

### 2. Configurar Variables de Entorno

```bash
cp backend/.env.example backend/.env
# Editar backend/.env con tus credenciales
```

### 3. Descargar Modelos de IA

```bash
# Crear directorio de modelos
mkdir -p backend/models

# YOLOv10
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov10n.pt -O backend/models/yolov10n.pt

# Real-ESRGAN (opcional)
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth -O backend/models/RealESRGAN_x4plus.pth
```

### 4. Levantar con Docker Compose

```bash
docker-compose up -d

# Ver logs
docker-compose logs -f

# Verificar servicios
docker-compose ps
```

### 5. Inicializar Base de Datos

```bash
# Ejecutar migraciones
docker-compose exec api python -c "from app.models.database import init_db; init_db()"

# Crear usuario admin
docker-compose exec api python scripts/create_admin.py
```

### 6. Acceder a la Plataforma

- 🌐 **Frontend**: http://localhost:3000
- 🔧 **API Docs**: http://localhost:8000/docs
- 🌸 **Flower (Celery)**: http://localhost:5555
- 📊 **pgAdmin**: http://localhost:5050 (si está habilitado)

---

## ⚙️ Configuración

### Variables de Entorno Críticas

```bash
# backend/.env

# Database
DATABASE_URL=postgresql://forensic:STRONG_PASSWORD@postgres:5432/forensic_db

# Seguridad - CAMBIAR EN PRODUCCIÓN
SECRET_KEY=tu-clave-secreta-muy-larga-y-compleja-2024

# AWS S3
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
S3_BUCKET_NAME=forensic-prod-videos

# Modelos de IA
YOLO_MODEL_PATH=./models/yolov10n.pt
DEEPFACE_MODEL=Facenet512
ESRGAN_MODEL_PATH=./models/RealESRGAN_x4plus.pth

# Procesamiento
FRAME_EXTRACTION_FPS=1
FACE_DETECTION_CONFIDENCE=0.7
FACE_MATCH_THRESHOLD=0.6
```

---

## 🔬 Pipeline Forense

### 1. Integridad y Cadena de Custodia

```python
# Cada video genera:
- SHA-256 Hash: Identificación única
- SHA-512 Hash: Verificación adicional
- EXIF Metadata: Fecha/hora original, dispositivo
- Cadena de custodia: Cada operación registrada
```

### 2. Procesamiento con IA

```python
# Pipeline automático:
1. Extracción de frames (1 fps)
2. Detección de objetos (YOLO)
   - Personas, vehículos, armas
3. Detección facial (DeepFace)
   - Ubicación, confianza
4. Generación de embeddings (512D)
5. Análisis de atributos
   - Edad, género, emoción
6. Super-resolution (4K)
7. Almacenamiento en S3
```

### 3. Búsqueda Biométrica

```sql
-- Query de similitud facial con pgvector
SELECT 
  fe.id, 
  fe.video_id,
  (fe.embedding <=> query_embedding) as distance
FROM face_embeddings fe
WHERE (fe.embedding <=> query_embedding) < 0.6
ORDER BY distance
LIMIT 10;
```

---

## 👥 Roles y Permisos (RBAC)

| Rol | Permisos | Casos de Uso |
|-----|----------|--------------|
| **Admin** | - Gestión completa del sistema<br>- Ver todas las organizaciones<br>- Gestión de usuarios<br>- Configuración de infraestructura | Administrador de la plataforma |
| **Investigator** | - Procesar videos<br>- Marcar personas de interés<br>- Generar reportes periciales<br>- Ver cadena de custodia<br>- Búsqueda facial avanzada | Analista forense, investigador criminal |
| **Client** | - Subir videos<br>- Ver sus propios videos<br>- Recibir alertas<br>- Descargar reportes | Usuario final, cliente del servicio |

---

## ☸️ Escalado con Kubernetes

### Despliegue en Kubernetes

```bash
# 1. Crear namespace
kubectl create namespace forensic-prod

# 2. Crear secrets
kubectl apply -f infrastructure/k8s/secrets.yaml -n forensic-prod

# 3. Desplegar base de datos
kubectl apply -f infrastructure/k8s/postgres-deployment.yaml -n forensic-prod
kubectl apply -f infrastructure/k8s/redis-deployment.yaml -n forensic-prod

# 4. Desplegar API
kubectl apply -f infrastructure/k8s/api-deployment.yaml -n forensic-prod

# 5. Desplegar Workers
kubectl apply -f infrastructure/k8s/celery-deployment.yaml -n forensic-prod

# 6. Verificar deployments
kubectl get pods -n forensic-prod
kubectl get svc -n forensic-prod
```

### Escalado Horizontal Automático

El sistema incluye **Horizontal Pod Autoscalers (HPA)** para escalar automáticamente según demanda:

#### API Scaling
```yaml
# De 3 a 10 réplicas según CPU/Memoria
minReplicas: 3
maxReplicas: 10
metrics:
  - CPU: 70%
  - Memory: 80%
```

#### Workers Scaling
```yaml
# De 5 a 50 workers para procesar miles de videos
minReplicas: 5
maxReplicas: 50
metrics:
  - CPU: 80%
  - Memory: 85%
```

### Procesamiento de Miles de Cámaras

Para escalar a **miles de cámaras en tiempo real**:

1. **Workers con GPU**: Cada worker con NVIDIA GPU procesa ~10 cámaras simultáneamente
2. **Pool de Workers**: 50 workers × 10 cámaras = **500 cámaras** procesadas en paralelo
3. **Escalado Vertical**: Usar instancias con múltiples GPUs (p3.8xlarge en AWS)
4. **Escalado Horizontal**: HPA agrega workers automáticamente bajo alta carga

```bash
# Ejemplo: Escalar manualmente a 30 workers
kubectl scale deployment celery-worker --replicas=30 -n forensic-prod

# Ver uso de recursos
kubectl top pods -n forensic-prod
```

### Arquitectura de Alta Disponibilidad

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOAD BALANCER (AWS ALB/NLB)                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
   │ API Pod │         │ API Pod │        │ API Pod │
   │ Replica │         │ Replica │        │ Replica │
   │   #1    │         │   #2    │        │   #3    │
   └─────────┘         └─────────┘        └─────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼────────────────────────┐
        │                   │                        │
   ┌────▼────┐         ┌────▼────┐    ...     ┌─────▼───┐
   │ Worker  │         │ Worker  │            │ Worker  │
   │ GPU #1  │         │ GPU #2  │            │ GPU #50 │
   └─────────┘         └─────────┘            └─────────┘
        │                   │                        │
        └───────────────────┼────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │  Redis Cluster │
                    │  (HA Mode)     │
                    └────────────────┘
```

---

## 📡 API Endpoints

### Autenticación

```http
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### Videos

```http
POST   /api/v1/videos/upload
GET    /api/v1/videos
GET    /api/v1/videos/{video_id}
GET    /api/v1/videos/{video_id}/status
GET    /api/v1/videos/{video_id}/faces
GET    /api/v1/videos/{video_id}/chain-of-custody  # Investigadores
```

### Búsqueda Facial

```http
POST   /api/v1/faces/search
POST   /api/v1/faces/mark-poi  # Investigadores
```

### Alertas

```http
GET    /api/v1/alerts
PATCH  /api/v1/alerts/{alert_id}/read
```

### Reportes

```http
POST   /api/v1/reports/generate  # Investigadores
GET    /api/v1/reports/{report_id}
```

### Admin

```http
GET    /api/v1/admin/users
GET    /api/v1/admin/stats
```

---

## 🤖 Módulos de IA

### 1. YOLOv10 - Detección de Objetos

```python
from app.forensics.ai_inference import AIInferenceModule

ai = AIInferenceModule(yolo_model_path="./models/yolov10n.pt")
detections = ai.detect_objects(frame, confidence_threshold=0.5)

# Output:
[
  {
    "class": "person",
    "confidence": 0.92,
    "bbox": {"x": 100, "y": 150, "width": 80, "height": 200}
  },
  {
    "class": "gun",
    "confidence": 0.87,
    "bbox": {"x": 200, "y": 180, "width": 40, "height": 30}
  }
]
```

### 2. DeepFace - Reconocimiento Facial

```python
# Generar embedding de 512 dimensiones
embedding = ai.generate_face_embedding(face_image)
# embedding.shape = (512,)

# Analizar atributos
attributes = ai.analyze_face_attributes(face_image)
# {
#   "age": 34,
#   "gender": "Man",
#   "emotion": "neutral",
#   "race": "latino hispanic"
# }
```

### 3. Real-ESRGAN - Super-Resolution

```python
from app.forensics.super_resolution import SuperResolutionModule

sr = SuperResolutionModule(model_path="./models/RealESRGAN_x4plus.pth")
enhanced_face = sr.enhance_face(pixelated_face, target_resolution="4k")

# Compara calidad
metrics = sr.compare_quality(original, enhanced)
# {
#   "psnr": 28.5,
#   "ssim": 0.92,
#   "improvement_ratio": 3.4
# }
```

---

## 🔒 Seguridad

### Autenticación JWT

```python
# Token con expiración de 7 días
access_token = AuthService.create_access_token(
    data={"sub": user_id, "role": user.role},
    expires_delta=timedelta(days=7)
)
```

### Protección de Endpoints

```python
# Solo usuarios autenticados
@app.get("/protected")
async def protected_route(user: User = Depends(get_current_user)):
    pass

# Solo investigadores
@app.post("/sensitive")
async def sensitive_route(user: User = Depends(require_investigator)):
    pass
```

### Cadena de Custodia

Cada operación genera un registro inmutable:

```json
{
  "action": "processed",
  "actor": "AI System",
  "timestamp": "2024-01-15T10:30:00Z",
  "hash_before": "abc123...",
  "hash_after": "abc123...",
  "ip_address": "192.168.1.10"
}
```

---

## 📊 Monitoreo

### Celery Flower

Monitoreo en tiempo real de workers:
- http://localhost:5555
- Tasks activas/completadas/fallidas
- Throughput de procesamiento
- Estado de queues

### Prometheus + Grafana

```yaml
# Métricas expuestas:
- forensic_videos_uploaded_total
- forensic_faces_detected_total
- forensic_processing_duration_seconds
- forensic_api_requests_total
```

---

## 🎯 Mejores Prácticas

### 1. Gestión de Modelos de IA

```bash
# Versionar modelos con DVC o Git LFS
dvc add backend/models/yolov10n.pt
dvc push

# En producción, descargar desde S3
aws s3 sync s3://forensic-models/ backend/models/
```

### 2. Optimización de Procesamiento

```python
# Batch processing de frames
frames_batch = [f[1] for f in frames[:100]]
results = ai.batch_detect_faces(frames_batch)

# Usar GPU cuando esté disponible
device = "cuda" if torch.cuda.is_available() else "cpu"
```

### 3. Backup de Base de Datos

```bash
# Backup automático diario
kubectl create cronjob postgres-backup \
  --image=postgres:16 \
  --schedule="0 2 * * *" \
  -- pg_dump -h postgres -U forensic forensic_db > backup_$(date +%Y%m%d).sql
```

---

## 📚 Estructura del Proyecto

```
securityHome/
├── backend/
│   ├── main.py                    # API FastAPI principal
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── api/                   # Endpoints REST
│       ├── core/
│       │   ├── auth.py           # OAuth2 + JWT + RBAC
│       │   └── config.py         # Configuración centralizada
│       ├── forensics/
│       │   ├── integrity.py      # SHA-256/512 + EXIF
│       │   ├── ai_inference.py   # YOLO + DeepFace
│       │   └── super_resolution.py  # Real-ESRGAN
│       ├── models/
│       │   ├── database.py       # SQLAlchemy + pgvector
│       │   └── models.py         # User, Video, FaceEmbedding, etc.
│       ├── services/
│       │   ├── forensic_service.py
│       │   ├── storage_service.py  # AWS S3 / GCS
│       │   └── video_service.py
│       └── workers/
│           ├── celery_app.py     # Celery config
│           └── tasks.py          # Tareas asíncronas
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── Dockerfile
│   └── FRONTEND_STRUCTURE.py     # Documentación del frontend
├── infrastructure/
│   ├── docker/
│   └── k8s/
│       ├── postgres-deployment.yaml
│       ├── redis-deployment.yaml
│       ├── api-deployment.yaml
│       ├── celery-deployment.yaml
│       └── secrets.yaml
├── docker-compose.yml            # Orquestación completa
└── README.md                     # Esta documentación
```

---

## 📄 Licencia

Este proyecto está bajo licencia MIT.

---

## 👨‍💻 Desarrollado con

- ❤️ Pasión por la justicia y la tecnología
- ☕ Mucho café
- 🧠 Arquitectura empresarial escalable
- 🔬 Estándares forenses internacionales

---

**ForensicVideo AI Platform** - *Transformando el análisis forense con IA*