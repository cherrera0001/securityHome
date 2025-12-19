#!/bin/bash

# 🚀 Script de Inicio Rápido - ForensicVideo AI Platform
# Este script ayuda a iniciar el proyecto rápidamente

set -e  # Salir si hay error

echo "🔍 ForensicVideo AI - Inicio Rápido"
echo "======================================"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Verificar entorno virtual
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Entorno virtual no encontrado. Creando...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✅ Entorno virtual creado${NC}"
fi

# 2. Activar entorno virtual
echo -e "${GREEN}🐍 Activando entorno virtual...${NC}"
source .venv/bin/activate

# 3. Verificar dependencias básicas
echo -e "${GREEN}📦 Verificando dependencias...${NC}"
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Instalando dependencias básicas...${NC}"
    pip install -q fastapi uvicorn sqlalchemy psycopg2-binary python-jose passlib pydantic-settings pillow pgvector celery redis python-multipart boto3 pydantic python-dotenv
    echo -e "${GREEN}✅ Dependencias instaladas${NC}"
else
    echo -e "${GREEN}✅ Dependencias ya instaladas${NC}"
fi

# 4. Verificar archivo .env
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
    if [ -f "backend/.env.example" ]; then
        echo -e "${YELLOW}📝 Copiando .env.example a .env...${NC}"
        cp backend/.env.example backend/.env
        echo -e "${YELLOW}⚠️  Por favor edita backend/.env con tus credenciales${NC}"
    else
        echo -e "${RED}❌ backend/.env.example no existe${NC}"
    fi
else
    echo -e "${GREEN}✅ Archivo .env existe${NC}"
fi

# 5. Verificar directorios
echo -e "${GREEN}📁 Verificando estructura de directorios...${NC}"
mkdir -p backend/models storage/{videos,faces,thumbnails,heatmaps}
echo -e "${GREEN}✅ Directorios creados${NC}"

# 6. Verificar modelos de IA (opcional)
echo ""
echo -e "${YELLOW}🤖 Modelos de IA (Opcional)${NC}"
echo "Los modelos de IA son necesarios para análisis forense completo:"
echo ""

if [ -f "backend/models/yolov10n.pt" ]; then
    echo -e "  ${GREEN}✅ YOLOv10 instalado${NC}"
else
    echo -e "  ${YELLOW}⚠️  YOLOv10 NO instalado${NC}"
    echo "     Descargar: wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov10n.pt -O backend/models/yolov10n.pt"
fi

if [ -f "backend/models/RealESRGAN_x4plus.pth" ]; then
    echo -e "  ${GREEN}✅ Real-ESRGAN instalado${NC}"
else
    echo -e "  ${YELLOW}⚠️  Real-ESRGAN NO instalado${NC}"
    echo "     Descargar: wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth -O backend/models/RealESRGAN_x4plus.pth"
fi

echo ""
echo "======================================"
echo -e "${GREEN}✨ Entorno configurado correctamente${NC}"
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "1. Configurar credenciales en backend/.env"
echo "2. Iniciar servicios con Docker Compose:"
echo "   ${YELLOW}docker-compose up -d postgres redis${NC}"
echo ""
echo "3. Iniciar API en modo desarrollo:"
echo "   ${YELLOW}cd backend && uvicorn main:app --reload${NC}"
echo ""
echo "4. Ver documentación de API:"
echo "   ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo "5. Iniciar worker de Celery (opcional):"
echo "   ${YELLOW}cd backend && celery -A app.workers.celery_app worker --loglevel=info${NC}"
echo ""
echo "======================================"
