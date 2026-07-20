from flask import Blueprint, request, jsonify
from psycopg2.extras import RealDictCursor
from database import ejecutar_consulta, obtener_conexion

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

    conn = obtener_conexion()
    if not conn:
        return jsonify({"error": "Error de conexión con la base de datos"}), 500

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Asegurar tabla notifications
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id_notification SERIAL PRIMARY KEY,
                    type VARCHAR(50) NOT NULL,
                    message TEXT NOT NULL,
                    related_id INTEGER,
                    is_read BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("""
                INSERT INTO role_requests (id_user, status)
                VALUES (%s, 'Pendiente')
                RETURNING id_request, id_user;
            """, (usuario_id,))
            solicitud = cur.fetchone()

            # Obtener username del solicitante
            cur.execute("SELECT username FROM users WHERE id_user = %s;", (usuario_id,))
            user_data = cur.fetchone()
            username = user_data['username'] if user_data else 'Usuario'

            cur.execute("""
                INSERT INTO notifications (type, message, related_id)
                VALUES (%s, %s, %s);
            """, ('role_request', f'{username} (ID {usuario_id}) ha solicitado ser Maestro.', solicitud['id_request']))

            conn.commit()

        return jsonify({"mensaje": "Solicitud enviada con éxito. En espera de aprobación del Administrador."}), 202
    except Exception as e:
        conn.rollback()
        print(f"Error al procesar solicitud: {e}")
        return jsonify({"error": "Error al procesar la solicitud"}), 500
    finally:
        conn.close()


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
# ENDPOINT 5: LISTAR USUARIOS PENDIENTES DE VALIDACIÓN
# =========================================================================
@admin_bp.route('/usuarios-pendientes', methods=['GET'])
def listar_usuarios_pendientes():
    """Lista usuarios con is_validated = FALSE (pendientes de activación)."""
    query = """
        SELECT id_user, username, email, role
        FROM users
        WHERE is_validated = FALSE;
    """
    resultados = ejecutar_consulta(query, es_select=True)
    if resultados is None:
        return jsonify({"error": "Error al consultar la base de datos"}), 500
    return jsonify(resultados), 200


# =========================================================================
# ENDPOINT 6: VALIDAR USUARIO (ACTIVAR CUENTA)
# =========================================================================
@admin_bp.route('/validar-usuario', methods=['POST'])
def validar_usuario():
    """Endpoint exclusivo del Administrador para activar la cuenta de un usuario."""
    datos = request.get_json()

    if not datos:
        return jsonify({"error": "Petición JSON inválida"}), 400

    id_user = datos.get('id_user')
    id_admin = datos.get('id_admin')

    if not id_user or not id_admin:
        return jsonify({"error": "Faltan campos obligatorios (id_user, id_admin)"}), 400

    query_verificar_admin = "SELECT role FROM users WHERE id_user = %s;"
    admin = ejecutar_consulta(query_verificar_admin, (id_admin,), es_select=True)

    if not admin or admin[0]['role'] != 'Administrador':
        return jsonify({"error": "Acceso denegado. Operación exclusiva del Administrador."}), 403

    query_activar = "UPDATE users SET is_validated = TRUE WHERE id_user = %s;"
    exito = ejecutar_consulta(query_activar, (id_user,), es_select=False)

    if exito:
        return jsonify({"mensaje": "Cuenta activada exitosamente."}), 200
    else:
        return jsonify({"error": "Error al activar la cuenta."}), 500


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


# =========================================================================
# ENDPOINT 7: LISTAR NOTIFICACIONES NO LEÍDAS
# =========================================================================
@admin_bp.route('/notificaciones', methods=['GET'])
def listar_notificaciones():
    query = """
        SELECT id_notification, type, message, related_id, is_read, created_at
        FROM notifications
        WHERE is_read = FALSE
        ORDER BY created_at DESC
        LIMIT 50;
    """
    resultados = ejecutar_consulta(query, es_select=True) or []
    return jsonify(resultados), 200


# =========================================================================
# ENDPOINT 8: MARCAR NOTIFICACIÓN COMO LEÍDA
# =========================================================================
@admin_bp.route('/notificaciones/<int:id_notification>/leer', methods=['PUT'])
def marcar_notificacion_leida(id_notification):
    query = "UPDATE notifications SET is_read = TRUE WHERE id_notification = %s;"
    exito = ejecutar_consulta(query, (id_notification,), es_select=False)
    if exito:
        return jsonify({"mensaje": "Notificación marcada como leída"}), 200
    return jsonify({"error": "Error al marcar notificación"}), 500