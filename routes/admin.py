from flask import Blueprint, request, jsonify
# Importación limpia gracias al paquete centralizado database/__init__.py
from database import ejecutar_consulta

# Creamos el Blueprint para el módulo de Administración
admin_bp = Blueprint('admin', __name__)

# --- ENDPOINTS ---

# =========================================================================
# ENDPOINT 1: SOLICITAR CAMBIO DE ROL A MAESTRO
# =========================================================================
@admin_bp.route('/solicitar-maestro', methods=['POST'])
def solicitar_cambio_rol():
    """Endpoint para que un estudiante envíe una solicitud para ser Maestro."""
    datos = request.get_json()
    
    if not datos:
        return jsonify({"error": "Petición JSON inválida"}), 400
        
    usuario_id = datos.get('usuario_id')
    
    if not usuario_id:
        return jsonify({"error": "El ID de usuario es obligatorio"}), 400

    query_solicitud = """
        INSERT INTO role_requests (id_user, status)
        VALUES (%s, 'Pendiente');
    """
    exito = ejecutar_consulta(query_solicitud, (usuario_id,), es_select=False)
    
    if exito:
        return jsonify({"mensaje": "Solicitud enviada con éxito. En espera de aprobación del Administrador."}), 202
    else:
        return jsonify({"error": "Error al procesar la solicitud"}), 500


# =========================================================================
# ENDPOINT 2: PROCESAR SOLICITUD (APROBAR / RECHAZAR)
# =========================================================================
@admin_bp.route('/procesar-maestro', methods=['POST'])
def procesar_solicitud_maestro():
    """Endpoint exclusivo del Administrador para aprobar o rechazar solicitudes."""
    datos = request.get_json()
    
    if not datos:
        return jsonify({"error": "Petición JSON inválida"}), 400
        
    id_request = datos.get('id_request')
    id_admin = datos.get('id_admin')
    accion = datos.get('accion')
    
    if not id_request or not id_admin or not accion:
        return jsonify({"error": "Faltan campos obligatorios (id_request, id_admin, accion)"}), 400

    # --- REGLA DE NEGOCIO: Verificación de rol (Tabla: usuarios, columnas: role, id_user) ---
    query_verificar_admin = "SELECT role FROM users WHERE id_user = %s;"
    usuario = ejecutar_consulta(query_verificar_admin, (id_admin,), es_select=True)
    
    if not usuario or usuario[0]['role'] != 'Administrador':
        return jsonify({"error": "Acceso denegado. Operación exclusiva del Administrador."}), 403

    if accion == "APROBAR":
        query_update_request = "UPDATE role_requests SET status = 'Aprobado' WHERE id_request = %s;"
        ejecutar_consulta(query_update_request, (id_request,), es_select=False)
        
        query_get_user = "SELECT id_user FROM role_requests WHERE id_request = %s;"
        solicitud = ejecutar_consulta(query_get_user, (id_request,), es_select=True)
        
        if solicitud:
            user_id = solicitud[0]['id_user']
            # 3. Le cambiamos el rol al usuario a 'Maestro' en la tabla usuarios
            query_update_rol = "UPDATE users SET role = 'Maestro' WHERE id_user = %s;"
            ejecutar_consulta(query_update_rol, (user_id,), es_select=False)
            
            return jsonify({"mensaje": "Solicitud aprobada. El usuario ahora tiene el rol de Maestro."}), 200
            
    elif accion == "RECHAZAR":
        query_update_request = "UPDATE role_requests SET status = 'Rechazado' WHERE id_request = %s;"
        ejecutar_consulta(query_update_request, (id_request,), es_select=False)
        return jsonify({"mensaje": "Solicitud rechazada correctamente por el Administrador."}), 200

    return jsonify({"error": "Acción no reconocida (Use APROBAR o RECHAZAR)"}), 400


# =========================================================================
# ENDPOINT 3: LISTAR SOLICITUDES PENDIENTES
# =========================================================================
@admin_bp.route('/solicitudes-pendientes', methods=['GET'])
def listar_solicitudes_pendientes():
    """Endpoint para que el Admin obtenga todas las solicitudes con estado 'Pendiente'."""
    query = """
        SELECT id_request, id_user, status
        FROM role_requests
        WHERE status = 'Pendiente';
    """
    resultados = ejecutar_consulta(query, es_select=True)
    if resultados is None:
        return jsonify({"error": "Error al consultar la base de datos"}), 500
    return jsonify(resultados), 200


# =========================================================================
# ENDPOINT 4: LISTAR SOLICITUDES APROBADAS
# =========================================================================
@admin_bp.route('/solicitudes-aprobadas', methods=['GET'])
def listar_solicitudes_aprobadas():
    query = """
        SELECT id_request, id_user, status
        FROM role_requests
        WHERE status = 'Aprobado';
    """
    resultados = ejecutar_consulta(query, es_select=True)
    if resultados is None:
        return jsonify({"error": "Error al consultar la base de datos"}), 500
    return jsonify(resultados), 200