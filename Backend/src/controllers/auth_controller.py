from flask import Blueprint, request, jsonify
import bcrypt
from src.repositories.usuario_repository import UsuarioRepository


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "ERROR",
            "mensaje": "No se recibieron datos"
        }), 400

    campos_obligatorios = [
        "dni",
        "nombre",
        "apellido",
        "email",
        "usuario",
        "contrasenia",
        "centro_id",
        "profesor_id",
        "fecha_inicio"
    ]

    campos_faltantes = [
        campo
        for campo in campos_obligatorios
        if not data.get(campo)
    ]

    if campos_faltantes:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Faltan campos obligatorios",
            "campos": campos_faltantes
        }), 400

    try:

        # ---------------------------------------------
        # Verificar usuario/email existentes
        # ---------------------------------------------

        usuario_existente = (
            UsuarioRepository
            .obtener_por_usuario_o_email(data["usuario"])
        )

        if usuario_existente:

            return jsonify({
                "status": "ERROR",
                "mensaje": "El usuario ya existe"
            }), 409

        email_existente = (
            UsuarioRepository
            .obtener_por_usuario_o_email(data["email"])
        )

        if email_existente:

            return jsonify({
                "status": "ERROR",
                "mensaje": "El email ya está registrado"
            }), 409

        # ---------------------------------------------
        # Hash de contraseña
        # ---------------------------------------------

        password_hash = bcrypt.hashpw(
            data["contrasenia"].encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # ---------------------------------------------
        # Registrar alumno
        # ---------------------------------------------

        nuevo_usuario = UsuarioRepository.registrar_alumno({
            "dni": data["dni"],
            "nombre": data["nombre"],
            "apellido": data["apellido"],
            "email": data["email"],
            "telefono": data.get("telefono"),
            "fecha_nacimiento": data.get("fecha_nacimiento"),
            "contacto_emergencia": data.get("contacto_emergencia"),

            "usuario": data["usuario"],
            "contrasenia": password_hash,

            "centro_id": data["centro_id"],
            "profesor_id": data["profesor_id"],
            "fecha_inicio": data["fecha_inicio"]
        })

        return jsonify({
            "status": "OK",
            "mensaje": "Alumno registrado correctamente",
            "usuario": nuevo_usuario
        }), 201

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo registrar el usuario",
            "detalle": str(e)
        }), 500



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

    usuario = UsuarioRepository.obtener_por_usuario_o_email(
        identificador
    )

    if not usuario:
        return jsonify({
            "status": "ERROR",
            "mensaje": "Usuario o contraseña incorrectos"
        }), 401

    if not usuario['usuario_activo'] or not usuario['persona_activa']:
        return jsonify({
            "status": "ERROR",
            "mensaje": "La cuenta se encuentra inactiva"
        }), 403

    contraseña_valida = bcrypt.checkpw(
        clave_ingresada.encode('utf-8'),
        usuario['contrasenia'].encode('utf-8')
    )

    if not contraseña_valida:
        return jsonify({
            "status": "ERROR",
            "mensaje": "Usuario o contraseña incorrectos"
        }), 401

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

