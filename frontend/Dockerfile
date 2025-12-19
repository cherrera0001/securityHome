FROM node:20-alpine

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar código
COPY . .

# Build (en producción)
# RUN npm run build

# Exponer puerto
EXPOSE 3000

# Comando
CMD ["npm", "run", "dev"]
