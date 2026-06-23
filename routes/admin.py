from flask import Blueprint, request, jsonify
from database.connection import ejecutar_consulta

# Creamos el Blueprint para el módulo de Administración
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/solicitar-maestro', methods=['POST'])
def solicitar_cambio_rol():
    """Endpoint para que un estudiante envíe una solicitud para ser Maestro."""
    datos = request.get_json()
    
    if not datos:
        return jsonify({"error": "Petición JSON inválida"}), 400
        
    usuario_id = datos.get('usuario_id')
    
    if not usuario_id:
        return jsonify({"error": "El ID de usuario es obligatorio"}), 400

    # Insertamos la solicitud en la tabla de control (asumiendo tabla 'solicitudes_rol' en Neon)
    query_solicitud = """
        INSERT INTO solicitudes_rol (usuario_id, estado)
        VALUES (%s, 'Pendiente');
    """
    exito = ejecutar_consulta(query_solicitud, (usuario_id,), es_select=False)
    
    if exito:
        return jsonify({"mensaje": "Solicitud enviada con éxito. En espera de aprobación del Administrador."}), 202
    else:
        return jsonify({"error": "Error al procesar la solicitud"}), 500


@admin_bp.route('/procesar-maestro', methods=['POST'])
def procesar_solicitud_maestro():
    """Endpoint exclusivo del Administrador para aprobar o rechazar solicitudes."""
    datos = request.get_json()
    
    if not datos:
        return jsonify({"error": "Petición JSON inválida"}), 400
        
    id_solicitud = datos.get('id_solicitud')
    id_admin = datos.get('id_admin')      # ID del usuario que opera
    accion = datos.get('accion')          # Espera: 'APROBAR' o 'RECHAZAR'
    
    if not id_solicitud or not id_admin or not accion:
        return jsonify({"error": "Faltan campos obligatorios (id_solicitud, id_admin, accion)"}), 400

    # --- APLICACIÓN DE LA REGLA DE NEGOCIO #2 (Validación de rol ejecutor) ---
    # Primero verificamos si quien intenta operar es realmente un Administrador en Neon DB
    query_verificar_admin = "SELECT rol FROM usuarios WHERE id = %s;"
    usuario = ejecutar_consulta(query_verificar_admin, (id_admin,), es_select=True)
    
    if not usuario or usuario[0]['rol'] != 'Administrador':
        return jsonify({"error": "Acceso denegado. Operación exclusiva del Administrador."}), 403

    if accion == "APROBAR":
        # 1. Actualizamos el estado de la solicitud
        query_update_solicitud = "UPDATE solicitudes_rol SET estado = 'Aprobado' WHERE id = %s;"
        ejecutar_consulta(query_update_solicitud, (id_solicitud,), es_select=False)
        
        # 2. Conseguimos el usuario_id de esa solicitud para cambiarle el rol a 'Maestro'
        query_get_user = "SELECT usuario_id FROM solicitudes_rol WHERE id = %s;"
        solicitud = ejecutar_consulta(query_get_user, (id_solicitud,), es_select=True)
        
        if solicitud:
            user_id = solicitud[0]['usuario_id']
            query_update_rol = "UPDATE usuarios SET rol = 'Maestro' WHERE id = %s;"
            ejecutar_consulta(query_update_rol, (user_id,), es_select=False)
            
            return jsonify({"mensaje": "Solicitud aprobada. El usuario ahora tiene el rol de Maestro."}), 200
            
    elif accion == "RECHAZAR":
        query_update_solicitud = "UPDATE solicitudes_rol SET estado = 'Rechazado' WHERE id = %s;"
        ejecutar_consulta(query_update_solicitud, (id_solicitud,), es_select=False)
        return jsonify({"mensaje": "Solicitud rechazada correctamente por el Administrador."}), 200

    return jsonify({"error": "Acción no reconocida (Use APROBAR o RECHAZAR)"}), 400