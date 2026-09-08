from flask import Blueprint, request, jsonify
from src.repositories.usuario_repository import UsuarioRepository

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('usuario') or not data.get('contrasenia'):
        return jsonify({
            "status": "ERROR",
            "mensaje": "Se requieren las credenciales (usuario/email y contraseña)"
        }), 400

    identificador = data.get('usuario')
    clave_ingresada = data.get('contrasenia')

    # Buscar usuario en DB
    usuario = UsuarioRepository.obtener_por_usuario_o_email(identificador)

    if not usuario:
        return jsonify({"status": "ERROR", "mensaje": "Usuario o contraseña incorrectos"}), 401

    if not usuario['usuario_activo'] or not usuario['persona_activa']:
        return jsonify({"status": "ERROR", "mensaje": "La cuenta se encuentra inactiva"}), 403

    # Verificación básica de contraseña (luego integraremos werkzeug/bcrypt)
    if usuario['contrasenia'] != clave_ingresada:
        return jsonify({"status": "ERROR", "mensaje": "Usuario o contraseña incorrectos"}), 401

    # Respuesta exitosa con datos de sesión
    return jsonify({
        "status": "OK",
        "mensaje": "Inicio de sesión exitoso",
        "usuario": {
            "id": usuario['usuario_id'],
            "persona_id": usuario['persona_id'],
            "usuario": usuario['usuario'],
            "nombre": usuario['nombre'],
            "apellido": usuario['apellido'],
            "email": usuario['email'],
            "rol": usuario['rol'],
            "avatar": usuario['avatar']
        }
    }), 200