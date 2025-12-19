"""
Módulo de Super-Resolution usando Real-ESRGAN
Mejora la calidad de rostros pixelados para análisis forense
"""
import cv2
import numpy as np
import torch
from typing import Optional
from pathlib import Path


class SuperResolutionModule:
    """Módulo de mejora de imagen usando Real-ESRGAN"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Inicializar modelo Real-ESRGAN
        
        Args:
            model_path: Ruta al modelo RealESRGAN_x4plus.pth
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.scale = 4  # Factor de escalado 4x
        
        try:
            from basicsr.archs.rrdbnet_arch import RRDBNet
            from realesrgan import RealESRGANer
            
            # Configurar modelo
            model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32,
                scale=self.scale
            )
            
            # Cargar upsampler
            if model_path and Path(model_path).exists():
                self.model = RealESRGANer(
                    scale=self.scale,
                    model_path=model_path,
                    model=model,
                    tile=0,
                    tile_pad=10,
                    pre_pad=0,
                    half=True if self.device.type == "cuda" else False,
                    device=self.device
                )
                print(f"✅ Real-ESRGAN loaded: {model_path}")
            else:
                print("⚠️  Real-ESRGAN model not found, using fallback")
                self.model = None
        except ImportError:
            print("⚠️  Real-ESRGAN not installed, using fallback upscaling")
            self.model = None
    
    def enhance_image(
        self,
        image: np.ndarray,
        target_size: Optional[tuple] = None
    ) -> np.ndarray:
        """
        Mejorar calidad de imagen usando Real-ESRGAN
        
        Args:
            image: Imagen de entrada (BGR)
            target_size: Tamaño objetivo (width, height), None para 4x auto
        
        Returns:
            Imagen mejorada en alta resolución
        """
        if self.model is not None:
            try:
                # Usar Real-ESRGAN
                enhanced, _ = self.model.enhance(image, outscale=self.scale)
                
                if target_size:
                    enhanced = cv2.resize(enhanced, target_size, interpolation=cv2.INTER_LANCZOS4)
                
                return enhanced
            except Exception as e:
                print(f"Error en Real-ESRGAN: {e}, usando fallback")
                return self._fallback_enhance(image, target_size)
        else:
            return self._fallback_enhance(image, target_size)
    
    def _fallback_enhance(
        self,
        image: np.ndarray,
        target_size: Optional[tuple] = None
    ) -> np.ndarray:
        """
        Método de mejora alternativo sin Real-ESRGAN
        Usa interpolación bicúbica y filtros de nitidez
        """
        if target_size is None:
            # Escalar 4x por defecto
            height, width = image.shape[:2]
            target_size = (width * 4, height * 4)
        
        # Upscaling con interpolación Lanczos (mejor calidad)
        upscaled = cv2.resize(image, target_size, interpolation=cv2.INTER_LANCZOS4)
        
        # Aplicar filtro de nitidez
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(upscaled, -1, kernel)
        
        # Reducción de ruido
        denoised = cv2.fastNlMeansDenoisingColored(sharpened, None, 10, 10, 7, 21)
        
        return denoised
    
    def enhance_face(
        self,
        face_image: np.ndarray,
        target_resolution: str = "4k"
    ) -> np.ndarray:
        """
        Mejorar específicamente un rostro a alta resolución
        
        Args:
            face_image: Imagen del rostro recortado
            target_resolution: '4k' (3840x2160), '1080p' (1920x1080), '720p' (1280x720)
        
        Returns:
            Rostro mejorado en la resolución objetivo
        """
        # Definir tamaños objetivo
        resolutions = {
            "4k": (512, 512),      # Para rostros, usamos cuadrado
            "1080p": (256, 256),
            "720p": (128, 128)
        }
        
        target_size = resolutions.get(target_resolution, (512, 512))
        
        # Primero, mejorar con ESRGAN
        enhanced = self.enhance_image(face_image, target_size=None)
        
        # Redimensionar al tamaño final
        final = cv2.resize(enhanced, target_size, interpolation=cv2.INTER_LANCZOS4)
        
        # Post-procesamiento facial
        final = self._enhance_face_details(final)
        
        return final
    
    def _enhance_face_details(
        self,
        face_image: np.ndarray
    ) -> np.ndarray:
        """
        Post-procesamiento específico para mejorar detalles faciales
        """
        # Mejorar contraste adaptativo (CLAHE)
        lab = cv2.cvtColor(face_image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        enhanced_lab = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        # Mejorar nitidez de bordes
        blurred = cv2.GaussianBlur(enhanced, (0, 0), 3)
        sharpened = cv2.addWeighted(enhanced, 1.5, blurred, -0.5, 0)
        
        return sharpened
    
    def batch_enhance(
        self,
        images: list,
        target_size: Optional[tuple] = None
    ) -> list:
        """
        Mejorar múltiples imágenes en batch
        Más eficiente que procesar una por una
        """
        enhanced_images = []
        
        for image in images:
            try:
                enhanced = self.enhance_image(image, target_size)
                enhanced_images.append(enhanced)
            except Exception as e:
                print(f"Error mejorando imagen: {e}")
                enhanced_images.append(image)  # Retornar original en caso de error
        
        return enhanced_images
    
    def compare_quality(
        self,
        original: np.ndarray,
        enhanced: np.ndarray
    ) -> dict:
        """
        Comparar métricas de calidad entre imagen original y mejorada
        
        Returns:
            Diccionario con métricas PSNR, SSIM, etc.
        """
        from skimage.metrics import peak_signal_noise_ratio as psnr
        from skimage.metrics import structural_similarity as ssim
        
        # Redimensionar enhanced al tamaño de original para comparar
        enhanced_resized = cv2.resize(enhanced, (original.shape[1], original.shape[0]))
        
        # Calcular métricas
        psnr_value = psnr(original, enhanced_resized)
        ssim_value = ssim(original, enhanced_resized, channel_axis=2)
        
        # Comparar nitidez (Laplacian variance)
        original_blur = cv2.Laplacian(cv2.cvtColor(original, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
        enhanced_blur = cv2.Laplacian(cv2.cvtColor(enhanced_resized, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
        
        return {
            "psnr": psnr_value,
            "ssim": ssim_value,
            "sharpness_original": original_blur,
            "sharpness_enhanced": enhanced_blur,
            "improvement_ratio": enhanced_blur / original_blur if original_blur > 0 else 0
        }
