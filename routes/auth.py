from flask import Blueprint, request, jsonify
from database.connection import ejecutar_consulta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def registrar_usuario():
    """Endpoint para registrar un usuario aplicando las reglas de negocio."""
    datos = request.get_json()
    
 
    if not datos:
        return jsonify({"error": "El cuerpo de la petición debe ser un JSON válido"}), 400
        
    nombre = datos.get('nombre')
    correo = datos.get('correo')
    clave = datos.get('clave')
    

    if not nombre or not correo or not clave:
        return jsonify({"error": "Todos los campos (nombre, correo, clave) son obligatorios"}), 400
        
    
    rol_por_defecto = "Estudiante"
    
   
    query_insertar = """
        INSERT INTO usuarios (nombre, correo, clave, rol) 
        VALUES (%s, %s, %s, %s);
    """
    params = (nombre, correo, clave, rol_por_defecto)
    
   
    exito = ejecutar_consulta(query_insertar, params, es_select=False)
    
    if exito:
        return jsonify({
            "mensaje": "Usuario registrado exitosamente",
            "usuario": {
                "nombre": nombre,
                "correo": correo,
                "rol": rol_por_defecto
            }
        }), 201
    else:
        return jsonify({"error": "No se pudo completar el registro. Inténtelo más tarde."}), 500