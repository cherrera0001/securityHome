"""
API Principal - ForensicVideo AI Platform
FastAPI con endpoints para autenticación, upload de videos, procesamiento, búsqueda facial y reportes
"""
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
import hashlib
import uuid
from pydantic import BaseModel, EmailStr

from app.core.config import settings
from app.core.auth import (
    AuthService, get_current_user, require_admin, 
    require_investigator, PermissionChecker
)
from app.models.database import get_db, init_db
from app.models.models import (
    User, Video, FaceEmbedding, ChainOfCustody, Alert, 
    ForensicReport, ProcessingTask, UserRole, VideoStatus, AlertLevel
)
# from app.services.video_service import VideoService
# from app.services.storage_service import StorageService
# from app.services.forensic_service import ForensicService
# from app.workers.celery_app import celery_app
# from app.workers.tasks import process_video_task

# Inicializar FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Pydantic Schemas ====================

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.CLIENT
    organization: Optional[str] = None


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    full_name: Optional[str]
    role: UserRole
    organization: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class VideoUploadResponse(BaseModel):
    video_id: uuid.UUID
    filename: str
    status: VideoStatus
    sha256_hash: str
    message: str


class VideoResponse(BaseModel):
    id: uuid.UUID
    filename: str
    original_filename: str
    status: VideoStatus
    duration: Optional[float]
    resolution: Optional[str]
    sha256_hash: str
    uploaded_at: str
    processing_progress: float
    thumbnail_url: Optional[str]
    
    class Config:
        from_attributes = True


class FaceEmbeddingResponse(BaseModel):
    id: uuid.UUID
    video_id: uuid.UUID
    frame_number: int
    timestamp_in_video: float
    confidence: float
    face_image_url: Optional[str]
    enhanced_face_url: Optional[str]
    is_person_of_interest: bool
    poi_label: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    emotion: Optional[str]
    
    class Config:
        from_attributes = True


class FaceSearchRequest(BaseModel):
    face_embedding_id: uuid.UUID
    threshold: float = 0.6
    max_results: int = 10


class FaceMatchResponse(BaseModel):
    face_id: uuid.UUID
    video_id: uuid.UUID
    similarity_score: float
    face_image_url: Optional[str]
    video_filename: str
    timestamp_in_video: float


class AlertResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    alert_level: AlertLevel
    alert_type: str
    is_read: bool
    created_at: str
    
    class Config:
        from_attributes = True


class MarkPOIRequest(BaseModel):
    face_embedding_id: uuid.UUID
    poi_label: str
    notes: Optional[str] = None


class ReportGenerateRequest(BaseModel):
    video_id: uuid.UUID
    report_type: str
    include_faces: bool = True
    include_objects: bool = True
    include_chain_of_custody: bool = True


# ==================== Health Check ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational"
    }


@app.on_event("startup")
async def startup_event():
    """Inicializar base de datos al arrancar"""
    init_db()
    print(f"✅ {settings.PROJECT_NAME} v{settings.VERSION} iniciado correctamente")


# ==================== Authentication Endpoints ====================

@app.post(f"{settings.API_V1_STR}/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Registrar nuevo usuario"""
    # Verificar si el email ya existe
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username ya existe")
    
    # Crear usuario
    hashed_password = AuthService.get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        organization=user_data.organization
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@app.post(f"{settings.API_V1_STR}/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login con OAuth2"""
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get(f"{settings.API_V1_STR}/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return current_user


# ==================== Video Upload & Processing Endpoints ====================

@app.post(f"{settings.API_V1_STR}/videos/upload", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Subir video para análisis forense
    - Calcula hash SHA-256/512 para integridad
    - Extrae metadatos EXIF
    - Crea registro en cadena de custodia
    - Inicia procesamiento asíncrono con Celery
    """
    # Validar tamaño
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400, 
            detail=f"Archivo demasiado grande. Máximo: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    # Calcular hashes para integridad forense
    sha256_hash = hashlib.sha256(content).hexdigest()
    sha512_hash = hashlib.sha512(content).hexdigest()
    
    # Verificar si ya existe este video (prevenir duplicados)
    existing = db.query(Video).filter(Video.sha256_hash == sha256_hash).first()
    if existing:
        raise HTTPException(status_code=400, detail="Este video ya fue subido anteriormente")
    
    # Extraer metadatos EXIF
    forensic_service = ForensicService()
    exif_metadata = forensic_service.extract_exif_metadata(content)
    
    # Guardar en storage (S3 o local)
    storage_service = StorageService()
    s3_url = await storage_service.upload_video(content, f"{sha256_hash}_{file.filename}")
    
    # Crear registro de video
    video = Video(
        user_id=current_user.id,
        filename=f"{sha256_hash}_{file.filename}",
        original_filename=file.filename,
        s3_url=s3_url,
        file_size=file_size,
        sha256_hash=sha256_hash,
        sha512_hash=sha512_hash,
        exif_metadata=exif_metadata,
        status=VideoStatus.UPLOADED
    )
    
    db.add(video)
    db.commit()
    db.refresh(video)
    
    # Registrar en cadena de custodia
    custody = ChainOfCustody(
        video_id=video.id,
        action="uploaded",
        actor_id=current_user.id,
        actor_name=current_user.full_name or current_user.username,
        hash_after=sha256_hash,
        operation_details={"filename": file.filename, "size_bytes": file_size}
    )
    db.add(custody)
    db.commit()
    
    # Iniciar procesamiento asíncrono con Celery
    task = process_video_task.delay(str(video.id))
    
    # Registrar tarea
    processing_task = ProcessingTask(
        video_id=video.id,
        celery_task_id=task.id,
        task_type="full_video_processing"
    )
    db.add(processing_task)
    db.commit()
    
    return VideoUploadResponse(
        video_id=video.id,
        filename=video.filename,
        status=video.status,
        sha256_hash=sha256_hash,
        message="Video subido correctamente. Procesamiento iniciado."
    )


@app.get(f"{settings.API_V1_STR}/videos", response_model=List[VideoResponse])
async def list_videos(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Listar videos del usuario (clientes solo ven los suyos, investigadores ven todos)"""
    if current_user.role in [UserRole.ADMIN, UserRole.INVESTIGATOR]:
        videos = db.query(Video).offset(skip).limit(limit).all()
    else:
        videos = db.query(Video).filter(Video.user_id == current_user.id).offset(skip).limit(limit).all()
    
    return videos


@app.get(f"{settings.API_V1_STR}/videos/{{video_id}}", response_model=VideoResponse)
async def get_video(
    video_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener información de un video específico"""
    video = db.query(Video).filter(Video.id == video_id).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    
    if not PermissionChecker.can_access_video(current_user, str(video.user_id)):
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    return video


@app.get(f"{settings.API_V1_STR}/videos/{{video_id}}/status")
async def get_video_processing_status(
    video_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener estado del procesamiento del video"""
    video = db.query(Video).filter(Video.id == video_id).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    
    if not PermissionChecker.can_access_video(current_user, str(video.user_id)):
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    # Obtener tareas relacionadas
    tasks = db.query(ProcessingTask).filter(ProcessingTask.video_id == video_id).all()
    
    return {
        "video_id": video.id,
        "status": video.status.value,
        "progress": video.processing_progress,
        "tasks": [
            {
                "task_type": t.task_type,
                "status": t.status,
                "progress": t.progress
            } for t in tasks
        ]
    }


# ==================== Face Detection & Search Endpoints ====================

@app.get(f"{settings.API_V1_STR}/videos/{{video_id}}/faces", response_model=List[FaceEmbeddingResponse])
async def get_detected_faces(
    video_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener todas las caras detectadas en un video"""
    video = db.query(Video).filter(Video.id == video_id).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    
    if not PermissionChecker.can_access_video(current_user, str(video.user_id)):
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    faces = db.query(FaceEmbedding).filter(FaceEmbedding.video_id == video_id).all()
    return faces


@app.post(f"{settings.API_V1_STR}/faces/search", response_model=List[FaceMatchResponse])
async def search_similar_faces(
    search_request: FaceSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Buscar caras similares usando pgvector
    Permite identificar si el mismo delincuente aparece en otros videos
    """
    # Obtener el embedding de consulta
    query_face = db.query(FaceEmbedding).filter(FaceEmbedding.id == search_request.face_embedding_id).first()
    
    if not query_face:
        raise HTTPException(status_code=404, detail="Cara no encontrada")
    
    # Búsqueda de similitud con pgvector (distancia coseno)
    from sqlalchemy import text
    
    query = text("""
        SELECT 
            fe.id, fe.video_id, fe.face_image_url, fe.timestamp_in_video,
            v.filename,
            (fe.embedding <=> :query_embedding) as distance
        FROM face_embeddings fe
        JOIN videos v ON fe.video_id = v.id
        WHERE fe.id != :query_face_id
        AND (fe.embedding <=> :query_embedding) < :threshold
        ORDER BY distance
        LIMIT :max_results
    """)
    
    results = db.execute(
        query,
        {
            "query_embedding": query_face.embedding,
            "query_face_id": str(search_request.face_embedding_id),
            "threshold": search_request.threshold,
            "max_results": search_request.max_results
        }
    ).fetchall()
    
    matches = []
    for row in results:
        matches.append(FaceMatchResponse(
            face_id=row.id,
            video_id=row.video_id,
            similarity_score=1 - row.distance,  # Convertir distancia a similitud
            face_image_url=row.face_image_url,
            video_filename=row.filename,
            timestamp_in_video=row.timestamp_in_video
        ))
    
    return matches


@app.post(f"{settings.API_V1_STR}/faces/mark-poi")
async def mark_person_of_interest(
    request: MarkPOIRequest,
    current_user: User = Depends(require_investigator),
    db: Session = Depends(get_db)
):
    """Marcar una cara como 'Persona de Interés' (solo investigadores)"""
    face = db.query(FaceEmbedding).filter(FaceEmbedding.id == request.face_embedding_id).first()
    
    if not face:
        raise HTTPException(status_code=404, detail="Cara no encontrada")
    
    face.is_person_of_interest = True
    face.poi_label = request.poi_label
    face.notes = request.notes
    
    db.commit()
    
    # Crear alerta
    alert = Alert(
        user_id=current_user.id,
        video_id=face.video_id,
        face_embedding_id=face.id,
        title=f"Persona de Interés Marcada: {request.poi_label}",
        description=f"Investigador {current_user.full_name} marcó una persona de interés",
        alert_level=AlertLevel.HIGH,
        alert_type="poi_marked"
    )
    db.add(alert)
    db.commit()
    
    return {"message": "Persona de interés marcada exitosamente", "face_id": face.id}


# ==================== Alerts Endpoints ====================

@app.get(f"{settings.API_V1_STR}/alerts", response_model=List[AlertResponse])
async def get_alerts(
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener alertas del usuario"""
    query = db.query(Alert).filter(Alert.user_id == current_user.id)
    
    if unread_only:
        query = query.filter(Alert.is_read == False)
    
    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    return alerts


@app.patch(f"{settings.API_V1_STR}/alerts/{{alert_id}}/read")
async def mark_alert_as_read(
    alert_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marcar alerta como leída"""
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == current_user.id).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    
    alert.is_read = True
    db.commit()
    
    return {"message": "Alerta marcada como leída"}


# ==================== Forensic Reports Endpoints ====================

@app.post(f"{settings.API_V1_STR}/reports/generate")
async def generate_forensic_report(
    request: ReportGenerateRequest,
    current_user: User = Depends(require_investigator),
    db: Session = Depends(get_db)
):
    """Generar reporte pericial (solo investigadores)"""
    video = db.query(Video).filter(Video.id == request.video_id).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    
    # Recopilar datos del reporte
    report_data = {
        "video": {
            "filename": video.original_filename,
            "sha256": video.sha256_hash,
            "uploaded_at": str(video.uploaded_at),
            "duration": video.duration,
            "resolution": video.resolution
        }
    }
    
    if request.include_faces:
        faces = db.query(FaceEmbedding).filter(FaceEmbedding.video_id == video.id).all()
        report_data["faces"] = [
            {
                "frame": f.frame_number,
                "timestamp": f.timestamp_in_video,
                "confidence": f.confidence,
                "is_poi": f.is_person_of_interest,
                "label": f.poi_label
            } for f in faces
        ]
    
    if request.include_chain_of_custody:
        custody_records = db.query(ChainOfCustody).filter(ChainOfCustody.video_id == video.id).all()
        report_data["chain_of_custody"] = [
            {
                "action": c.action,
                "actor": c.actor_name,
                "timestamp": str(c.timestamp),
                "hash": c.hash_after
            } for c in custody_records
        ]
    
    # Crear reporte
    report = ForensicReport(
        video_id=video.id,
        generated_by=current_user.id,
        report_title=f"Análisis Forense - {video.original_filename}",
        report_type=request.report_type,
        report_data=report_data
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # TODO: Generar PDF del reporte
    
    return {
        "report_id": report.id,
        "message": "Reporte generado exitosamente",
        "data": report_data
    }


@app.get(f"{settings.API_V1_STR}/reports/{{report_id}}")
async def get_report(
    report_id: uuid.UUID,
    current_user: User = Depends(require_investigator),
    db: Session = Depends(get_db)
):
    """Obtener reporte específico"""
    report = db.query(ForensicReport).filter(ForensicReport.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    
    return report


# ==================== Chain of Custody Endpoints ====================

@app.get(f"{settings.API_V1_STR}/videos/{{video_id}}/chain-of-custody")
async def get_chain_of_custody(
    video_id: uuid.UUID,
    current_user: User = Depends(require_investigator),
    db: Session = Depends(get_db)
):
    """Obtener cadena de custodia de un video (solo investigadores)"""
    video = db.query(Video).filter(Video.id == video_id).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    
    custody_records = db.query(ChainOfCustody).filter(
        ChainOfCustody.video_id == video_id
    ).order_by(ChainOfCustody.timestamp).all()
    
    return {
        "video_id": video.id,
        "filename": video.original_filename,
        "sha256_hash": video.sha256_hash,
        "records": [
            {
                "id": str(c.id),
                "action": c.action,
                "actor": c.actor_name,
                "timestamp": str(c.timestamp),
                "hash_after": c.hash_after,
                "ip_address": c.ip_address,
                "details": c.operation_details
            } for c in custody_records
        ]
    }


# ==================== Admin Endpoints ====================

@app.get(f"{settings.API_V1_STR}/admin/users", response_model=List[UserResponse])
async def list_all_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Listar todos los usuarios (solo admin)"""
    users = db.query(User).all()
    return users


@app.get(f"{settings.API_V1_STR}/admin/stats")
async def get_system_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas del sistema (solo admin)"""
    total_users = db.query(User).count()
    total_videos = db.query(Video).count()
    total_faces = db.query(FaceEmbedding).count()
    processing_videos = db.query(Video).filter(Video.status == VideoStatus.PROCESSING).count()
    
    return {
        "total_users": total_users,
        "total_videos": total_videos,
        "total_faces_detected": total_faces,
        "videos_processing": processing_videos,
        "system_status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
