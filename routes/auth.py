from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth', __name__)

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
        
    # NOTA: Dejamos esto en formato de prueba JSON por ahora.
    # En el siguiente paso crearemos la función real para conectar a Neon.
    return jsonify({
        "message": f"Usuario {username} registrado con éxito en ProgramaYa!",
        "status": "success"
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Correo y contraseña requeridos"}), 400
        
    # Simulación de login exitoso temporal para desarrollo
    if email == "admin@programaya.com" and password == "12345":
        return jsonify({
            "message": "Inicio de sesión exitoso",
            "user": {"username": "AdminEjemplo", "role": "admin"}
        }), 200
        
    return jsonify({"error": "Credenciales inválidas"}), 401