# API de Moodle Grading Forms para Oracle APEX

Esta API REST conecta Oracle APEX con la base de datos de Moodle (corriendo en Docker en Azure) para acceder a las tablas de evaluación de Student Outcomes.

## Tablas de Base de Datos

- `mdl_gradingform_utb_outcomes` - Student Outcomes
- `mdl_gradingform_utb_indicators` - Indicadores de evaluación de cada SO
- `mdl_gradingform_utb_lvl` - Niveles de desempeño de cada indicador por cada SO
- `mdl_gradingform_utb_evaluations` - Evaluaciones realizadas

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Instalar dependencias:
   ```powershell
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:
   - Copiar `.env.example` a `.env`
   - Actualizar con las credenciales de tu base de datos Moodle en Azure

5. Ejecutar la API:
   ```powershell
   python main.py
   ```
   o
   ```powershell
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Endpoints Disponibles

### Health Check
- `GET /health` - Verificar estado de la API y conexión a BD

### Student Outcomes
- `GET /api/outcomes` - Obtener todos los outcomes
- `GET /api/outcomes/{outcome_id}` - Obtener un outcome específico
- Query params: `course_id`, `limit`, `offset`

### Indicadores
- `GET /api/indicators` - Obtener todos los indicadores
- `GET /api/indicators/{indicator_id}` - Obtener un indicador específico
- Query params: `outcome_id`, `limit`, `offset`

### Niveles de Desempeño
- `GET /api/levels` - Obtener todos los niveles
- `GET /api/levels/{level_id}` - Obtener un nivel específico
- Query params: `indicator_id`, `limit`, `offset`

### Evaluaciones
- `GET /api/evaluations` - Obtener todas las evaluaciones
- `GET /api/evaluations/{evaluation_id}` - Obtener una evaluación específica
- Query params: `student_id`, `indicator_id`, `limit`, `offset`

### Análisis Combinados
- `GET /api/student-performance/{student_id}` - Desempeño completo de un estudiante
- `GET /api/outcome-summary/{outcome_id}` - Resumen completo de un outcome con indicadores y niveles

## Documentación Interactiva

Una vez ejecutada la API, acceder a:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Integración con Oracle APEX

### Configuración de Web Source en Oracle APEX

1. En Oracle APEX, ir a **Shared Components** > **Web Source Modules**
2. Crear nuevo módulo con:
   - **Base URL**: `http://your-api-host:8000/api`
   - **Authentication**: None (o configurar según necesidad)

3. Ejemplos de endpoints para usar en APEX:
   ```
   /outcomes
   /indicators?outcome_id=1
   /evaluations?student_id=123
   /student-performance/123
   ```

### Ejemplo de REST Data Source en APEX

```sql
-- En APEX, crear REST Data Source:
-- URL: http://your-api-host:8000/api/outcomes
-- Método: GET
-- Autenticación: No Auth (o configurar token si implementas seguridad)
```

### Ejemplo de uso en APEX Interactive Grid

```sql
SELECT 
    id,
    name,
    description,
    course
FROM (
    SELECT * FROM TABLE(
        APEX_WEB_SERVICE.MAKE_REST_REQUEST(
            p_url => 'http://your-api-host:8000/api/outcomes',
            p_http_method => 'GET'
        )
    )
)
```

## Consideraciones de Seguridad

Para producción, considera:

1. **Autenticación**: Implementar JWT o API Keys
2. **HTTPS**: Usar certificados SSL/TLS
3. **CORS**: Restringir origins permitidos
4. **Rate Limiting**: Limitar número de peticiones
5. **Validación**: Validar todos los inputs
6. **Secrets**: Usar Azure Key Vault para credenciales

## Despliegue en Azure

### Opción 1: Azure Container Instances
```powershell
# Crear Dockerfile y desplegar
az container create --resource-group myResourceGroup --name moodle-api --image your-image --dns-name-label moodle-api --ports 8000
```

### Opción 2: Azure App Service
```powershell
# Desplegar directamente a App Service
az webapp up --name moodle-api --runtime PYTHON:3.11
```

## Troubleshooting

### Error de conexión a la base de datos
- Verificar que el contenedor Docker de Moodle esté corriendo
- Verificar firewall rules en Azure
- Confirmar credenciales en archivo `.env`

### CORS errors desde Oracle APEX
- Actualizar `allow_origins` en `main.py` con el dominio de APEX
- Verificar que Oracle APEX permita conexiones HTTP/HTTPS externas

## Estructura del Proyecto

```
moodle-api/
├── main.py                 # Aplicación principal FastAPI
├── requirements.txt        # Dependencias Python
├── .env                   # Variables de entorno (no incluir en git)
├── .env.example           # Ejemplo de variables de entorno
└── README.md              # Esta documentación
```

## Contacto y Soporte

Para preguntas o soporte, contactar al equipo de desarrollo.
