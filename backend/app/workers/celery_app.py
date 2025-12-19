"""
Celery Application Configuration
"""
from celery import Celery
from app.core.config import settings

# Crear instancia de Celery
celery_app = Celery(
    "forensic_video_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"]
)

# Configuración de Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hora máximo por tarea
    task_soft_time_limit=3000,  # 50 minutos soft limit
    worker_prefetch_multiplier=1,  # Procesar una tarea a la vez
    worker_max_tasks_per_child=50,  # Reiniciar worker cada 50 tareas
)

# Configuración de routing
celery_app.conf.task_routes = {
    "app.workers.tasks.process_video_task": {"queue": "video_processing"},
    "app.workers.tasks.detect_faces_task": {"queue": "face_detection"},
    "app.workers.tasks.detect_objects_task": {"queue": "object_detection"},
    "app.workers.tasks.enhance_face_task": {"queue": "enhancement"},
}

# Beat schedule (tareas periódicas)
celery_app.conf.beat_schedule = {
    "cleanup-old-tasks": {
        "task": "app.workers.tasks.cleanup_old_tasks",
        "schedule": 3600.0,  # Cada hora
    },
}
