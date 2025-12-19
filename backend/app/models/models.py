"""
Modelos de Base de Datos para Sistema de Análisis Forense de Video
Incluye soporte para pgvector para búsqueda de similitud facial
"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, 
    Boolean, Text, Float, Enum, JSON, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
import uuid

from app.models.database import Base


class UserRole(PyEnum):
    """Roles del sistema RBAC"""
    ADMIN = "admin"
    INVESTIGATOR = "investigator"  # Analista Forense
    CLIENT = "client"  # Usuario Final


class VideoStatus(PyEnum):
    """Estados del procesamiento de video"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AlertLevel(PyEnum):
    """Niveles de alerta"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class User(Base):
    """Modelo de Usuario con RBAC"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CLIENT)
    organization = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    videos = relationship("Video", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", foreign_keys="Alert.user_id", back_populates="user", cascade="all, delete-orphan")


class Video(Base):
    """Modelo de Video con cadena de custodia"""
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    
    # Almacenamiento en Cloud
    s3_url = Column(String(1000))
    thumbnail_url = Column(String(1000))
    
    # Metadata del video
    duration = Column(Float)  # segundos
    fps = Column(Float)
    resolution = Column(String(50))  # e.g., "1920x1080"
    codec = Column(String(50))
    file_size = Column(Integer)  # bytes
    
    # Estado y procesamiento
    status = Column(Enum(VideoStatus), default=VideoStatus.UPLOADED)
    processing_progress = Column(Float, default=0.0)  # 0-100
    
    # Integridad Forense
    sha256_hash = Column(String(64), unique=True, nullable=False, index=True)
    sha512_hash = Column(String(128))
    exif_metadata = Column(JSONB)  # Metadata EXIF original
    
    # Timestamps
    recorded_at = Column(DateTime)  # Fecha original de grabación
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Análisis forense
    analysis_results = Column(JSONB)  # Resultados del análisis
    
    # Relaciones
    user = relationship("User", back_populates="videos")
    chain_of_custody = relationship("ChainOfCustody", back_populates="video", cascade="all, delete-orphan")
    face_embeddings = relationship("FaceEmbedding", back_populates="video", cascade="all, delete-orphan")
    detected_objects = relationship("DetectedObject", back_populates="video", cascade="all, delete-orphan")
    processing_tasks = relationship("ProcessingTask", back_populates="video", cascade="all, delete-orphan")
    heatmaps = relationship("MotionHeatmap", back_populates="video", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_video_user_status', 'user_id', 'status'),
        Index('idx_video_created', 'uploaded_at'),
    )


class ChainOfCustody(Base):
    """Cadena de Custodia para trazabilidad forense"""
    __tablename__ = "chain_of_custody"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    
    # Información de la acción
    action = Column(String(100), nullable=False)  # "uploaded", "processed", "exported", etc.
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    actor_name = Column(String(255))
    
    # Integridad
    hash_before = Column(String(128))
    hash_after = Column(String(128))
    
    # Metadata de la operación
    operation_details = Column(JSONB)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relaciones
    video = relationship("Video", back_populates="chain_of_custody")


class FaceEmbedding(Base):
    """Embeddings faciales para búsqueda de similitud con pgvector"""
    __tablename__ = "face_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    
    # Embedding facial (512 dimensiones para DeepFace)
    embedding = Column(Vector(512), nullable=False)
    
    # Información de detección
    frame_number = Column(Integer, nullable=False)
    timestamp_in_video = Column(Float)  # segundos
    confidence = Column(Float)  # 0-1
    
    # Bounding box de la cara
    bbox_x = Column(Integer)
    bbox_y = Column(Integer)
    bbox_width = Column(Integer)
    bbox_height = Column(Integer)
    
    # Face attributes
    age = Column(Integer)
    gender = Column(String(20))
    emotion = Column(String(50))
    race = Column(String(50))
    
    # URL de imagen de la cara extraída
    face_image_url = Column(String(1000))
    enhanced_face_url = Column(String(1000))  # Versión mejorada con Real-ESRGAN
    
    # Marcado por investigadores
    is_person_of_interest = Column(Boolean, default=False)
    poi_label = Column(String(255))  # Etiqueta personalizada
    notes = Column(Text)
    
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    video = relationship("Video", back_populates="face_embeddings")
    matches = relationship("FaceMatch", foreign_keys="FaceMatch.query_face_id", back_populates="query_face")

    __table_args__ = (
        Index('idx_face_video', 'video_id'),
        Index('idx_face_poi', 'is_person_of_interest'),
        # Índice IVFFlat para búsqueda rápida de vectores
        Index('idx_face_embedding', 'embedding', postgresql_using='ivfflat', 
              postgresql_with={'lists': 100}, postgresql_ops={'embedding': 'vector_cosine_ops'}),
    )


class FaceMatch(Base):
    """Matches entre caras detectadas en diferentes videos"""
    __tablename__ = "face_matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_face_id = Column(UUID(as_uuid=True), ForeignKey("face_embeddings.id"), nullable=False)
    matched_face_id = Column(UUID(as_uuid=True), ForeignKey("face_embeddings.id"), nullable=False)
    
    # Similitud (distancia coseno: 0-2, donde 0 es idéntico)
    similarity_score = Column(Float, nullable=False)
    
    # Flag si es confirmado por investigador
    is_confirmed = Column(Boolean, default=False)
    confirmed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    query_face = relationship("FaceEmbedding", foreign_keys=[query_face_id], back_populates="matches")
    matched_face = relationship("FaceEmbedding", foreign_keys=[matched_face_id])

    __table_args__ = (
        Index('idx_match_query', 'query_face_id'),
        Index('idx_match_similarity', 'similarity_score'),
    )


class DetectedObject(Base):
    """Objetos detectados con YOLOv10"""
    __tablename__ = "detected_objects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    
    # Información de detección
    frame_number = Column(Integer, nullable=False)
    timestamp_in_video = Column(Float)
    
    # Clasificación
    object_class = Column(String(100), nullable=False)  # "person", "weapon", "vehicle", etc.
    confidence = Column(Float)
    
    # Bounding box
    bbox_x = Column(Integer)
    bbox_y = Column(Integer)
    bbox_width = Column(Integer)
    bbox_height = Column(Integer)
    
    # URL de snapshot
    snapshot_url = Column(String(1000))
    
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    video = relationship("Video", back_populates="detected_objects")

    __table_args__ = (
        Index('idx_object_video', 'video_id'),
        Index('idx_object_class', 'object_class'),
    )


class MotionHeatmap(Base):
    """Heatmaps de movimiento para visualización"""
    __tablename__ = "motion_heatmaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    
    # Datos del heatmap
    heatmap_data = Column(JSONB)  # Matriz de calor serializada
    heatmap_image_url = Column(String(1000))  # Visualización renderizada
    
    # Segmento temporal
    start_time = Column(Float)  # segundos
    end_time = Column(Float)
    
    # Estadísticas
    total_movement_score = Column(Float)
    hotspot_count = Column(Integer)
    hotspot_coordinates = Column(JSONB)  # Lista de zonas de alto movimiento
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    video = relationship("Video", back_populates="heatmaps")

    __table_args__ = (
        Index('idx_heatmap_video', 'video_id'),
    )


class ProcessingTask(Base):
    """Tareas de procesamiento asíncrono (Celery)"""
    __tablename__ = "processing_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    
    # Información de la tarea
    celery_task_id = Column(String(255), unique=True, index=True)
    task_type = Column(String(100), nullable=False)  # "face_detection", "object_detection", etc.
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    
    # Progreso y resultados
    progress = Column(Float, default=0.0)
    result = Column(JSONB)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relaciones
    video = relationship("Video", back_populates="processing_tasks")

    __table_args__ = (
        Index('idx_task_video', 'video_id'),
        Index('idx_task_status', 'status'),
    )


class Alert(Base):
    """Alertas generadas por el sistema"""
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"))
    face_embedding_id = Column(UUID(as_uuid=True), ForeignKey("face_embeddings.id"))
    
    # Información de la alerta
    title = Column(String(500), nullable=False)
    description = Column(Text)
    alert_level = Column(Enum(AlertLevel), default=AlertLevel.MEDIUM)
    alert_type = Column(String(100))  # "face_match", "weapon_detected", "poi_detected", etc.
    
    # Metadata
    alert_metadata = Column(JSONB)
    
    # Estado
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    resolved_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relaciones
    user = relationship("User", foreign_keys=[user_id], back_populates="alerts")
    resolver = relationship("User", foreign_keys=[resolved_by])

    __table_args__ = (
        Index('idx_alert_user_status', 'user_id', 'is_read'),
        Index('idx_alert_level', 'alert_level'),
    )


class ForensicReport(Base):
    """Reportes periciales generados"""
    __tablename__ = "forensic_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Información del reporte
    report_title = Column(String(500), nullable=False)
    report_type = Column(String(100))  # "full_analysis", "face_identification", "chain_of_custody", etc.
    
    # Contenido del reporte
    report_data = Column(JSONB)  # Datos estructurados
    report_pdf_url = Column(String(1000))  # PDF generado
    
    # Firma digital
    digital_signature = Column(String(500))
    signature_timestamp = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_report_video', 'video_id'),
        Index('idx_report_user', 'generated_by'),
    )
