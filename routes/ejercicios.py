from flask import Blueprint, request, jsonify
from psycopg2.extras import RealDictCursor
from database import ejecutar_consulta, obtener_conexion

ejercicios_bp = Blueprint('ejercicios', __name__)

TABLA_EJERCICIOS = """
    CREATE TABLE IF NOT EXISTS exercises (
        id_exercise SERIAL PRIMARY KEY,
        id_chapter INTEGER NOT NULL REFERENCES chapters(id_chapter) ON DELETE CASCADE,
        question TEXT NOT NULL,
        expected_solution TEXT NOT NULL
    );
"""

# Obtener ejercicios de un capítulo
@ejercicios_bp.route('/capitulos/<int:chapter_id>/ejercicios', methods=['GET'])
def get_ejercicios(chapter_id):
    conn = obtener_conexion()
    if not conn:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(TABLA_EJERCICIOS)
            cur.execute(
                "SELECT id_exercise, id_chapter, question FROM exercises WHERE id_chapter = %s ORDER BY id_exercise;",
                (chapter_id,)
            )
            ejercicios = cur.fetchall()
            conn.commit()
        return jsonify({"ejercicios": ejercicios}), 200
    except Exception as e:
        conn.rollback()
        print(f"Error en get_ejercicios: {e}")
        return jsonify({"error": "Error interno"}), 500
    finally:
        conn.close()

# Crear un ejercicio
@ejercicios_bp.route('/capitulos/<int:chapter_id>/ejercicios', methods=['POST'])
def crear_ejercicio(chapter_id):
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "Petición JSON inválida"}), 400

    id_user = datos.get('id_user')
    question = datos.get('question', '').strip()
    expected_solution = datos.get('expected_solution', '').strip()

    if not id_user:
        return jsonify({"error": "Debes iniciar sesión"}), 401
    if not question or not expected_solution:
        return jsonify({"error": "question y expected_solution son obligatorios"}), 400

    query = """
        SELECT c.id_user AS course_owner
        FROM chapters ch
        JOIN courses c ON ch.id_course = c.id_course
        WHERE ch.id_chapter = %s
    """
    result = ejecutar_consulta(query, (chapter_id,), es_select=True)
    if not result:
        return jsonify({"error": "Capítulo no encontrado"}), 404
    if result[0]['course_owner'] != id_user:
        return jsonify({"error": "No tienes permiso"}), 403

    conn = obtener_conexion()
    if not conn:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(TABLA_EJERCICIOS)
            cur.execute(
                "INSERT INTO exercises (id_chapter, question, expected_solution) VALUES (%s, %s, %s) RETURNING id_exercise, id_chapter, question;",
                (chapter_id, question, expected_solution)
            )
            ejercicio = cur.fetchone()
            conn.commit()
        return jsonify({"mensaje": "Ejercicio creado", "ejercicio": ejercicio}), 201
    except Exception as e:
        conn.rollback()
        print(f"Error al crear ejercicio: {e}")
        return jsonify({"error": "Error interno"}), 500
    finally:
        conn.close()

# Actualizar un ejercicio
@ejercicios_bp.route('/ejercicios/<int:exercise_id>', methods=['PUT'])
def actualizar_ejercicio(exercise_id):
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "Petición JSON inválida"}), 400

    id_user = datos.get('id_user')
    question = datos.get('question', '').strip()
    expected_solution = datos.get('expected_solution', '').strip()

    if not id_user:
        return jsonify({"error": "Debes iniciar sesión"}), 401
    if not question or not expected_solution:
        return jsonify({"error": "question y expected_solution son obligatorios"}), 400

    conn = obtener_conexion()
    if not conn:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT c.id_user AS course_owner
                FROM exercises e
                JOIN chapters ch ON e.id_chapter = ch.id_chapter
                JOIN courses c ON ch.id_course = c.id_course
                WHERE e.id_exercise = %s
            """, (exercise_id,))
            result = cur.fetchone()
            if not result:
                return jsonify({"error": "Ejercicio no encontrado"}), 404
            if result['course_owner'] != id_user:
                return jsonify({"error": "No tienes permiso"}), 403

            cur.execute(
                "UPDATE exercises SET question = %s, expected_solution = %s WHERE id_exercise = %s RETURNING id_exercise, id_chapter, question;",
                (question, expected_solution, exercise_id)
            )
            ejercicio = cur.fetchone()
            conn.commit()
        return jsonify({"mensaje": "Ejercicio actualizado", "ejercicio": ejercicio}), 200
    except Exception as e:
        conn.rollback()
        print(f"Error al actualizar ejercicio: {e}")
        return jsonify({"error": "Error interno"}), 500
    finally:
        conn.close()

# Eliminar un ejercicio
@ejercicios_bp.route('/ejercicios/<int:exercise_id>', methods=['DELETE'])
def eliminar_ejercicio(exercise_id):
    id_user = request.args.get('id_user')
    if not id_user:
        return jsonify({"error": "Debes iniciar sesión"}), 401

    conn = obtener_conexion()
    if not conn:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT c.id_user AS course_owner
                FROM exercises e
                JOIN chapters ch ON e.id_chapter = ch.id_chapter
                JOIN courses c ON ch.id_course = c.id_course
                WHERE e.id_exercise = %s
            """, (exercise_id,))
            result = cur.fetchone()
            if not result:
                return jsonify({"error": "Ejercicio no encontrado"}), 404
            if result['course_owner'] != int(id_user):
                return jsonify({"error": "No tienes permiso"}), 403

            cur.execute("DELETE FROM exercises WHERE id_exercise = %s;", (exercise_id,))
            conn.commit()
        return jsonify({"mensaje": "Ejercicio eliminado"}), 200
    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar ejercicio: {e}")
        return jsonify({"error": "Error interno"}), 500
    finally:
        conn.close()

# Validar solución
@ejercicios_bp.route('/ejercicios/<int:exercise_id>/validar', methods=['POST'])
def validar_ejercicio(exercise_id):
    datos = request.get_json()
    if not datos or 'user_solution' not in datos:
        return jsonify({"error": "Debes enviar user_solution"}), 400

    user_solution = datos['user_solution'].strip()

    result = ejecutar_consulta(
        "SELECT id_exercise, question, expected_solution FROM exercises WHERE id_exercise = %s;",
        (exercise_id,), es_select=True
    )
    if not result:
        return jsonify({"error": "Ejercicio no encontrado"}), 404

    expected = result[0]['expected_solution'].strip()
    correct = user_solution.lower() == expected.lower()

    return jsonify({
        "correct": correct,
        "message": "¡Correcto!" if correct else "Incorrecto. Intenta de nuevo."
    }), 200
