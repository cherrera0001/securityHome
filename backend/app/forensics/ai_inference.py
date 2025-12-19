"""
Módulo de AI Inference para Análisis Forense
YOLOv10 para detección de objetos
DeepFace para reconocimiento facial y análisis biométrico
"""
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
import torch
from deepface import DeepFace
from ultralytics import YOLO
from pathlib import Path


class AIInferenceModule:
    """Módulo de inferencia de IA para análisis forense"""
    
    def __init__(self, yolo_model_path: str, deepface_model: str = "Facenet512"):
        """
        Inicializar modelos de IA
        
        Args:
            yolo_model_path: Ruta al modelo YOLOv10
            deepface_model: Modelo de DeepFace (Facenet512 para embeddings de 512 dims)
        """
        self.yolo_model = YOLO(yolo_model_path)
        self.deepface_model = deepface_model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"✅ YOLO Model loaded: {yolo_model_path}")
        print(f"✅ DeepFace Model: {deepface_model}")
        print(f"🖥️  Device: {self.device}")
    
    def detect_objects(
        self,
        frame: np.ndarray,
        confidence_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Detectar objetos en un frame usando YOLOv10
        
        Returns:
            Lista de objetos detectados con class, confidence, y bbox
        """
        results = self.yolo_model(frame, conf=confidence_threshold, device=self.device)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                detection = {
                    "class": result.names[int(box.cls)],
                    "confidence": float(box.conf),
                    "bbox": {
                        "x": int(box.xyxy[0][0]),
                        "y": int(box.xyxy[0][1]),
                        "width": int(box.xyxy[0][2] - box.xyxy[0][0]),
                        "height": int(box.xyxy[0][3] - box.xyxy[0][1])
                    }
                }
                detections.append(detection)
        
        return detections
    
    def detect_faces(
        self,
        frame: np.ndarray,
        confidence_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Detectar caras en un frame
        
        Returns:
            Lista de caras detectadas con ubicación
        """
        try:
            # DeepFace detecta caras automáticamente
            faces = DeepFace.extract_faces(
                img_path=frame,
                detector_backend="retinaface",  # Mejor detector
                enforce_detection=False
            )
            
            detected_faces = []
            for face in faces:
                if face.get("confidence", 0) >= confidence_threshold:
                    facial_area = face.get("facial_area", {})
                    detected_faces.append({
                        "confidence": face.get("confidence"),
                        "bbox": {
                            "x": facial_area.get("x", 0),
                            "y": facial_area.get("y", 0),
                            "width": facial_area.get("w", 0),
                            "height": facial_area.get("h", 0)
                        },
                        "face_image": face.get("face")
                    })
            
            return detected_faces
        except Exception as e:
            print(f"Error detectando caras: {e}")
            return []
    
    def generate_face_embedding(
        self,
        face_image: np.ndarray
    ) -> np.ndarray:
        """
        Generar embedding facial de 512 dimensiones usando DeepFace
        Este embedding permite comparación biométrica entre caras
        
        Returns:
            Array de 512 dimensiones (vector)
        """
        try:
            embedding = DeepFace.represent(
                img_path=face_image,
                model_name=self.deepface_model,
                enforce_detection=False
            )
            
            # DeepFace devuelve lista de embeddings
            if isinstance(embedding, list) and len(embedding) > 0:
                return np.array(embedding[0]["embedding"])
            
            return np.array(embedding["embedding"])
        except Exception as e:
            print(f"Error generando embedding: {e}")
            return np.zeros(512)  # Embedding vacío en caso de error
    
    def analyze_face_attributes(
        self,
        face_image: np.ndarray
    ) -> Dict[str, Any]:
        """
        Analizar atributos faciales: edad, género, emoción, raza
        Útil para análisis forense descriptivo
        """
        try:
            analysis = DeepFace.analyze(
                img_path=face_image,
                actions=["age", "gender", "emotion", "race"],
                enforce_detection=False
            )
            
            if isinstance(analysis, list):
                analysis = analysis[0]
            
            return {
                "age": analysis.get("age"),
                "gender": analysis.get("dominant_gender"),
                "emotion": analysis.get("dominant_emotion"),
                "race": analysis.get("dominant_race")
            }
        except Exception as e:
            print(f"Error analizando atributos faciales: {e}")
            return {
                "age": None,
                "gender": None,
                "emotion": None,
                "race": None
            }
    
    def compare_faces(
        self,
        face1: np.ndarray,
        face2: np.ndarray
    ) -> Tuple[float, bool]:
        """
        Comparar dos caras para verificación biométrica
        
        Returns:
            (distance, is_match) - distancia y si hay match
        """
        try:
            result = DeepFace.verify(
                img1_path=face1,
                img2_path=face2,
                model_name=self.deepface_model,
                enforce_detection=False
            )
            
            distance = result.get("distance", 1.0)
            verified = result.get("verified", False)
            
            return distance, verified
        except Exception as e:
            print(f"Error comparando caras: {e}")
            return 1.0, False
    
    def detect_weapons(
        self,
        frame: np.ndarray,
        weapon_classes: List[str] = ["knife", "gun", "rifle"]
    ) -> List[Dict[str, Any]]:
        """
        Detectar armas en el frame (crítico para análisis forense)
        """
        all_detections = self.detect_objects(frame, confidence_threshold=0.6)
        
        # Filtrar solo armas
        weapons = [
            det for det in all_detections 
            if det["class"].lower() in weapon_classes
        ]
        
        return weapons
    
    def detect_vehicles(
        self,
        frame: np.ndarray
    ) -> List[Dict[str, Any]]:
        """
        Detectar vehículos y placas (útil para análisis forense)
        """
        all_detections = self.detect_objects(frame, confidence_threshold=0.5)
        
        vehicle_classes = ["car", "truck", "bus", "motorcycle", "bicycle"]
        vehicles = [
            det for det in all_detections 
            if det["class"].lower() in vehicle_classes
        ]
        
        return vehicles
    
    def generate_motion_heatmap(
        self,
        frames: List[np.ndarray]
    ) -> np.ndarray:
        """
        Generar heatmap de movimiento para visualización forense
        Muestra zonas de mayor actividad en el video
        """
        if len(frames) == 0:
            return np.zeros((480, 640))
        
        # Inicializar acumulador de diferencias
        height, width = frames[0].shape[:2]
        heatmap = np.zeros((height, width), dtype=np.float32)
        
        # Calcular diferencias entre frames consecutivos
        for i in range(1, len(frames)):
            # Convertir a escala de grises
            gray1 = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            
            # Diferencia absoluta
            diff = cv2.absdiff(gray1, gray2)
            
            # Acumular
            heatmap += diff.astype(np.float32)
        
        # Normalizar
        heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
        heatmap = heatmap.astype(np.uint8)
        
        # Aplicar colormap para visualización
        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        
        return heatmap_color
    
    def detect_tattoos(
        self,
        body_image: np.ndarray
    ) -> List[Dict[str, Any]]:
        """
        Detectar tatuajes en imagen corporal
        Importante para identificación forense
        
        TODO: Requiere modelo especializado de detección de tatuajes
        Por ahora, retorna placeholder
        """
        # Implementar con modelo especializado (TattooNet, etc.)
        return []
    
    def extract_license_plate(
        self,
        vehicle_image: np.ndarray
    ) -> str:
        """
        Extraer texto de placa vehicular usando OCR
        
        TODO: Integrar con EasyOCR o Tesseract
        """
        # Implementar OCR para placas
        return ""
