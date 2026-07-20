from flask import Blueprint, request, jsonify
from psycopg2.extras import RealDictCursor
from database import ejecutar_consulta

cursos_bp = Blueprint('cursos', __name__)

# =========================================================================
# ENDPOINT 1: LISTAR TODOS LOS CURSOS (O FILTRARLOS POR LENGUAJE)
# =========================================================================
@cursos_bp.route('/cursos', methods=['GET'])
def get_cursos():
    lenguaje = request.args.get('lenguaje')
    q = request.args.get('q', '').strip()
    propios = request.args.get('propios')
    id_user = request.args.get('id_user')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 12, type=int)

    condiciones = []
    params = []

    if lenguaje:
        condiciones.append("language = %s")
        params.append(lenguaje)

    if q:
        condiciones.append("(title ILIKE %s OR description ILIKE %s)")
        params.extend([f'%{q}%', f'%{q}%'])

    if propios == '1' and id_user:
        condiciones.append("id_user = %s")
        params.append(int(id_user))

    where_clause = ""
    if condiciones:
        where_clause = " WHERE " + " AND ".join(condiciones)

    # Total de cursos (sin paginación)
    query_count = f"SELECT COUNT(*) AS total FROM courses{where_clause};"
    total_result = ejecutar_consulta(query_count, params, es_select=True)
    total = total_result[0]['total'] if total_result else 0

    # Página actual con límites seguros
    limit = min(max(limit, 1), 50)
    page = max(page, 1)
    offset = (page - 1) * limit

    query = f"""
        SELECT id_course, id_user, title, date_created, course_image, language, module_name, level, description 
        FROM courses{where_clause}
        ORDER BY date_created DESC
        LIMIT %s OFFSET %s;
    """

    cursos = ejecutar_consulta(query, params + [limit, offset], es_select=True) or []
    return jsonify({
        "cursos": cursos,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if total > 0 else 0
    }), 200


# =========================================================================
# ENDPOINT 2: CREAR UN NUEVO MANUAL PEDAGÓGICO / CURSO CON CAPÍTULOS
# =========================================================================
@cursos_bp.route('/manuales/nuevo', methods=['POST'])
def crear_manual():
    """
    Crea un curso con sus capítulos iniciales en una sola transacción.
    Recibe: { usuario_id, titulo, lenguaje, nivel, descripcion, capitulos[], modulos[] }
    """
    from database import obtener_conexion

    datos = request.get_json()
    
    if not datos:
        return jsonify({"error": "Petición JSON inválida"}), 400
    
    usuario_id = datos.get('usuario_id')
    titulo = datos.get('titulo')
    lenguaje = datos.get('lenguaje')
    nivel = datos.get('nivel')
    descripcion = datos.get('descripcion')
    imagen_url = datos.get('imagen_url')
    capitulos = datos.get('capitulos', [])
    modulos = datos.get('modulos', [])
    
    # Validaciones mínimas
    if not usuario_id:
        return jsonify({"error": "Debes iniciar sesión para crear un curso."}), 401
    if not titulo:
        return jsonify({"error": "El título del curso es obligatorio."}), 400
    if not lenguaje:
        return jsonify({"error": "El lenguaje es obligatorio."}), 400
    if len(capitulos) == 0:
        return jsonify({"error": "Debes agregar al menos un capítulo."}), 400

    # --- REGLA DE NEGOCIO: Verificación de permisos ---
    query_verificar_rol = "SELECT role FROM users WHERE id_user = %s;"
    usuario = ejecutar_consulta(query_verificar_rol, (usuario_id,), es_select=True)
    
    if not usuario or usuario[0]['role'] != 'Maestro':
        return jsonify({"error": "Acceso denegado. Solo los Maestros pueden crear cursos."}), 403

    conexion = obtener_conexion()
    if not conexion:
        return jsonify({"error": "Error de conexión con la base de datos."}), 500

    try:
        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:
            # Asegurar columnas adicionales (ignora si ya existen)
            for col, tipo in [('level', 'VARCHAR(50)'), ('description', 'TEXT')]:
                cursor.execute(f"""
                    ALTER TABLE courses ADD COLUMN IF NOT EXISTS {col} {tipo};
                """)

            # 1. Insertar el curso
            descripcion_guardar = descripcion if descripcion else None
            nivel_guardar = nivel if nivel else None
            primer_modulo = modulos[0] if modulos and modulos[0] else None
            cursor.execute("""
                INSERT INTO courses (id_user, title, course_image, language, module_name, level, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id_course;
            """, (usuario_id, titulo, imagen_url or None, lenguaje, primer_modulo, nivel_guardar, descripcion_guardar))
            curso_id = cursor.fetchone()['id_course']

            # 2. Insertar cada capítulo
            for idx, cap_titulo in enumerate(capitulos):
                if not cap_titulo:
                    continue
                modulo_cap = modulos[idx] if idx < len(modulos) and modulos[idx] else None
                cursor.execute("""
                    INSERT INTO chapters (id_course, id_user, chapter_title, chapter_content, chapter_order, solution)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (curso_id, usuario_id, cap_titulo, None, idx + 1, None))

            conexion.commit()

        return jsonify({
            "mensaje": "Curso y capítulos creados exitosamente.",
            "id_curso": curso_id
        }), 201

    except Exception as e:
        conexion.rollback()
        print(f"Error al crear curso: {e}")
        return jsonify({"error": "Error interno al guardar el curso en la base de datos."}), 500
    finally:
        conexion.close()


# =========================================================================
# ENDPOINT 3: VER CAPÍTULOS DE UN CURSO ESPECÍFICO
# =========================================================================
@cursos_bp.route('/cursos/<int:curso_id>/capitulos', methods=['GET'])
def get_capitulos(curso_id):
    """
    Devuelve los capítulos y lecciones correspondientes a un ID de curso.
    No incluye comentarios en la estructura según requerimiento de diseño.
    """
    query_select = """
        SELECT id_chapter, id_course, id_user, chapter_title, chapter_content, chapter_order, solution 
        FROM chapters 
        WHERE id_course = %s
        ORDER BY chapter_order ASC;
    """
    capitulos = ejecutar_consulta(query_select, (curso_id,), es_select=True)
    
    return jsonify({
        "id_course": curso_id,
        "capitulos": capitulos
    }), 200


# =========================================================================
# ENDPOINT 4: CREAR UN NUEVO CAPÍTULO EN UN CURSO EXISTENTE
# =========================================================================
@cursos_bp.route('/cursos/<int:curso_id>/capitulo/nuevo', methods=['POST'])
def crear_capitulo(curso_id):
    """
    Agrega un capítulo nuevo a un curso existente.
    Recibe: { id_user, chapter_title, chapter_content, chapter_order, exercises? }
    exercises: [{ question, expected_solution }]
    """
    from database import obtener_conexion

    datos = request.get_json()

    if not datos:
        return jsonify({"error": "Petición JSON inválida"}), 400

    id_user = datos.get('id_user')
    chapter_title = datos.get('chapter_title')
    chapter_content = datos.get('chapter_content')
    chapter_order = datos.get('chapter_order')
    exercises = datos.get('exercises', [])

    if not id_user:
        return jsonify({"error": "Debes iniciar sesión"}), 401
    if not chapter_title or not chapter_content:
        return jsonify({"error": "chapter_title y chapter_content son obligatorios"}), 400

    # Verificar rol Maestro
    query_rol = "SELECT role FROM users WHERE id_user = %s;"
    usuario = ejecutar_consulta(query_rol, (id_user,), es_select=True)
    if not usuario or usuario[0]['role'] != 'Maestro':
        return jsonify({"error": "Solo los Maestros pueden crear capítulos"}), 403

    # Verificar que el curso exista y pertenezca al usuario
    query_curso = "SELECT id_course FROM courses WHERE id_course = %s AND id_user = %s;"
    curso = ejecutar_consulta(query_curso, (curso_id, id_user), es_select=True)
    if not curso:
        return jsonify({"error": "Curso no encontrado o no te pertenece"}), 404

    conexion = obtener_conexion()
    if not conexion:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500

    try:
        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:
            # Asegurar tabla exercises
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS exercises (
                    id_exercise SERIAL PRIMARY KEY,
                    id_chapter INTEGER NOT NULL REFERENCES chapters(id_chapter) ON DELETE CASCADE,
                    question TEXT NOT NULL,
                    expected_solution TEXT NOT NULL
                );
            """)

            # Auto-calcular chapter_order si no se envió
            if not chapter_order:
                cursor.execute("SELECT COALESCE(MAX(chapter_order), 0) + 1 AS next_order FROM chapters WHERE id_course = %s;", (curso_id,))
                chapter_order = cursor.fetchone()['next_order']

            cursor.execute("""
                INSERT INTO chapters (id_course, id_user, chapter_title, chapter_content, chapter_order)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_chapter;
            """, (curso_id, id_user, chapter_title, chapter_content, chapter_order))
            chapter_id = cursor.fetchone()['id_chapter']

            for ex in exercises:
                question = ex.get('question', '').strip()
                expected_solution = ex.get('expected_solution', '').strip()
                if question and expected_solution:
                    cursor.execute("""
                        INSERT INTO exercises (id_chapter, question, expected_solution)
                        VALUES (%s, %s, %s);
                    """, (chapter_id, question, expected_solution))

            conexion.commit()

        return jsonify({
            "mensaje": "Capítulo creado exitosamente",
            "id_chapter": chapter_id,
            "id_course": curso_id
        }), 201

    except Exception as e:
        conexion.rollback()
        print(f"Error al crear capítulo: {e}")
        return jsonify({"error": "Error interno al guardar el capítulo"}), 500
    finally:
        conexion.close()


# =========================================================================
# ENDPOINT 5: ACTUALIZAR UN CAPÍTULO (PUT)
# =========================================================================
@cursos_bp.route('/cursos/<int:curso_id>/capitulo/<int:chapter_id>', methods=['PUT'])
def actualizar_capitulo(curso_id, chapter_id):
    from database import obtener_conexion

    datos = request.get_json()
    if not datos:
        return jsonify({"error": "Petición JSON inválida"}), 400

    id_user = datos.get('id_user')
    if not id_user:
        return jsonify({"error": "Debes iniciar sesión"}), 401

    # Verificar que el capítulo exista y pertenezca al curso
    query_capitulo = """
        SELECT c.id_course, c.id_user AS course_owner
        FROM chapters ch
        JOIN courses c ON ch.id_course = c.id_course
        WHERE ch.id_chapter = %s AND ch.id_course = %s
    """
    resultado = ejecutar_consulta(query_capitulo, (chapter_id, curso_id), es_select=True)
    if not resultado:
        return jsonify({"error": "Capítulo no encontrado"}), 404

    if resultado[0]['course_owner'] != id_user:
        return jsonify({"error": "No tienes permiso para editar este capítulo"}), 403

    chapter_title = datos.get('chapter_title')
    chapter_content = datos.get('chapter_content')

    if not chapter_title and not chapter_content:
        return jsonify({"error": "Debes enviar al menos un campo para actualizar"}), 400

    conexion = obtener_conexion()
    if not conexion:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500

    try:
        campos = []
        params = []
        if chapter_title:
            campos.append("chapter_title = %s")
            params.append(chapter_title)
        if chapter_content is not None:
            campos.append("chapter_content = %s")
            params.append(chapter_content)

        params.extend([chapter_id, curso_id])

        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"""
                UPDATE chapters
                SET {', '.join(campos)}
                WHERE id_chapter = %s AND id_course = %s
                RETURNING id_chapter, id_course, chapter_title, chapter_content, chapter_order;
            """, params)
            actualizado = cursor.fetchone()
            conexion.commit()

        return jsonify({"mensaje": "Capítulo actualizado", "capitulo": actualizado}), 200

    except Exception as e:
        conexion.rollback()
        print(f"Error al actualizar capítulo: {e}")
        return jsonify({"error": "Error interno al actualizar el capítulo"}), 500
    finally:
        conexion.close()


# =========================================================================
# ENDPOINT 6: ELIMINAR UN CAPÍTULO (DELETE)
# =========================================================================
@cursos_bp.route('/cursos/<int:curso_id>/capitulo/<int:chapter_id>', methods=['DELETE'])
def eliminar_capitulo(curso_id, chapter_id):
    from database import obtener_conexion

    id_user = request.args.get('id_user')
    if not id_user:
        return jsonify({"error": "Debes iniciar sesión"}), 401

    # Verificar que el capítulo exista y pertenezca al dueño del curso
    query_capitulo = """
        SELECT c.id_user AS course_owner, ch.chapter_order
        FROM chapters ch
        JOIN courses c ON ch.id_course = c.id_course
        WHERE ch.id_chapter = %s AND ch.id_course = %s
    """
    resultado = ejecutar_consulta(query_capitulo, (chapter_id, curso_id), es_select=True)
    if not resultado:
        return jsonify({"error": "Capítulo no encontrado"}), 404

    if resultado[0]['course_owner'] != int(id_user):
        return jsonify({"error": "No tienes permiso para eliminar este capítulo"}), 403

    order_eliminado = resultado[0]['chapter_order']

    conexion = obtener_conexion()
    if not conexion:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500

    try:
        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                DELETE FROM chapters
                WHERE id_chapter = %s AND id_course = %s;
            """, (chapter_id, curso_id))
            if cursor.rowcount == 0:
                conexion.rollback()
                return jsonify({"error": "Capítulo no encontrado"}), 404

            # Reordenar capítulos siguientes
            cursor.execute("""
                UPDATE chapters
                SET chapter_order = chapter_order - 1
                WHERE id_course = %s AND chapter_order > %s;
            """, (curso_id, order_eliminado))

            conexion.commit()

        return jsonify({"mensaje": "Capítulo eliminado exitosamente"}), 200

    except Exception as e:
        conexion.rollback()
        print(f"Error al eliminar capítulo: {e}")
        return jsonify({"error": "Error interno al eliminar el capítulo"}), 500
    finally:
        conexion.close()


# =========================================================================
# ENDPOINT 7: ACTUALIZAR UN CURSO (PUT)
# =========================================================================
@cursos_bp.route('/cursos/<int:curso_id>', methods=['PUT'])
def actualizar_curso(curso_id):
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "Petición JSON inválida"}), 400

    id_user = datos.get('id_user')
    if not id_user:
        return jsonify({"error": "Debes iniciar sesión"}), 401

    # Verificar propiedad
    query_curso = "SELECT id_course FROM courses WHERE id_course = %s AND id_user = %s;"
    curso = ejecutar_consulta(query_curso, (curso_id, id_user), es_select=True)
    if not curso:
        return jsonify({"error": "Curso no encontrado o no te pertenece"}), 404

    campos = []
    params = []
    for campo, valor in [('title', datos.get('titulo')), ('language', datos.get('lenguaje')),
                          ('level', datos.get('nivel')), ('description', datos.get('descripcion')),
                          ('course_image', datos.get('imagen_url'))]:
        if valor is not None:
            campos.append(f"{campo} = %s")
            params.append(valor)

    if not campos:
        return jsonify({"error": "No hay campos para actualizar"}), 400

    from database import obtener_conexion
    conn = obtener_conexion()
    if not conn:
        return jsonify({"error": "Error de conexión"}), 500

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"""
                UPDATE courses SET {', '.join(campos)} WHERE id_course = %s RETURNING id_course, id_user, title, date_created, course_image, language, module_name, level, description;
            """, params + [curso_id])
            actualizado = cur.fetchone()
            conn.commit()
        return jsonify({"mensaje": "Curso actualizado", "curso": actualizado}), 200
    except Exception as e:
        conn.rollback()
        print(f"Error al actualizar curso: {e}")
        return jsonify({"error": "Error interno"}), 500
    finally:
        conn.close()


# =========================================================================
# ENDPOINT 8: ELIMINAR UN CURSO (DELETE)
# =========================================================================
@cursos_bp.route('/cursos/<int:curso_id>', methods=['DELETE'])
def eliminar_curso(curso_id):
    id_user = request.args.get('id_user')
    if not id_user:
        return jsonify({"error": "Debes iniciar sesión"}), 401

    query_curso = "SELECT id_course FROM courses WHERE id_course = %s AND id_user = %s;"
    curso = ejecutar_consulta(query_curso, (curso_id, int(id_user)), es_select=True)
    if not curso:
        return jsonify({"error": "Curso no encontrado o no te pertenece"}), 404

    from database import obtener_conexion
    conn = obtener_conexion()
    if not conn:
        return jsonify({"error": "Error de conexión"}), 500

    try:
        with conn.cursor() as cur:
            # Eliminar ejercicios (ON DELETE CASCADE desde exercises → chapters)
            # Eliminar capítulos primero para evitar FK violation
            cur.execute("DELETE FROM chapters WHERE id_course = %s;", (curso_id,))
            cur.execute("DELETE FROM courses WHERE id_course = %s;", (curso_id,))
            conn.commit()
        return jsonify({"mensaje": "Curso y todos sus capítulos eliminados"}), 200
    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar curso: {e}")
        return jsonify({"error": "Error interno"}), 500
    finally:
        conn.close()