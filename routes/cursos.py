from flask import Blueprint, jsonify, request  # CORREGIDO: Importamos request

cursos_bp = Blueprint('cursos', __name__)

# --- FUNCIÓN TEMPORAL PARA EVITAR ERRORES (Simulación de Neon DB) ---
def ejecutar_consulta(query, params=None, es_select=True):
    """
    Función puente temporal para la metodología RAD.
    Simula las respuestas de PostgreSQL sin colgar el servidor.
    """
    print(f"[Neon DB Ejecutando]: {query} | Parámetros: {params}")
    
    if es_select:
        # Si busca el rol del usuario (Simulamos que el ID 1 es Maestro y el 2 es Estudiante)
        if "FROM usuarios" in query:
            if params and params[0] == 1:
                return [{'rol': 'Maestro'}]
            return [{'rol': 'Estudiante'}]
            
        # Si busca los manuales/cursos
        return [
            {"id": 1, "titulo": "Variables y Estructuras en Python", "lenguaje": "Python", "contenido": "Guía de fundamentos...", "creador_id": 1},
            {"id": 2, "titulo": "Manipulación del DOM con JS", "lenguaje": "JavaScript", "contenido": "Guía de frontend...", "creador_id": 1}
        ]
    return True # Simulamos que el INSERT fue exitoso

# --- ENDPOINTS CORREGIDOS ---

@cursos_bp.route('/cursos', methods=['GET'])
def get_cursos():
    lenguaje_filtro = request.args.get('lenguaje')
    
    if lenguaje_filtro:
        query_select = "SELECT id, titulo, lenguaje, contenido, creador_id FROM manuales WHERE lenguaje = %s;"
        manuales = ejecutar_consulta(query_select, (lenguaje_filtro,), es_select=True)
    else:
        query_select = "SELECT id, titulo, lenguaje, contenido, creador_id FROM manuales;"
        manuales = ejecutar_consulta(query_select, es_select=True)
        
    return jsonify({"manuales": manuales}), 200


@cursos_bp.route('/manuales/nuevo', methods=['POST'])
def crear_manual():
    """Endpoint de escritura: Restringido por Regla de Negocio a rol 'Maestro'."""
    datos = request.get_json()
    
    if not datos:
        return jsonify({"error": "Petición JSON inválida"}), 400
        
    usuario_id = datos.get('usuario_id') # ID de quien intenta crear el manual
    titulo = datos.get('titulo')
    lenguaje = datos.get('lenguaje') # Debería ser 'Python' o 'JavaScript'
    contenido = datos.get('contenido')
    
    if not usuario_id or not titulo or not lenguaje or not contenido:
        return jsonify({"error": "Faltan campos obligatorios (usuario_id, titulo, lenguaje, contenido)"}), 400

    # --- APLICACIÓN DE LA REGLA DE NEGOCIO #3 (Verificación de permisos de escritura) ---
    query_verificar_rol = "SELECT rol FROM usuarios WHERE id = %s;"
    usuario = ejecutar_consulta(query_verificar_rol, (usuario_id,), es_select=True)
    
    if not usuario or usuario[0]['rol'] != 'Maestro':
        return jsonify({"error": "Acceso denegado. Los Estudiantes solo poseen permisos de lectura."}), 403

    # Si pasa la validación del rol, procedemos a insertar el nuevo manual en Neon DB
    query_insertar_manual = """
        INSERT INTO manuales (titulo, lenguaje, contenido, creador_id)
        VALUES (%s, %s, %s, %s);
    """
    params = (titulo, lenguaje, contenido, usuario_id)
    exito = ejecutar_consulta(query_insertar_manual, params, es_select=False)
    
    if exito:
        return jsonify({"mensaje": "Manual pedagógico publicado de forma exitosa por el Maestro."}), 201
    else:
        return jsonify({"error": "Error interno al intentar registrar el manual."}), 500