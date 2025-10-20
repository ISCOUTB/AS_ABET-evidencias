from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import mysql.connector
from mysql.connector import Error
from pydantic import BaseModel
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Moodle Grading API",
    description="API para conectar Oracle APEX con base de datos Moodle",
    version="1.0.0"
)

# Configuración de CORS para permitir acceso desde Oracle APEX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica el dominio de Oracle APEX
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'your-azure-docker-host.com'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'moodle'),
    'password': os.getenv('DB_PASSWORD', 'your-password'),
    'database': os.getenv('DB_NAME', 'moodle')
}

# Modelos Pydantic
class StudentOutcome(BaseModel):
    id: int
    course: Optional[int]
    name: str
    description: Optional[str]
    descriptionformat: Optional[int]
    sortorder: Optional[int]
    timecreated: Optional[int]
    timemodified: Optional[int]

class Indicator(BaseModel):
    id: int
    outcomeid: int
    name: str
    description: Optional[str]
    descriptionformat: Optional[int]
    sortorder: Optional[int]
    timecreated: Optional[int]
    timemodified: Optional[int]

class PerformanceLevel(BaseModel):
    id: int
    indicatorid: int
    level: int
    name: str
    description: Optional[str]
    score: Optional[float]
    timecreated: Optional[int]
    timemodified: Optional[int]

class Evaluation(BaseModel):
    id: int
    instanceid: int
    studentid: int
    indicatorid: int
    levelid: int
    remark: Optional[str]
    evaluatorid: Optional[int]
    timecreated: Optional[int]
    timemodified: Optional[int]

# Función para obtener conexión a la base de datos
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión a la base de datos: {str(e)}")

# Función para cerrar conexión
def close_db_connection(connection, cursor):
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()

@app.get("/")
def read_root():
    return {
        "message": "API de Moodle Grading Forms",
        "version": "1.0.0",
        "endpoints": {
            "outcomes": "/api/outcomes",
            "indicators": "/api/indicators",
            "levels": "/api/levels",
            "evaluations": "/api/evaluations"
        }
    }

@app.get("/health")
def health_check():
    """Endpoint para verificar el estado de la API y conexión a BD"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        close_db_connection(connection, cursor)
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

# ==================== STUDENT OUTCOMES ====================
@app.get("/api/outcomes", response_model=List[StudentOutcome])
def get_outcomes(
    course_id: Optional[int] = Query(None, description="Filtrar por ID de curso"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Obtener todos los Student Outcomes"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM mdl_gradingform_utb_outcomes"
        params = []
        
        if course_id is not None:
            query += " WHERE course = %s"
            params.append(course_id)
        
        query += " ORDER BY sortorder, id LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return results
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar outcomes: {str(e)}")
    finally:
        close_db_connection(connection, cursor)

@app.get("/api/outcomes/{outcome_id}", response_model=StudentOutcome)
def get_outcome_by_id(outcome_id: int):
    """Obtener un Student Outcome específico por ID"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM mdl_gradingform_utb_outcomes WHERE id = %s"
        cursor.execute(query, (outcome_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Outcome no encontrado")
        
        return result
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar outcome: {str(e)}")
    finally:
        close_db_connection(connection, cursor)

# ==================== INDICATORS ====================
@app.get("/api/indicators", response_model=List[Indicator])
def get_indicators(
    outcome_id: Optional[int] = Query(None, description="Filtrar por ID de outcome"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Obtener todos los indicadores de evaluación"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM mdl_gradingform_utb_indicators"
        params = []
        
        if outcome_id is not None:
            query += " WHERE outcomeid = %s"
            params.append(outcome_id)
        
        query += " ORDER BY sortorder, id LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return results
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar indicators: {str(e)}")
    finally:
        close_db_connection(connection, cursor)

@app.get("/api/indicators/{indicator_id}", response_model=Indicator)
def get_indicator_by_id(indicator_id: int):
    """Obtener un indicador específico por ID"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM mdl_gradingform_utb_indicators WHERE id = %s"
        cursor.execute(query, (indicator_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Indicador no encontrado")
        
        return result
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar indicador: {str(e)}")
    finally:
        close_db_connection(connection, cursor)

# ==================== PERFORMANCE LEVELS ====================
@app.get("/api/levels", response_model=List[PerformanceLevel])
def get_levels(
    indicator_id: Optional[int] = Query(None, description="Filtrar por ID de indicador"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Obtener todos los niveles de desempeño"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM mdl_gradingform_utb_lvl"
        params = []
        
        if indicator_id is not None:
            query += " WHERE indicatorid = %s"
            params.append(indicator_id)
        
        query += " ORDER BY level, id LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return results
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar levels: {str(e)}")
    finally:
        close_db_connection(connection, cursor)

@app.get("/api/levels/{level_id}", response_model=PerformanceLevel)
def get_level_by_id(level_id: int):
    """Obtener un nivel de desempeño específico por ID"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM mdl_gradingform_utb_lvl WHERE id = %s"
        cursor.execute(query, (level_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Nivel no encontrado")
        
        return result
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar nivel: {str(e)}")
    finally:
        close_db_connection(connection, cursor)

# ==================== EVALUATIONS ====================
@app.get("/api/evaluations", response_model=List[Evaluation])
def get_evaluations(
    student_id: Optional[int] = Query(None, description="Filtrar por ID de estudiante"),
    indicator_id: Optional[int] = Query(None, description="Filtrar por ID de indicador"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Obtener todas las evaluaciones realizadas"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM mdl_gradingform_utb_evaluations WHERE 1=1"
        params = []
        
        if student_id is not None:
            query += " AND studentid = %s"
            params.append(student_id)
        
        if indicator_id is not None:
            query += " AND indicatorid = %s"
            params.append(indicator_id)
        
        query += " ORDER BY timecreated DESC, id LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return results
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar evaluations: {str(e)}")
    finally:
        close_db_connection(connection, cursor)

@app.get("/api/evaluations/{evaluation_id}", response_model=Evaluation)
def get_evaluation_by_id(evaluation_id: int):
    """Obtener una evaluación específica por ID"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM mdl_gradingform_utb_evaluations WHERE id = %s"
        cursor.execute(query, (evaluation_id,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Evaluación no encontrada")
        
        return result
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar evaluación: {str(e)}")
    finally:
        close_db_connection(connection, cursor)

# ==================== ENDPOINTS COMBINADOS PARA ANÁLISIS ====================
@app.get("/api/student-performance/{student_id}")
def get_student_performance(student_id: int):
    """Obtener el desempeño completo de un estudiante con detalles de outcomes, indicators y levels"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT 
            e.id as evaluation_id,
            e.studentid,
            e.timecreated,
            e.remark,
            o.id as outcome_id,
            o.name as outcome_name,
            i.id as indicator_id,
            i.name as indicator_name,
            l.id as level_id,
            l.level as level_number,
            l.name as level_name,
            l.score
        FROM mdl_gradingform_utb_evaluations e
        INNER JOIN mdl_gradingform_utb_indicators i ON e.indicatorid = i.id
        INNER JOIN mdl_gradingform_utb_outcomes o ON i.outcomeid = o.id
        INNER JOIN mdl_gradingform_utb_lvl l ON e.levelid = l.id
        WHERE e.studentid = %s
        ORDER BY e.timecreated DESC
        """
        
        cursor.execute(query, (student_id,))
        results = cursor.fetchall()
        
        if not results:
            raise HTTPException(status_code=404, detail="No se encontraron evaluaciones para este estudiante")
        
        return {
            "student_id": student_id,
            "total_evaluations": len(results),
            "evaluations": results
        }
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar desempeño del estudiante: {str(e)}")
    finally:
        close_db_connection(connection, cursor)

@app.get("/api/outcome-summary/{outcome_id}")
def get_outcome_summary(outcome_id: int):
    """Obtener resumen completo de un outcome con sus indicadores y niveles"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Obtener outcome
        cursor.execute("SELECT * FROM mdl_gradingform_utb_outcomes WHERE id = %s", (outcome_id,))
        outcome = cursor.fetchone()
        
        if not outcome:
            raise HTTPException(status_code=404, detail="Outcome no encontrado")
        
        # Obtener indicadores del outcome
        cursor.execute(
            "SELECT * FROM mdl_gradingform_utb_indicators WHERE outcomeid = %s ORDER BY sortorder",
            (outcome_id,)
        )
        indicators = cursor.fetchall()
        
        # Para cada indicador, obtener sus niveles
        for indicator in indicators:
            cursor.execute(
                "SELECT * FROM mdl_gradingform_utb_lvl WHERE indicatorid = %s ORDER BY level",
                (indicator['id'],)
            )
            indicator['levels'] = cursor.fetchall()
        
        outcome['indicators'] = indicators
        
        return outcome
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar resumen del outcome: {str(e)}")
    finally:
        close_db_connection(connection, cursor)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
