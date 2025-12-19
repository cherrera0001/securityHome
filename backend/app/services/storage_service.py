"""
Servicio de Almacenamiento - AWS S3 / Google Cloud Storage
"""
import boto3
from botocore.exceptions import ClientError
from typing import Optional
import io
from app.core.config import settings


class StorageService:
    """Servicio para almacenamiento en cloud (S3/GCS)"""
    
    def __init__(self):
        if settings.USE_S3:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.bucket_name = settings.S3_BUCKET_NAME
        else:
            self.s3_client = None
            self.bucket_name = None
    
    async def upload_video(self, file_content: bytes, filename: str) -> str:
        """
        Subir video a S3
        
        Returns:
            URL del archivo en S3
        """
        if not settings.USE_S3 or not self.s3_client:
            # Fallback: guardar localmente
            return self._save_locally(file_content, filename, "videos")
        
        try:
            # Upload a S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"videos/{filename}",
                Body=file_content,
                ContentType='video/mp4'
            )
            
            # Retornar URL
            url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/videos/{filename}"
            return url
        except ClientError as e:
            print(f"Error subiendo a S3: {e}")
            return self._save_locally(file_content, filename, "videos")
    
    async def upload_image(self, file_content: bytes, filename: str, folder: str = "faces") -> str:
        """Subir imagen (cara, thumbnail, etc.) a S3"""
        if not settings.USE_S3 or not self.s3_client:
            return self._save_locally(file_content, filename, folder)
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"{folder}/{filename}",
                Body=file_content,
                ContentType='image/jpeg'
            )
            
            url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{folder}/{filename}"
            return url
        except ClientError as e:
            print(f"Error subiendo imagen a S3: {e}")
            return self._save_locally(file_content, filename, folder)
    
    def _save_locally(self, file_content: bytes, filename: str, folder: str) -> str:
        """Guardar archivo localmente (fallback)"""
        from pathlib import Path
        
        base_dir = Path("/tmp/forensic_storage")
        folder_path = base_dir / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        
        file_path = folder_path / filename
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return f"/storage/{folder}/{filename}"
    
    async def download_file(self, s3_key: str) -> bytes:
        """Descargar archivo de S3"""
        if not settings.USE_S3 or not self.s3_client:
            return b""
        
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return response['Body'].read()
        except ClientError as e:
            print(f"Error descargando de S3: {e}")
            return b""
    
    async def delete_file(self, s3_key: str) -> bool:
        """Eliminar archivo de S3"""
        if not settings.USE_S3 or not self.s3_client:
            return False
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError as e:
            print(f"Error eliminando de S3: {e}")
            return False
