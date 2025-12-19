"""
Configuración de base de datos PostgreSQL con soporte pgvector
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Motor de base de datos con pool de conexiones
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializar base de datos y extensiones"""
    from sqlalchemy import text
    
    # Crear extensión pgvector para búsqueda de embeddings
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
