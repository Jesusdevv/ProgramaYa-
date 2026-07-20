from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
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

    hashed_password = generate_password_hash(password)

    query_insertar = """
        INSERT INTO users (username, email, password, role, is_validated)
        VALUES (%s, %s, %s, 'Estudiante', FALSE);
    """
    exito = ejecutar_consulta(query_insertar, (username, email, hashed_password), es_select=False)
    
    if exito:
        return jsonify({
            "mensaje": f"Usuario {username} registrado con éxito en ProgramaYa!"
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
        
    # Buscar usuario por email
    query_login = """
        SELECT id_user, username, email, password, role, is_validated 
        FROM users 
        WHERE email = %s;
    """
    usuario = ejecutar_consulta(query_login, (email,), es_select=True)
    
    if usuario and check_password_hash(usuario[0]['password'], password):
        if not usuario[0]['is_validated']:
            return jsonify({"error": "Cuenta no validada. Espera a que el administrador active tu cuenta."}), 403

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

    if not check_password_hash(usuario[0]['password'], current_password):
        return jsonify({"error": "La contraseña actual no es correcta"}), 401

    # Cambiar contraseña
    hashed_new = generate_password_hash(new_password)
    query_update = "UPDATE users SET password = %s WHERE id_user = %s;"
    exito = ejecutar_consulta(query_update, (hashed_new, id_user), es_select=False)

    if exito:
        return jsonify({"message": "Contraseña cambiada exitosamente"}), 200
    else:
        return jsonify({"error": "Error al cambiar la contraseña"}), 500