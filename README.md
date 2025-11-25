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

La API estará disponible en: `http://localhost:8000`

## 🧪 Probar el Endpoint

### Método 1: Script de prueba automático

```powershell
# Editar test_endpoint.py y configurar API_KEY y OUTCOME_ID
python test_endpoint.py
```

### Método 2: PowerShell (Invoke-RestMethod)

```powershell
# Probar health check (sin autenticación)
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET

# Probar outcome-summary (con autenticación)
$headers = @{"X-API-Key"="tu_api_key_aqui"}
Invoke-RestMethod -Uri "http://localhost:8000/api/outcome-summary/1" -Method GET -Headers $headers
```

### Método 3: cURL

```bash
# Health check
curl http://localhost:8000/health

# Outcome summary
curl -H "X-API-Key: tu_api_key_aqui" http://localhost:8000/api/outcome-summary/1
```

### Método 4: Navegador / Swagger UI

Abre en tu navegador: `http://localhost:8000/docs`

La documentación interactiva te permite probar todos los endpoints directamente.

## 📊 Respuesta Esperada

Si el endpoint funciona correctamente, devolverá:

```json
{
  "id": 1,
  "so_number": "SO1",
  "description_en": "...",
  "description_es": "...",
  "timecreated": 1234567890,
  "timemodified": 1234567890,
  "indicators": [
    {
      "id": 1,
      "student_outcome_id": 1,
      "indicator_letter": "a",
      "description_en": "...",
      "description_es": "...",
      "levels": [
        {
          "id": 1,
          "indicator_id": 1,
          "title_en": "Excellent",
          "description_en": "...",
          "minscore": 90.0,
          "maxscore": 100.0
        }
      ]
    }
  ]
}
```

## ❌ Posibles Errores

### Error 403 - API Key inválida
```json
{"detail": "API Key inválida o faltante"}
```
**Solución**: Verifica que el header `X-API-Key` tenga el valor correcto configurado en `.env`

### Error 404 - Outcome no encontrado
```json
{"detail": "Outcome no encontrado"}
```
**Solución**: Verifica que el `outcome_id` exista en la tabla `mdl_gradingform_utb_outcomes`

### Error 500 - Error de base de datos
```json
{"detail": "Error al consultar resumen: ..."}
```
**Solución**: 
- Verifica credenciales de BD en `.env`
- Confirma que las tablas existen: `mdl_gradingform_utb_outcomes`, `mdl_gradingform_utb_indicators`, `mdl_gradingform_utb_lvl`
- Revisa logs del servidor MySQL

## 📝 Endpoints Disponibles

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Estado de la API | No |
| GET | `/api/outcomes` | Listar outcomes | Sí |
| GET | `/api/indicators/{outcome_id}` | Indicadores por outcome | Sí |
| GET | `/api/levels/{indicator_id}` | Niveles por indicador | Sí |
| GET | `/api/evaluations/{student_code}` | Evaluaciones por estudiante | Sí |
| GET | `/api/outcome-summary/{outcome_id}` | Resumen completo de outcome | Sí |

## 🐛 Debug

Si el endpoint sigue sin funcionar:

1. **Verificar logs del servidor**
   ```powershell
   # Los logs aparecerán en la consola donde ejecutaste uvicorn
   ```

2. **Probar conexión a BD directamente**
   ```python
   import mysql.connector
   conn = mysql.connector.connect(
       host="tu_host",
       user="tu_usuario",
       password="tu_password",
       database="moodle"
   )
   cursor = conn.cursor()
   cursor.execute("SELECT * FROM mdl_gradingform_utb_outcomes LIMIT 1")
   print(cursor.fetchone())
   ```

3. **Verificar estructura de tablas**
   ```sql
   SHOW TABLES LIKE 'mdl_gradingform_utb_%';
   DESCRIBE mdl_gradingform_utb_outcomes;
   ```

## 📞 Contacto

Si necesitas ayuda adicional, proporciona:
- Logs del servidor (salida de uvicorn)
- Mensaje de error completo
- Versión de Python: `python --version`
- Estado de salud: `curl http://localhost:8000/health`
