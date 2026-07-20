import psycopg2
from psycopg2.extras import RealDictCursor
from flask import current_app

def obtener_conexion():
    """Establece una conexión directa con la base de datos de Neon."""
    try:
        # Extraemos la URI de configuración de forma segura desde la app de Flask
        db_url = current_app.config['DATABASE_URL']
        
        conexion = psycopg2.connect(db_url, connect_timeout=10)
        return conexion
    except Exception as e:
        print(f"❌ Error crítico al conectar a Neon DB: {e}")
        return None

def ejecutar_consulta(query, params=None, es_select=True):
    """
    Función unificada para ejecutar comandos SQL.
    Sustituye por completo a las funciones puente provisionales.
    """
    conexion = obtener_conexion()
    if not conexion:
        return None
        
    resultado = None
    try:
        # RealDictCursor permite que Postgres devuelva los datos como diccionarios/JSON nativos
        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            
            if es_select:
                resultado = cursor.fetchall()
            else:
                conexion.commit() # Guarda los cambios de forma permanente (INSERT, UPDATE, DELETE)
                resultado = True
    except Exception as e:
        print(f" Error en la consulta SQL: {e}")
        conexion.rollback() # Revierte cambios si algo falla para no corromper la DB
        if not es_select:
            resultado = False
    finally:
        conexion.close() # Cierra la conexión siempre para liberar memoria RAM
        
    return resultado