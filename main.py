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

# ==================== MODELOS PYDANTIC ====================

class OutcomeFull(BaseModel):
    id: int
    so_number: str
    title_en: str
    title_es: str
    description_en: str
    description_es: str
    sortorder: int
    timecreated: int
    timemodified: int

class IndicatorFull(BaseModel):
    id: int
    student_outcome_id: int
    indicator_letter: str
    description_en: str
    description_es: str
    timecreated: int
    timemodified: int

class LevelFull(BaseModel):
    id: int
    indicator_id: int
    title_en: str
    title_es: str
    description_en: str
    description_es: str
    minscore: float
    maxscore: float
    sortorder: int
    timecreated: int
    timemodified: int

class EvaluationFull(BaseModel):
    id: int
    instanceid: int
    studentid: int
    courseid: int
    activityid: int
    activityname: str
    student_outcome_id: int
    indicator_id: int
    performance_level_id: int
    score: float
    feedback: str | None = None
    timecreated: int
    timemodified: int

# ==================== FUNCIONES DE BASE DE DATOS ====================

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión a la base de datos: {str(e)}")

def close_db_connection(connection, cursor):
    """Cerrar conexión a la base de datos"""
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()

# ==================== ENDPOINTS PRINCIPALES ====================

@app.get("/")
def read_root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "API de Moodle Grading Forms",
        "version": "1.0.0",
        "endpoints": {
            "outcomes": "/api/outcomes",
            "indicators": "/api/indicators",
            "levels": "/api/levels",
            "evaluations": "/api/evaluations",
            "health": "/health"
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

# ==================== ENDPOINTS DE DATOS ====================

@app.get("/api/outcomes", response_model=list[OutcomeFull])
def get_all_outcomes():
    """Obtener todos los Student Outcomes"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT id, so_number, title_en, title_es, description_en, description_es, sortorder, timecreated, timemodified FROM mdl_gradingform_utb_outcomes"
        cursor.execute(query)
        results = cursor.fetchall()
        outcomes = [OutcomeFull(**row) for row in results]
        return outcomes
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar outcomes: {str(e)}")
    finally:
        close_db_connection(connection, cursor)

@app.get("/api/indicators", response_model=list[IndicatorFull])
def get_all_indicators():
    """Obtener todos los Indicators"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT id, student_outcome_id, indicator_letter, description_en, description_es, timecreated, timemodified FROM mdl_gradingform_utb_indicators"
        cursor.execute(query)
        results = cursor.fetchall()
        indicators = [IndicatorFull(**row) for row in results]
        return indicators
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar indicators: {str(e)}")
    finally:
        close_db_connection(connection, cursor)

@app.get("/api/levels", response_model=list[LevelFull])
def get_all_levels():
    """Obtener todos los Performance Levels"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT id, indicator_id, title_en, title_es, description_en, description_es, minscore, maxscore, sortorder, timecreated, timemodified FROM mdl_gradingform_utb_lvl"
        cursor.execute(query)
        results = cursor.fetchall()
        levels = [LevelFull(**row) for row in results]
        return levels
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar levels: {str(e)}")
    finally:
        close_db_connection(connection, cursor)

@app.get("/api/evaluations", response_model=list[EvaluationFull])
def get_all_evaluations():
    """Obtener todas las Evaluations"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT id, instanceid, studentid, courseid, activityid, activityname, student_outcome_id, indicator_id, performance_level_id, score, feedback, timecreated, timemodified FROM mdl_gradingform_utb_evaluations"
        cursor.execute(query)
        results = cursor.fetchall()
        evaluations = [EvaluationFull(**row) for row in results]
        return evaluations
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar evaluaciones: {str(e)}")
    finally:
        close_db_connection(connection, cursor)

# ==================== ENDPOINTS ADICIONALES ====================

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
            e.score,
            e.feedback,
            e.timecreated,
            o.id as outcome_id,
            o.so_number,
            o.title_en as outcome_name,
            i.id as indicator_id,
            i.indicator_letter,
            l.id as level_id,
            l.title_en as level_name,
            l.minscore,
            l.maxscore
        FROM mdl_gradingform_utb_evaluations e
        INNER JOIN mdl_gradingform_utb_indicators i ON e.indicator_id = i.id
        INNER JOIN mdl_gradingform_utb_outcomes o ON i.student_outcome_id = o.id
        INNER JOIN mdl_gradingform_utb_lvl l ON e.performance_level_id = l.id
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
            "SELECT * FROM mdl_gradingform_utb_indicators WHERE student_outcome_id = %s ORDER BY id",
            (outcome_id,)
        )
        indicators = cursor.fetchall()
        
        # Para cada indicador, obtener sus niveles
        for indicator in indicators:
            cursor.execute(
                "SELECT * FROM mdl_gradingform_utb_lvl WHERE indicator_id = %s ORDER BY sortorder",
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
