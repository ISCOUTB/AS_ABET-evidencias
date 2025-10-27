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


