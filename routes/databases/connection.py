import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config

def conectar_db():
    """Establece y retorna una conexión activa con la base de datos de Neon."""
    try:
        # Intenta abrir el canal de comunicación usando la URL de config.py
        conexion = psycopg2.connect(Config.DATABASE_URL)
        return conexion
    except Exception as e:
        print(f" Error crítico al conectar a Neon PostgreSQL: {e}")
        return None

def ejecutar_consulta(query, params=None, es_select=True):
  
    conexion = conectar_db()
    if not conexion:
        return None
        
    resultado = None
    try:
        # RealDictCursor transforma las filas en diccionarios de Python
        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            
            if es_select:
                resultado = cursor.fetchall()
            else:
                conexion.commit() # Guarda los cambios de forma permanente (INSERT, UPDATE)
                resultado = True
    except Exception as e:
        print(f"⚠️ Error al ejecutar la consulta SQL: {e}")
        if not es_select:
            conexion.rollback() # Revierte los cambios si la transacción falló
    finally:
        if conexion:
            conexion.close() # Cierra la conexión de red para liberar el pool de Neon
        
    return resultado