from flask import Blueprint, request, jsonify
from database import ejecutar_consulta  # <--- Corto, limpio y sin .connection

cursos_bp = Blueprint('cursos', __name__)
# ... (el resto de tus rutas queda exactamente igual)

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
            SELECT id_course, id_user, title, date_created, course_image, language, module_name 
            FROM cursos 
            WHERE language = %s;
        """
        cursos = ejecutar_consulta(query_select, (lenguaje_filtro,), es_select=True)
    else:
        query_select = """
            SELECT id_course, id_user, title, date_created, course_image, language, module_name 
            FROM cursos;
        """
        cursos = ejecutar_consulta(query_select, es_select=True)
        
    return jsonify({"cursos": cursos}), 200


# =========================================================================
# ENDPOINT 2: CREAR UN NUEVO MANUAL PEDAGÓGICO / CURSO
# =========================================================================
@cursos_bp.route('/manuales/nuevo', methods=['POST'])
def crear_manual():
    """
    Endpoint de escritura: Restringido por Regla de Negocio a usuarios con rol 'Maestro'.
    """
    datos = request.get_json()
    
    if not datos:
        return jsonify({"error": "Petición JSON inválida"}), 400
        
    usuario_id = datos.get('usuario_id')
    titulo = datos.get('title')
    course_image = datos.get('course_image')
    lenguaje = datos.get('language')
    modulo_name = datos.get('module_name')
    
    if not usuario_id or not titulo or not course_image or not lenguaje or not modulo_name:
        return jsonify({"error": "Faltan campos obligatorios (usuario_id, title, course_image, language, module_name)"}), 400

    # --- REGLA DE NEGOCIO: Verificación de permisos de escritura ---
    query_verificar_rol = "SELECT role FROM usuarios WHERE id_user = %s;"
    usuario = ejecutar_consulta(query_verificar_rol, (usuario_id,), es_select=True)
    
    if not usuario or usuario[0]['role'] != 'Maestro':
        return jsonify({"error": "Acceso denegado. Los Estudiantes solo poseen permisos de lectura."}), 403

    # Inserción en la base de datos Neon
    query_insertar_manual = """
        INSERT INTO cursos (id_user, title, course_image, language, module_name)
        VALUES (%s, %s, %s, %s, %s);
    """
    params = (usuario_id, titulo, course_image, lenguaje, modulo_name)
    exito = ejecutar_consulta(query_insertar_manual, params, es_select=False)
    
    if exito:
        return jsonify({"mensaje": "Manual pedagógico publicado de forma exitosa por el Maestro."}), 201
    else:
        return jsonify({"error": "Error interno al intentar registrar el manual en la base de datos."}), 500


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
        SELECT id_chapter, id_course, id_user, chapter_title, chapter_content, chapter_order, solution_text 
        FROM capitulos 
        WHERE id_course = %s
        ORDER BY chapter_order ASC;
    """
    capitulos = ejecutar_consulta(query_select, (curso_id,), es_select=True)
    
    return jsonify({
        "id_course": curso_id,
        "capitulos": capitulos
    }), 200