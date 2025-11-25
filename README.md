# ABET Evaluation API - Guía de Prueba

## 🔧 Problema Resuelto

El endpoint `/api/outcome-summary/{outcome_id}` tenía un problema de manejo de conexiones a la base de datos que podía causar:
- Fugas de conexiones si ocurría una excepción
- Errores intermitentes bajo carga
- Conexiones no cerradas correctamente

### ✅ Corrección Aplicada
- Añadido bloque `try-finally` para garantizar cierre de conexiones
- Manejo apropiado de excepciones de base de datos
- Inicialización correcta de variables `conn` y `cursor`

## 📋 Pre-requisitos

1. **Python 3.8+** instalado
2. **MySQL/MariaDB** con base de datos Moodle configurada
3. Credenciales de acceso a la base de datos

## 🚀 Instalación y Configuración

### 1. Instalar dependencias

```powershell
# Crear entorno virtual (recomendado)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```powershell
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
notepad .env
```

Configuración necesaria en `.env`:
```env
DB_HOST=tu_host_mysql
DB_PORT=3306
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_NAME=moodle
API_KEY=tu_api_key_opcional
```

### 3. Ejecutar la API

```powershell
# Opción 1: Con recarga automática (desarrollo)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Opción 2: Sin recarga (producción)
python main.py
```
# ABET Evaluation API

Breve descripción
------------------
API en FastAPI que expone endpoints para consultar Student Outcomes y estadísticas de evaluaciones usando tablas del plugin `gradingform_utb` en Moodle.

Contenido del repositorio
-------------------------
- `main.py`: aplicación FastAPI.
- `requirements.txt`: dependencias.
- `README.md`: esta documentación.
- `.env.example`: ejemplo de variables de entorno.

Requisitos
---------
- Python 3.8 o superior
- MySQL/MariaDB con la base de datos Moodle que contiene las tablas `mdl_*` y `mdl_gradingform_utb_*` del plugin

Variables de entorno
--------------------
Copiar `.env.example` a `.env` y completar los valores:

- `DB_HOST` (host de la base de datos)
- `DB_PORT` (puerto, por defecto `3306`)
- `DB_USER` (usuario de BD)
- `DB_PASSWORD` (contraseña de BD)
- `DB_NAME` (nombre de la BD, p. ej. `moodle`)
- `API_KEY` (opcional, para proteger endpoints)
- `SSL_CERTFILE` (opcional, ruta a certificado PEM para HTTPS)
- `SSL_KEYFILE` (opcional, ruta a key PEM para HTTPS)

Instalación
-----------
1. Crear y activar un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:

```bash
cp .env.example .env
# editar .env con tus valores
```

Ejecución
---------
- Desarrollo (recarga automática):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Producción (el bloque `__main__` en `main.py` activa TLS si `SSL_CERTFILE` y `SSL_KEYFILE` están definidas):

```bash
python main.py
```

HTTPS local (opcional)
----------------------
Generar certificado auto-firmado para pruebas:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt -subj "/CN=localhost"
export SSL_CERTFILE="$PWD/server.crt"
export SSL_KEYFILE="$PWD/server.key"
python main.py
```

Endpoints principales
--------------------
- `GET /health` — comprobación de salud (sin API key)
- `GET /api/outcomes` — listar student outcomes; acepta `teacher_id` y `teacher_name` como filtros opcionales
- `GET /api/indicators/{outcome_id}` — indicadores de un outcome
- `GET /api/levels/{indicator_id}` — niveles de desempeño de un indicador
- `GET /api/evaluations/{student_id}` — evaluaciones de un estudiante
- `GET /api/outcome-summary/{outcome_id}` — resumen del outcome
- `GET /api/outcome-report/{outcome_id}` — reporte enriquecido con cursos, profesores y lista de estudiantes calificados (incluye programa si está disponible)

Ejemplos de uso
---------------
```bash
# Health
curl http://localhost:8000/health

# Obtener outcomes
curl -H "X-API-Key: TU_API_KEY" "http://localhost:8000/api/outcomes"

# Obtener reporte enriquecido
curl -H "X-API-Key: TU_API_KEY" "http://localhost:8000/api/outcome-report/1"
```

Despliegue recomendado
----------------------
Usar un reverse-proxy (Nginx, Caddy o Traefik) para gestionar TLS en producción. No se recomienda exponer Uvicorn directamente a Internet sin proxy.

