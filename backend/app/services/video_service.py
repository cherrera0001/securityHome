"""
Servicio de Video - Procesamiento y extracción de frames
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional
import tempfile
from pathlib import Path


class VideoService:
    """Servicio para procesamiento de videos"""
    
    @staticmethod
    def extract_video_metadata(video_path: str) -> dict:
        """Extraer metadata del video"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError("No se pudo abrir el video")
        
        metadata = {
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "codec": int(cap.get(cv2.CAP_PROP_FOURCC)),
            "duration": 0
        }
        
        if metadata["fps"] > 0:
            metadata["duration"] = metadata["frame_count"] / metadata["fps"]
        
        metadata["resolution"] = f"{metadata['width']}x{metadata['height']}"
        
        cap.release()
        return metadata
    
    @staticmethod
    def extract_frames(
        video_path: str,
        fps: int = 1,
        max_frames: Optional[int] = None
    ) -> List[Tuple[int, np.ndarray]]:
        """
        Extraer frames del video
        
        Args:
            video_path: Ruta al video
            fps: Frames por segundo a extraer (1 = 1 frame/segundo)
            max_frames: Número máximo de frames a extraer
        
        Returns:
            Lista de tuplas (frame_number, frame_image)
        """
        cap = cv2.VideoCapture(video_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        
        if video_fps == 0:
            cap.release()
            raise ValueError("FPS del video es 0")
        
        frame_interval = int(video_fps / fps)
        frames = []
        frame_count = 0
        extracted_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                frames.append((frame_count, frame))
                extracted_count += 1
                
                if max_frames and extracted_count >= max_frames:
                    break
            
            frame_count += 1
        
        cap.release()
        return frames
    
    @staticmethod
    def generate_thumbnail(video_path: str, timestamp: float = 1.0) -> np.ndarray:
        """Generar thumbnail del video"""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Ir al frame en el timestamp especificado
        frame_number = int(timestamp * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise ValueError("No se pudo extraer thumbnail")
        
        # Redimensionar a thumbnail (320x180)
        thumbnail = cv2.resize(frame, (320, 180), interpolation=cv2.INTER_AREA)
        return thumbnail
