from flask import Blueprint, request, jsonify
from database import ejecutar_consulta

perfil_bp = Blueprint('perfil', __name__)

@perfil_bp.route('/perfil', methods=['GET'])
def obtener_perfil():
    id_user = request.args.get('user_id')
    if not id_user:
        return jsonify({"error": "user_id es requerido"}), 400
    query = "SELECT id_user, username, email, role FROM users WHERE id_user = %s;"
    usuario = ejecutar_consulta(query, (id_user,), es_select=True)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    return jsonify({"user": usuario[0]}), 200

@perfil_bp.route('/perfil', methods=['PUT'])
def actualizar_perfil():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Petición JSON inválida"}), 400
    id_user = data.get('user_id')
    username = data.get('username')
    email = data.get('email')
    if not id_user:
        return jsonify({"error": "user_id es requerido"}), 400
    if not username and not email:
        return jsonify({"error": "Debes proporcionar al menos username o email"}), 400

    campos = []
    params = []
    if username:
        campos.append("username = %s")
        params.append(username)
    if email:
        query_verificar = "SELECT id_user FROM users WHERE email = %s AND id_user != %s;"
        existente = ejecutar_consulta(query_verificar, (email, id_user), es_select=True)
        if existente:
            return jsonify({"error": "El correo electrónico ya está en uso"}), 400
        campos.append("email = %s")
        params.append(email)

    params.append(id_user)
    query = f"UPDATE users SET {', '.join(campos)} WHERE id_user = %s;"
    exito = ejecutar_consulta(query, params, es_select=False)
    if exito:
        nuevo_query = "SELECT id_user, username, email, role FROM users WHERE id_user = %s;"
        actualizado = ejecutar_consulta(nuevo_query, (id_user,), es_select=True)
        return jsonify({"message": "Perfil actualizado exitosamente", "user": actualizado[0]}), 200
    return jsonify({"error": "Error al actualizar el perfil"}), 500
