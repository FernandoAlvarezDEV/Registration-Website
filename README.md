# ENO Portal — Formulario de Inscripción 2026

Portal web de inscripción para el evento Onda Fest.

## Estructura del Proyecto

```
Registration-Website/
├── frontend/          # HTML, CSS (Tailwind CDN), JavaScript
│   ├── Index.html     # Formulario principal de registro
│   ├── login.html     # Inicio de sesión
│   ├── dashboard.html # Dashboard del participante
│   ├── admin.html     # Panel de administración
│   ├── success.html   # Confirmación de registro
│   └── js/            # Scripts JS por página
└── server/            # Backend FastAPI + PostgreSQL
    ├── main.py        # Endpoints de la API
    ├── models.py      # Modelos SQLAlchemy + Pydantic
    ├── database.py    # Conexión a PostgreSQL
    ├── config.py      # Variables de entorno
    └── requirements.txt
```

## Despliegue en Render

### 1. Base de datos (Supabase)
1. Crea un proyecto en [supabase.com](https://supabase.com)
2. Ve a **Project Settings → Database**
3. Copia los datos de conexión

### 2. Backend en Render
1. Sube el repositorio a GitHub
2. Ve a [render.com](https://render.com) → **New → Web Service**
3. Conecta el repositorio de GitHub
4. Configura:
   - **Root Directory:** server
   - **Build Command:** pip install -r requirements.txt
   - **Start Command:** uvicorn main:app --host 0.0.0.0 --port \
5. Agrega las variables de entorno (ver server/.env.example)

### 3. Frontend en Render
1. **New → Static Site**
2. Conecta el mismo repositorio
3. Configura:
   - **Root Directory:** rontend
   - **Publish Directory:** .

### Variables de Entorno Requeridas
Consulta server/.env.example para la lista completa.

## Desarrollo Local

```bash
# 1. Instalar dependencias del backend
cd server
pip install -r requirements.txt

# 2. Copiar y completar el archivo de entorno
cp .env.example .env
# Edita .env con tus credenciales de Supabase

# 3. Iniciar el servidor
uvicorn main:app --reload --port 8000
```

Abrir rontend/Index.html en un Live Server (VS Code) en el puerto 5500.
