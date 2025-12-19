"""
Sistema de Autenticación con OAuth2, JWT y RBAC
"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.database import get_db
from app.models.models import User, UserRole

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


class AuthService:
    """Servicio de autenticación"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash de contraseña"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crear JWT token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Autenticar usuario"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Obtener usuario actual desde token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    
    return user


class RoleChecker:
    """Dependency para verificar roles de usuario (RBAC)"""
    
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Roles permitidos: {[r.value for r in self.allowed_roles]}"
            )
        return user


# Dependency shortcuts para roles comunes
require_admin = RoleChecker([UserRole.ADMIN])
require_investigator = RoleChecker([UserRole.ADMIN, UserRole.INVESTIGATOR])
require_any_authenticated = RoleChecker([UserRole.ADMIN, UserRole.INVESTIGATOR, UserRole.CLIENT])


class PermissionChecker:
    """Verificación de permisos granulares"""
    
    @staticmethod
    def can_access_video(user: User, video_user_id: str) -> bool:
        """Verificar si el usuario puede acceder a un video"""
        # Admin puede acceder a todo
        if user.role == UserRole.ADMIN:
            return True
        
        # Investigadores pueden acceder a videos de su organización
        if user.role == UserRole.INVESTIGATOR:
            return True  # TODO: Implementar lógica de organización
        
        # Clientes solo pueden acceder a sus propios videos
        return str(user.id) == str(video_user_id)
    
    @staticmethod
    def can_mark_person_of_interest(user: User) -> bool:
        """Solo investigadores y admins pueden marcar personas de interés"""
        return user.role in [UserRole.ADMIN, UserRole.INVESTIGATOR]
    
    @staticmethod
    def can_generate_report(user: User) -> bool:
        """Solo investigadores y admins pueden generar reportes"""
        return user.role in [UserRole.ADMIN, UserRole.INVESTIGATOR]
    
    @staticmethod
    def can_manage_users(user: User) -> bool:
        """Solo admins pueden gestionar usuarios"""
        return user.role == UserRole.ADMIN
    
    @staticmethod
    def can_view_chain_of_custody(user: User) -> bool:
        """Investigadores y admins pueden ver cadena de custodia"""
        return user.role in [UserRole.ADMIN, UserRole.INVESTIGATOR]
