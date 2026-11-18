#agregado al docs
import os

from flask import Blueprint, request, jsonify
import bcrypt
from datetime import date
from src.repositories.usuario_repository import UsuarioRepository
from src.repositories.profesor_repository import ProfesorRepository
from src.utils.auth import generar_token, token_required


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

    # ---------------------------------------------
    # Validar contraseña (misma regla que PUT /api/perfil/password)
    # ---------------------------------------------

    if (
        not isinstance(data["contrasenia"], str)
        or len(data["contrasenia"]) < 8
    ):

        return jsonify({
            "status": "ERROR",
            "mensaje": "La contraseña debe tener al menos 8 caracteres"
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


# =========================================================
# POST /api/auth/register-profesor
# Auto-registro público de profesor: queda PENDIENTE
# de habilitación por un administrador.
# =========================================================

@auth_bp.route("/register-profesor", methods=["POST"])
def register_profesor():

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se recibieron datos"
        }), 400

    # Normalizamos los campos de identidad (sin tocar la contraseña)
    for campo in ("dni", "nombre", "apellido", "email", "usuario"):

        if isinstance(data.get(campo), str):
            data[campo] = data[campo].strip()

    campos_obligatorios = [
        "dni",
        "nombre",
        "apellido",
        "email",
        "usuario",
        "contrasenia"
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

    # ---------------------------------------------
    # Validar contraseña (misma regla que register)
    # ---------------------------------------------

    if (
        not isinstance(data["contrasenia"], str)
        or len(data["contrasenia"]) < 8
    ):

        return jsonify({
            "status": "ERROR",
            "mensaje": "La contraseña debe tener al menos 8 caracteres"
        }), 400

    try:

        # ---------------------------------------------
        # Verificar DNI / email / usuario existentes
        # ---------------------------------------------

        if ProfesorRepository.obtener_por_dni(data["dni"]):

            return jsonify({
                "status": "ERROR",
                "mensaje": "El DNI ya está registrado"
            }), 409

        if ProfesorRepository.obtener_por_email(data["email"]):

            return jsonify({
                "status": "ERROR",
                "mensaje": "El email ya está registrado"
            }), 409

        if ProfesorRepository.obtener_por_usuario(data["usuario"]):

            return jsonify({
                "status": "ERROR",
                "mensaje": "El usuario ya está registrado"
            }), 409

        # ---------------------------------------------
        # Hash de contraseña
        # ---------------------------------------------

        password_hash = bcrypt.hashpw(
            data["contrasenia"].encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        # ---------------------------------------------
        # Crear SIEMPRE un PROFESOR inactivo.
        # El rol, el estado y los centros los define
        # el ADMIN al habilitar la cuenta.
        # ---------------------------------------------

        nuevo_profesor = ProfesorRepository.crear({

            "dni": data["dni"],
            "nombre": data["nombre"],
            "apellido": data["apellido"],
            "email": data["email"],

            "telefono": data.get("telefono"),
            "fecha_nacimiento": data.get("fecha_nacimiento"),
            "contacto_emergencia": data.get("contacto_emergencia"),

            "usuario": data["usuario"],
            "contrasenia": password_hash,

            "rol": "PROFESOR",
            "activo": False,
            "fecha_alta": date.today().isoformat(),
            "centro_ids": []
        })

        return jsonify({
            "status": "OK",
            "mensaje": (
                "Registro recibido. Un administrador debe habilitar "
                "la cuenta para que puedas iniciar sesión."
            ),
            "profesor": nuevo_profesor
        }), 201

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo registrar el profesor",
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

        mensaje = "La cuenta se encuentra inactiva"

        if usuario['rol'] == 'PROFESOR':
            mensaje = (
                "La cuenta está inactiva o pendiente de habilitación "
                "por un administrador"
            )

        return jsonify({
            "status": "ERROR",
            "mensaje": mensaje
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

    token = generar_token(usuario)

    return jsonify({
        "status": "OK",
        "mensaje": "Inicio de sesión exitoso",

        "token": token,

        "usuario": {
            "id": usuario["usuario_id"],
            "persona_id": usuario["persona_id"],
            "alumno_id": usuario.get("alumno_id"),
            "profesor_id": usuario.get("profesor_id"),
            "usuario": usuario["usuario"],
            "nombre": usuario["nombre"],
            "apellido": usuario["apellido"],
            "email": usuario["email"],
            "rol": usuario["rol"],
            "avatar": usuario["avatar"]
        }
    }), 200

    
@auth_bp.route("/me", methods=["GET"])
@token_required
def obtener_usuario_autenticado():
    usuario_token = request.usuario

    try:
        usuario = UsuarioRepository.obtener_por_id(
            usuario_token["usuario_id"]
        )

        if not usuario:
            return jsonify({
                "status": "ERROR",
                "mensaje": "El usuario ya no existe"
            }), 401

        if not usuario["usuario_activo"] or not usuario["persona_activa"]:
            return jsonify({
                "status": "ERROR",
                "mensaje": "La cuenta se encuentra inactiva"
            }), 403

        return jsonify({
            "status": "OK",
            "mensaje": "Usuario autenticado",
            "usuario": {
                "id": usuario["usuario_id"],
                "persona_id": usuario["persona_id"],
                "alumno_id": usuario.get("alumno_id"),
                "profesor_id": usuario.get("profesor_id"),
                "usuario": usuario["usuario"],
                "nombre": usuario["nombre"],
                "apellido": usuario["apellido"],
                "email": usuario["email"],
                "rol": usuario["rol"],
                "avatar": usuario["avatar"]
            }
        }), 200

    except Exception:
        return jsonify({
            "status": "ERROR",
            "mensaje": "Error al obtener el usuario autenticado"
        }), 500


# =========================================================
# INICIO DE SESIÓN CON GOOGLE
# ---------------------------------------------------------
# El frontend obtiene un ID token con Google Identity Services y
# lo manda acá. Validamos la firma y el audience contra
# GOOGLE_CLIENT_ID y buscamos una cuenta del CRM con ese email.
#
# Si el email todavía no tiene cuenta, la creamos como alumno
# provisorio con lo que informa Google (nombre, apellido, email y
# foto). La ficha se completa con la primera sede y el primer
# profesor activos, la fecha de hoy y un DNI generado (G-...).
# Se puede desactivar con GOOGLE_AUTO_ALTA=0.
# =========================================================

def _usuario_publico(usuario):
    return {
        "id": usuario["usuario_id"],
        "persona_id": usuario["persona_id"],
        "alumno_id": usuario.get("alumno_id"),
        "profesor_id": usuario.get("profesor_id"),
        "usuario": usuario["usuario"],
        "nombre": usuario["nombre"],
        "apellido": usuario["apellido"],
        "email": usuario["email"],
        "rol": usuario["rol"],
        "avatar": usuario["avatar"]
    }


def _mensaje_cuenta_inactiva(usuario):

    if usuario.get("rol") == "PROFESOR":
        return (
            "La cuenta está inactiva o pendiente de habilitación "
            "por un administrador"
        )

    return "La cuenta se encuentra inactiva"


def _auto_alta_google_habilitada():

    valor = (os.getenv("GOOGLE_AUTO_ALTA") or "1").strip().lower()

    return valor not in ("0", "false", "no", "off")


def _nombre_google(informacion, email):

    nombre = (informacion.get("given_name") or "").strip()
    apellido = (informacion.get("family_name") or "").strip()

    if not nombre and not apellido:
        nombre = email.split("@")[0]

    return nombre, apellido


@auth_bp.route("/google/config", methods=["GET"])
def google_config():

    client_id = os.getenv("GOOGLE_CLIENT_ID")

    return jsonify({
        "status": "OK",
        "habilitado": bool(client_id),
        "client_id": client_id or None,
        "auto_alta": _auto_alta_google_habilitada()
    }), 200


@auth_bp.route("/google", methods=["POST"])
def login_google():

    data = request.get_json(silent=True) or {}
    credential = data.get("credential")

    if not isinstance(credential, str) or not credential.strip():

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se recibió el token de Google"
        }), 400

    client_id = os.getenv("GOOGLE_CLIENT_ID")

    if not client_id:

        return jsonify({
            "status": "ERROR",
            "mensaje": (
                "El inicio de sesión con Google todavía no está "
                "configurado en el servidor"
            )
        }), 503

    try:

        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token

        informacion = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            client_id
        )

    except ImportError:

        return jsonify({
            "status": "ERROR",
            "mensaje": (
                "Falta la dependencia google-auth en el servidor. "
                "Instalá Backend/requirements.txt"
            )
        }), 503

    except ValueError:

        return jsonify({
            "status": "ERROR",
            "mensaje": (
                "No pudimos validar tu cuenta de Google. "
                "Probá de nuevo o ingresá con usuario y contraseña."
            )
        }), 401

    except Exception:

        return jsonify({
            "status": "ERROR",
            "mensaje": (
                "No pudimos conectar con Google en este momento. "
                "Probá de nuevo en unos minutos."
            )
        }), 503

    email = (informacion.get("email") or "").strip()

    if not email:

        return jsonify({
            "status": "ERROR",
            "mensaje": "La cuenta de Google no informó un email"
        }), 401

    if not informacion.get("email_verified"):

        return jsonify({
            "status": "ERROR",
            "mensaje": (
                "El email de tu cuenta de Google no está verificado"
            )
        }), 403

    try:

        usuario = UsuarioRepository.obtener_por_usuario_o_email(email)

    except Exception:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo consultar la cuenta"
        }), 503

    cuenta_creada = False

    if not usuario:

        if not _auto_alta_google_habilitada():

            return jsonify({
                "status": "ERROR",
                "mensaje": (
                    "No hay una cuenta del CRM con el email " + email + ". "
                    "Pedile a la escuela que te dé de alta o ingresá con "
                    "usuario y contraseña."
                )
            }), 404

        nombre, apellido = _nombre_google(informacion, email)

        try:

            UsuarioRepository.registrar_desde_google({
                "nombre": nombre,
                "apellido": apellido,
                "email": email,
                "sub": informacion.get("sub"),
                "avatar": informacion.get("picture"),
                "contrasenia": bcrypt.hashpw(
                    os.urandom(24).hex().encode("utf-8"),
                    bcrypt.gensalt()
                ).decode("utf-8")
            })

            usuario = UsuarioRepository.obtener_por_usuario_o_email(email)
            cuenta_creada = True

        except ValueError:

            return jsonify({
                "status": "ERROR",
                "mensaje": (
                    "No hay una cuenta del CRM con el email " + email +
                    " y la escuela no tiene una sede y un profesor activos "
                    "para crear una ficha provisoria. Pedile al "
                    "administrador que te dé de alta."
                )
            }), 409

        except Exception:

            return jsonify({
                "status": "ERROR",
                "mensaje": (
                    "No hay una cuenta del CRM con el email " + email +
                    " y no pudimos crearla automáticamente. "
                    "Pedile a la escuela que te dé de alta."
                )
            }), 500

        if not usuario:

            return jsonify({
                "status": "ERROR",
                "mensaje": "No se pudo recuperar la cuenta recién creada"
            }), 500

    if not usuario["usuario_activo"] or not usuario["persona_activa"]:

        return jsonify({
            "status": "ERROR",
            "mensaje": _mensaje_cuenta_inactiva(usuario)
        }), 403

    try:

        token = generar_token(usuario)

    except Exception:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo generar la sesión"
        }), 500

    if cuenta_creada:
        mensaje = (
            "Cuenta creada con Google. Podés completar tus datos y definir "
            "una contraseña desde Mi perfil."
        )
    else:
        mensaje = "Inicio de sesión exitoso"

    return jsonify({
        "status": "OK",
        "mensaje": mensaje,
        "cuenta_creada": cuenta_creada,
        "token": token,
        "usuario": _usuario_publico(usuario)
    }), 200

