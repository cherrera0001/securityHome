"""
Configuración centralizada del sistema
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración global de la aplicación"""
    
    # Aplicación
    PROJECT_NAME: str = "ForensicVideo AI Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # Base de datos PostgreSQL
    DATABASE_URL: str = "postgresql://forensic:forensic_pass@postgres:5432/forensic_db"
    
    # Redis para Celery
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    
    # Seguridad JWT
    SECRET_KEY: str = "your-super-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días
    
    # AWS S3 / Cloud Storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "forensic-video-storage"
    USE_S3: bool = True
    
    # Google Cloud Storage (alternativa)
    GCS_BUCKET_NAME: Optional[str] = None
    GCS_CREDENTIALS_PATH: Optional[str] = None
    
    # Modelos de IA
    YOLO_MODEL_PATH: str = "./models/yolov10n.pt"
    DEEPFACE_MODEL: str = "Facenet512"  # 512-dimensional embeddings
    ESRGAN_MODEL_PATH: str = "./models/RealESRGAN_x4plus.pth"
    
    # Procesamiento
    MAX_VIDEO_SIZE_MB: int = 500
    MAX_UPLOAD_SIZE_MB: int = 1000
    FRAME_EXTRACTION_FPS: int = 1  # Extraer 1 frame por segundo
    FACE_DETECTION_CONFIDENCE: float = 0.7
    OBJECT_DETECTION_CONFIDENCE: float = 0.5
    
    # Búsqueda facial (pgvector)
    FACE_MATCH_THRESHOLD: float = 0.6  # Distancia coseno máxima para considerar match
    MAX_FACE_MATCHES: int = 10
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Limites de rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
