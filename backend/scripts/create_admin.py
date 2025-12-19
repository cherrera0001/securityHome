"""
Script para crear usuario administrador inicial
"""
import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

from app.models.database import SessionLocal, init_db
from app.models.models import User, UserRole
from app.core.auth import AuthService
import uuid


def create_admin_user():
    """Crear usuario administrador inicial"""
    # Inicializar DB
    init_db()
    
    db = SessionLocal()
    
    try:
        # Verificar si ya existe un admin
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        
        if existing_admin:
            print(f"⚠️  Ya existe un usuario administrador: {existing_admin.email}")
            return
        
        # Crear admin
        admin = User(
            email="admin@forensicvideo.ai",
            username="admin",
            hashed_password=AuthService.get_password_hash("admin123"),  # CAMBIAR EN PRODUCCIÓN
            full_name="System Administrator",
            role=UserRole.ADMIN,
            organization="ForensicVideo AI",
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("✅ Usuario administrador creado exitosamente")
        print(f"   Email: {admin.email}")
        print(f"   Password: admin123")
        print(f"   ⚠️  CAMBIAR PASSWORD EN PRODUCCIÓN")
        
    except Exception as e:
        print(f"❌ Error creando administrador: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
