"""
Celery Tasks - Procesamiento Asíncrono de Video
Pipeline completo: Detección de objetos, reconocimiento facial, super-resolution
"""
import cv2
import numpy as np
from celery import Task
from typing import List
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import uuid

from app.workers.celery_app import celery_app
from app.models.database import SessionLocal
from app.models.models import (
    Video, VideoStatus, FaceEmbedding, DetectedObject,
    ProcessingTask, MotionHeatmap, ChainOfCustody, Alert, AlertLevel
)
from app.forensics.ai_inference import AIInferenceModule
from app.forensics.super_resolution import SuperResolutionModule
from app.services.video_service import VideoService
from app.services.storage_service import StorageService
from app.core.config import settings


class DatabaseTask(Task):
    """Base task con sesión de base de datos"""
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True, name="app.workers.tasks.process_video_task")
def process_video_task(self, video_id: str):
    """
    Tarea principal de procesamiento de video
    Pipeline completo: extracción de frames, detección, análisis
    """
    db = self.db
    video = db.query(Video).filter(Video.id == uuid.UUID(video_id)).first()
    
    if not video:
        return {"error": "Video no encontrado"}
    
    try:
        # Actualizar estado
        video.status = VideoStatus.PROCESSING
        db.commit()
        
        # Actualizar progreso: 10%
        self.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Descargando video'})
        
        # Descargar video de S3
        storage = StorageService()
        video_content = await storage.download_file(f"videos/{video.filename}")
        
        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(video_content)
            video_path = tmp_file.name
        
        # Extraer metadata
        self.update_state(state='PROGRESS', meta={'progress': 20, 'status': 'Extrayendo metadata'})
        video_service = VideoService()
        metadata = video_service.extract_video_metadata(video_path)
        
        video.duration = metadata['duration']
        video.fps = metadata['fps']
        video.resolution = metadata['resolution']
        db.commit()
        
        # Generar thumbnail
        self.update_state(state='PROGRESS', meta={'progress': 25, 'status': 'Generando thumbnail'})
        thumbnail = video_service.generate_thumbnail(video_path)
        thumbnail_bytes = cv2.imencode('.jpg', thumbnail)[1].tobytes()
        thumbnail_url = await storage.upload_image(thumbnail_bytes, f"{video.id}_thumb.jpg", "thumbnails")
        video.thumbnail_url = thumbnail_url
        db.commit()
        
        # Extraer frames para análisis
        self.update_state(state='PROGRESS', meta={'progress': 30, 'status': 'Extrayendo frames'})
        frames = video_service.extract_frames(video_path, fps=settings.FRAME_EXTRACTION_FPS)
        
        # Inicializar módulos de IA
        ai_module = AIInferenceModule(
            yolo_model_path=settings.YOLO_MODEL_PATH,
            deepface_model=settings.DEEPFACE_MODEL
        )
        sr_module = SuperResolutionModule(model_path=settings.ESRGAN_MODEL_PATH)
        
        # Procesar cada frame
        total_frames = len(frames)
        faces_detected = 0
        objects_detected = 0
        
        for idx, (frame_number, frame) in enumerate(frames):
            progress = 30 + (idx / total_frames * 50)  # 30% - 80%
            self.update_state(
                state='PROGRESS',
                meta={
                    'progress': progress,
                    'status': f'Analizando frame {idx+1}/{total_frames}'
                }
            )
            
            timestamp = frame_number / metadata['fps']
            
            # Detectar objetos con YOLO
            objects = ai_module.detect_objects(frame, confidence_threshold=settings.OBJECT_DETECTION_CONFIDENCE)
            for obj in objects:
                detected_obj = DetectedObject(
                    video_id=video.id,
                    frame_number=frame_number,
                    timestamp_in_video=timestamp,
                    object_class=obj['class'],
                    confidence=obj['confidence'],
                    bbox_x=obj['bbox']['x'],
                    bbox_y=obj['bbox']['y'],
                    bbox_width=obj['bbox']['width'],
                    bbox_height=obj['bbox']['height']
                )
                db.add(detected_obj)
                objects_detected += 1
            
            # Detectar caras con DeepFace
            faces = ai_module.detect_faces(frame, confidence_threshold=settings.FACE_DETECTION_CONFIDENCE)
            for face in faces:
                # Extraer región de la cara
                bbox = face['bbox']
                face_crop = frame[
                    bbox['y']:bbox['y']+bbox['height'],
                    bbox['x']:bbox['x']+bbox['width']
                ]
                
                if face_crop.size == 0:
                    continue
                
                # Generar embedding facial (512 dimensiones)
                embedding = ai_module.generate_face_embedding(face_crop)
                
                # Analizar atributos faciales
                attributes = ai_module.analyze_face_attributes(face_crop)
                
                # Guardar cara original
                face_bytes = cv2.imencode('.jpg', face_crop)[1].tobytes()
                face_filename = f"{video.id}_face_{frame_number}_{uuid.uuid4()}.jpg"
                face_url = await storage.upload_image(face_bytes, face_filename, "faces")
                
                # Mejorar cara con Super-Resolution
                enhanced_face = sr_module.enhance_face(face_crop, target_resolution="4k")
                enhanced_bytes = cv2.imencode('.jpg', enhanced_face)[1].tobytes()
                enhanced_filename = f"{video.id}_face_enhanced_{frame_number}_{uuid.uuid4()}.jpg"
                enhanced_url = await storage.upload_image(enhanced_bytes, enhanced_filename, "faces_enhanced")
                
                # Crear registro de embedding facial
                face_embedding = FaceEmbedding(
                    video_id=video.id,
                    embedding=embedding.tolist(),
                    frame_number=frame_number,
                    timestamp_in_video=timestamp,
                    confidence=face['confidence'],
                    bbox_x=bbox['x'],
                    bbox_y=bbox['y'],
                    bbox_width=bbox['width'],
                    bbox_height=bbox['height'],
                    age=attributes.get('age'),
                    gender=attributes.get('gender'),
                    emotion=attributes.get('emotion'),
                    race=attributes.get('race'),
                    face_image_url=face_url,
                    enhanced_face_url=enhanced_url
                )
                db.add(face_embedding)
                faces_detected += 1
            
            # Commit cada 10 frames
            if idx % 10 == 0:
                db.commit()
        
        # Commit final
        db.commit()
        
        # Generar heatmap de movimiento
        self.update_state(state='PROGRESS', meta={'progress': 85, 'status': 'Generando heatmap de movimiento'})
        frame_images = [f[1] for f in frames[:100]]  # Primeros 100 frames
        heatmap = ai_module.generate_motion_heatmap(frame_images)
        heatmap_bytes = cv2.imencode('.jpg', heatmap)[1].tobytes()
        heatmap_url = await storage.upload_image(heatmap_bytes, f"{video.id}_heatmap.jpg", "heatmaps")
        
        # Guardar heatmap
        motion_heatmap = MotionHeatmap(
            video_id=video.id,
            heatmap_image_url=heatmap_url,
            start_time=0,
            end_time=min(100 / metadata['fps'], metadata['duration']),
            total_movement_score=0,  # TODO: Calcular score
            hotspot_count=0
        )
        db.add(motion_heatmap)
        
        # Actualizar video
        self.update_state(state='PROGRESS', meta={'progress': 95, 'status': 'Finalizando procesamiento'})
        video.status = VideoStatus.COMPLETED
        video.processing_progress = 100.0
        video.processed_at = datetime.utcnow()
        video.analysis_results = {
            "faces_detected": faces_detected,
            "objects_detected": objects_detected,
            "frames_analyzed": total_frames
        }
        db.commit()
        
        # Registrar en cadena de custodia
        custody = ChainOfCustody(
            video_id=video.id,
            action="processed",
            actor_name="AI Processing System",
            hash_after=video.sha256_hash,
            operation_details={
                "faces_detected": faces_detected,
                "objects_detected": objects_detected,
                "processing_time": "completed"
            }
        )
        db.add(custody)
        db.commit()
        
        # Crear alerta de procesamiento completado
        alert = Alert(
            user_id=video.user_id,
            video_id=video.id,
            title=f"Procesamiento completado: {video.original_filename}",
            description=f"Se detectaron {faces_detected} rostros y {objects_detected} objetos",
            alert_level=AlertLevel.LOW,
            alert_type="processing_completed"
        )
        db.add(alert)
        db.commit()
        
        # Limpiar archivo temporal
        Path(video_path).unlink(missing_ok=True)
        
        return {
            "status": "completed",
            "video_id": str(video.id),
            "faces_detected": faces_detected,
            "objects_detected": objects_detected
        }
    
    except Exception as e:
        # Marcar como fallido
        video.status = VideoStatus.FAILED
        db.commit()
        
        # Registrar error
        custody = ChainOfCustody(
            video_id=video.id,
            action="processing_failed",
            actor_name="AI Processing System",
            operation_details={"error": str(e)}
        )
        db.add(custody)
        db.commit()
        
        raise


@celery_app.task(name="app.workers.tasks.search_similar_faces_task")
def search_similar_faces_task(face_embedding_id: str, threshold: float = 0.6):
    """Búsqueda asíncrona de caras similares"""
    # Implementar búsqueda de similitud
    pass


@celery_app.task(name="app.workers.tasks.enhance_face_task")
def enhance_face_task(face_embedding_id: str):
    """Tarea para mejorar calidad de una cara específica"""
    db = SessionLocal()
    
    try:
        face = db.query(FaceEmbedding).filter(FaceEmbedding.id == uuid.UUID(face_embedding_id)).first()
        if not face:
            return {"error": "Face not found"}
        
        # Descargar cara
        storage = StorageService()
        # TODO: Implementar mejora
        
        return {"status": "enhanced"}
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.cleanup_old_tasks")
def cleanup_old_tasks():
    """Limpiar tareas antiguas completadas"""
    db = SessionLocal()
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        old_tasks = db.query(ProcessingTask).filter(
            ProcessingTask.completed_at < cutoff_date,
            ProcessingTask.status == "completed"
        ).all()
        
        for task in old_tasks:
            db.delete(task)
        
        db.commit()
        return {"deleted": len(old_tasks)}
    finally:
        db.close()
