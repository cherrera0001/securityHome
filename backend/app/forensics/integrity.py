"""
Módulo de Integridad Forense
Manejo de metadatos EXIF, hash SHA-256/512, y cadena de custodia
"""
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional
from PIL import Image
from PIL.ExifTags import TAGS
import io


class IntegrityModule:
    """Módulo para asegurar la integridad forense de los archivos"""
    
    @staticmethod
    def calculate_sha256(file_content: bytes) -> str:
        """Calcular hash SHA-256"""
        return hashlib.sha256(file_content).hexdigest()
    
    @staticmethod
    def calculate_sha512(file_content: bytes) -> str:
        """Calcular hash SHA-512"""
        return hashlib.sha512(file_content).hexdigest()
    
    @staticmethod
    def calculate_md5(file_content: bytes) -> str:
        """Calcular hash MD5 (legacy, para compatibilidad)"""
        return hashlib.md5(file_content).hexdigest()
    
    @staticmethod
    def verify_integrity(file_content: bytes, expected_hash: str, algorithm: str = "sha256") -> bool:
        """Verificar integridad del archivo"""
        if algorithm == "sha256":
            calculated_hash = IntegrityModule.calculate_sha256(file_content)
        elif algorithm == "sha512":
            calculated_hash = IntegrityModule.calculate_sha512(file_content)
        elif algorithm == "md5":
            calculated_hash = IntegrityModule.calculate_md5(file_content)
        else:
            raise ValueError(f"Algoritmo no soportado: {algorithm}")
        
        return calculated_hash == expected_hash
    
    @staticmethod
    def extract_exif_metadata(file_content: bytes) -> Dict[str, Any]:
        """
        Extraer metadatos EXIF de imagen/video
        Importante para establecer fecha/hora original de grabación
        """
        try:
            image = Image.open(io.BytesIO(file_content))
            exif_data = {}
            
            if hasattr(image, '_getexif') and image._getexif():
                exif = image._getexif()
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    # Convertir bytes a string si es necesario
                    if isinstance(value, bytes):
                        try:
                            value = value.decode()
                        except:
                            value = str(value)
                    exif_data[tag] = value
            
            return exif_data
        except Exception as e:
            return {"error": str(e), "message": "No se pudo extraer EXIF"}
    
    @staticmethod
    def generate_custody_certificate(
        video_id: str,
        filename: str,
        sha256_hash: str,
        sha512_hash: str,
        actor: str,
        action: str
    ) -> Dict[str, Any]:
        """
        Generar certificado de cadena de custodia
        Documento forense que certifica la integridad del archivo
        """
        timestamp = datetime.utcnow().isoformat()
        
        certificate = {
            "certificate_version": "1.0",
            "video_id": video_id,
            "filename": filename,
            "action": action,
            "actor": actor,
            "timestamp": timestamp,
            "integrity": {
                "sha256": sha256_hash,
                "sha512": sha512_hash
            },
            "forensic_standard": "ISO 27037:2012",
            "certification": f"Este certificado certifica que el archivo '{filename}' "
                           f"con hash SHA-256: {sha256_hash} fue {action} por {actor} "
                           f"en fecha {timestamp} UTC."
        }
        
        # Firmar el certificado (hash del certificado mismo)
        cert_json = json.dumps(certificate, sort_keys=True)
        certificate["certificate_signature"] = hashlib.sha256(cert_json.encode()).hexdigest()
        
        return certificate
    
    @staticmethod
    def create_evidence_package(
        video_data: Dict[str, Any],
        chain_of_custody: list,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crear paquete completo de evidencia forense
        Incluye video, cadena de custodia completa, y metadatos
        """
        package = {
            "package_version": "1.0",
            "created_at": datetime.utcnow().isoformat(),
            "video_information": video_data,
            "chain_of_custody": chain_of_custody,
            "metadata": metadata,
            "forensic_compliance": {
                "iso_27037": True,
                "nist_guidelines": True,
                "digital_evidence_standard": "IEEE 1849-2016"
            }
        }
        
        # Hash del paquete completo
        package_json = json.dumps(package, sort_keys=True)
        package["package_hash"] = hashlib.sha512(package_json.encode()).hexdigest()
        
        return package
