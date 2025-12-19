"""
Servicio Forense - Integración de módulos
"""
from app.forensics.integrity import IntegrityModule
from app.forensics.ai_inference import AIInferenceModule
from app.forensics.super_resolution import SuperResolutionModule
from app.core.config import settings


class ForensicService:
    """Servicio centralizado de análisis forense"""
    
    def __init__(self):
        self.integrity = IntegrityModule()
        # Los módulos de IA se inicializan bajo demanda para ahorrar recursos
    
    def extract_exif_metadata(self, file_content: bytes):
        """Extraer metadatos EXIF"""
        return self.integrity.extract_exif_metadata(file_content)
    
    def calculate_hash(self, file_content: bytes, algorithm: str = "sha256") -> str:
        """Calcular hash del archivo"""
        if algorithm == "sha256":
            return self.integrity.calculate_sha256(file_content)
        elif algorithm == "sha512":
            return self.integrity.calculate_sha512(file_content)
        else:
            raise ValueError(f"Algoritmo no soportado: {algorithm}")
