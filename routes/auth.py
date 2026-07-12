from flask import Blueprint, request, jsonify
# Importación centralizada limpia sin .connection
from database import ejecutar_consulta

auth_bp = Blueprint('auth', __name__)

# =========================================================================
# ENDPOINT 1: REGISTRO DE USUARIOS
# =========================================================================
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No se enviaron datos"}), 400
        
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({"error": "Faltan campos obligatorios"}), 400
        
    # Verificar si el correo ya existe en Neon para evitar duplicados
    query_verificar = "SELECT id_user FROM users WHERE email = %s;"
    usuario_existente = ejecutar_consulta(query_verificar, (email,), es_select=True)
    if usuario_existente:
        return jsonify({"error": "El correo electrónico ya está registrado"}), 400

    # Insertar el nuevo usuario usando las columnas de tu Diccionario de Datos
    # Por defecto, se registra con el rol 'Estudiante' e is_validated en False
    query_insertar = """
        INSERT INTO users (username, email, password, role, is_validated)
        VALUES (%s, %s, %s, 'Estudiante', FALSE);
    """
    exito = ejecutar_consulta(query_insertar, (username, email, password), es_select=False)
    
    if exito:
        return jsonify({
            "message": f"Usuario {username} registrado con éxito en ProgramaYa!",
            "status": "success"
        }), 201
    else:
        return jsonify({"error": "Error interno al registrar el usuario en la base de datos"}), 500


# =========================================================================
# ENDPOINT 2: INICIO DE SESIÓN (LOGIN)
# =========================================================================
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Petición JSON inválida"}), 400
        
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Correo y contraseña requeridos"}), 400
        
    # Consultar a Neon si existe el usuario con ese email y esa contraseña
    query_login = """
        SELECT id_user, username, email, role, is_validated 
        FROM users 
        WHERE email = %s AND password = %s;
    """
    usuario = ejecutar_consulta(query_login, (email, password), es_select=True)
    
    if usuario:
        # Al usar RealDictCursor, 'usuario[0]' ya es un diccionario con las columnas reales
        return jsonify({
            "message": "Inicio de sesión exitoso",
            "user": {
                "id_user": usuario[0]['id_user'],
                "username": usuario[0]['username'],
                "role": usuario[0]['role'],
                "is_validated": usuario[0]['is_validated']
            }
        }), 200
        
    return jsonify({"error": "Credenciales inválidas"}), 401


# =========================================================================
# ENDPOINT 3: CAMBIO DE CONTRASEÑA
# =========================================================================
@auth_bp.route('/cambiar-contrasena', methods=['POST'])
def cambiar_contrasena():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Petición JSON inválida"}), 400

    id_user = data.get('id_user')
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not id_user or not current_password or not new_password:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "La nueva contraseña debe tener al menos 6 caracteres"}), 400

    if current_password == new_password:
        return jsonify({"error": "La nueva contraseña no puede ser igual a la actual"}), 400

    # Verificar contraseña actual
    query_verificar = "SELECT password FROM users WHERE id_user = %s;"
    usuario = ejecutar_consulta(query_verificar, (id_user,), es_select=True)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if usuario[0]['password'] != current_password:
        return jsonify({"error": "La contraseña actual no es correcta"}), 401

    # Cambiar contraseña
    query_update = "UPDATE users SET password = %s WHERE id_user = %s;"
    exito = ejecutar_consulta(query_update, (new_password, id_user), es_select=False)

    if exito:
        return jsonify({"message": "Contraseña cambiada exitosamente"}), 200
    else:
        return jsonify({"error": "Error al cambiar la contraseña"}), 500