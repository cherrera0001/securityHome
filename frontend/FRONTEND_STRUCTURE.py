"""
ForensicVideo AI Platform - Dashboard Principal
Next.js 14 con Tailwind CSS

Este archivo documenta la estructura del frontend:

/app
  /dashboard
    page.tsx - Dashboard principal con upload de videos
    /videos
      page.tsx - Lista de videos
      [id]/page.tsx - Detalle de video
    /faces
      page.tsx - Galería de rostros detectados
    /heatmaps
      page.tsx - Visualización de heatmaps de movimiento
    /reports
      page.tsx - Reportes periciales
    /alerts
      page.tsx - Alertas del sistema
  /auth
    /login/page.tsx - Login
    /register/page.tsx - Registro

/components
  VideoUploader.tsx - Componente de upload con drag & drop
  FaceGallery.tsx - Galería de rostros con búsqueda
  HeatmapViewer.tsx - Visualizador de heatmaps
  VideoPlayer.tsx - Reproductor de video con timeline
  AlertBanner.tsx - Banner de alertas
  ReportGenerator.tsx - Generador de reportes

/lib
  api.ts - Cliente API (Axios)
  auth.ts - Gestión de autenticación
  store.ts - Estado global (Zustand)

Características principales:
1. Upload de videos con drag & drop
2. Visualización de progreso de procesamiento en tiempo real
3. Galería de rostros con búsqueda de similitud
4. Heatmaps de movimiento interactivos
5. Timeline de video con marcadores de detección
6. Sistema de alertas en tiempo real
7. Generación y descarga de reportes periciales
8. Dashboard responsive con Tailwind CSS
"""

# Placeholder para documentación del frontend
# El frontend completo requeriría archivos adicionales que se implementarían en:
# - app/dashboard/page.tsx
# - components/VideoUploader.tsx
# - components/FaceGallery.tsx
# - components/HeatmapViewer.tsx
# - lib/api.ts
# - lib/auth.ts

FRONTEND_STRUCTURE = """
frontend/
├── app/
│   ├── layout.tsx (Root layout con navbar)
│   ├── page.tsx (Landing page)
│   ├── dashboard/
│   │   ├── page.tsx (Dashboard principal)
│   │   ├── videos/
│   │   │   ├── page.tsx (Lista de videos)
│   │   │   └── [id]/page.tsx (Detalle + player)
│   │   ├── faces/
│   │   │   └── page.tsx (Galería de rostros)
│   │   ├── heatmaps/
│   │   │   └── page.tsx (Visualización de heatmaps)
│   │   ├── reports/
│   │   │   └── page.tsx (Reportes periciales)
│   │   └── alerts/
│   │       └── page.tsx (Sistema de alertas)
│   └── auth/
│       ├── login/page.tsx
│       └── register/page.tsx
├── components/
│   ├── VideoUploader.tsx (Drag & drop upload)
│   ├── VideoPlayer.tsx (Player con timeline)
│   ├── FaceGallery.tsx (Grid de rostros)
│   ├── FaceCard.tsx (Tarjeta individual de rostro)
│   ├── HeatmapViewer.tsx (Canvas de heatmap)
│   ├── ProcessingStatus.tsx (Progress bar)
│   ├── AlertBanner.tsx (Notificaciones)
│   ├── ReportGenerator.tsx (Formulario de reportes)
│   ├── Navbar.tsx (Navegación principal)
│   └── Sidebar.tsx (Sidebar del dashboard)
├── lib/
│   ├── api.ts (Axios client)
│   ├── auth.ts (JWT handling)
│   ├── store.ts (Zustand store)
│   └── utils.ts (Utilidades)
├── styles/
│   └── globals.css
├── public/
│   └── images/
├── package.json
├── next.config.js
├── tailwind.config.js
└── tsconfig.json
"""
