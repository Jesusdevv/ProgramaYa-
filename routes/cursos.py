from flask import Blueprint, request, jsonify
from psycopg2.extras import RealDictCursor
from database import ejecutar_consulta

cursos_bp = Blueprint('cursos', __name__)

# =========================================================================
# ENDPOINT 1: LISTAR TODOS LOS CURSOS (O FILTRARLOS POR LENGUAJE)
# =========================================================================
@cursos_bp.route('/cursos', methods=['GET'])
def get_cursos():
    """
    Devuelve la lista de cursos disponibles en la plataforma.
    Permite filtrar por lenguaje en la URL usando: /api/cursos?lenguaje=Python
    """
    lenguaje_filtro = request.args.get('lenguaje')
    
    if lenguaje_filtro:
        query_select = """
            SELECT id_course, id_user, title, date_created, course_image, language, module_name, level, description 
            FROM courses 
            WHERE language = %s;
        """
        cursos = ejecutar_consulta(query_select, (lenguaje_filtro,), es_select=True)
    else:
        query_select = """
            SELECT id_course, id_user, title, date_created, course_image, language, module_name, level, description 
            FROM courses;
        """
        cursos = ejecutar_consulta(query_select, es_select=True)
        
    return jsonify({"cursos": cursos}), 200


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
    Recibe: { id_user, chapter_title, chapter_content, chapter_order }
    """
    from database import obtener_conexion

    datos = request.get_json()

    if not datos:
        return jsonify({"error": "Petición JSON inválida"}), 400

    id_user = datos.get('id_user')
    chapter_title = datos.get('chapter_title')
    chapter_content = datos.get('chapter_content')
    chapter_order = datos.get('chapter_order')

    if not id_user:
        return jsonify({"error": "Debes iniciar sesión"}), 401
    if not chapter_title or not chapter_content or not chapter_order:
        return jsonify({"error": "Todos los campos son obligatorios (chapter_title, chapter_content, chapter_order)"}), 400

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
            cursor.execute("""
                INSERT INTO chapters (id_course, id_user, chapter_title, chapter_content, chapter_order)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_chapter;
            """, (curso_id, id_user, chapter_title, chapter_content, chapter_order))
            chapter_id = cursor.fetchone()['id_chapter']
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