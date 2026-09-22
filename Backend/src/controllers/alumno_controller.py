from flask import Blueprint, request, jsonify
import bcrypt

from src.repositories.alumno_repository import AlumnoRepository


alumno_bp = Blueprint(
    "alumnos",
    __name__,
    url_prefix="/api/alumnos"
)


# =========================================================
# GET /api/alumnos
# Listar alumnos
# =========================================================

@alumno_bp.route("", methods=["GET"])
def listar_alumnos():

    try:

        incluir_inactivos = (
            request.args.get("todos", "false").lower() == "true"
        )

        alumnos = AlumnoRepository.listar(
            incluir_inactivos=incluir_inactivos
        )

        return jsonify({
            "status": "OK",
            "cantidad": len(alumnos),
            "alumnos": alumnos
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudieron obtener los alumnos",
            "detalle": str(e)
        }), 500


# =========================================================
# GET /api/alumnos/<id>
# Obtener alumno
# =========================================================

@alumno_bp.route("/<int:alumno_id>", methods=["GET"])
def obtener_alumno(alumno_id):

    try:

        alumno = AlumnoRepository.obtener_por_id(alumno_id)

        if not alumno:
            return jsonify({
                "status": "ERROR",
                "mensaje": "Alumno no encontrado"
            }), 404

        return jsonify({
            "status": "OK",
            "alumno": alumno
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo obtener el alumno",
            "detalle": str(e)
        }), 500


# =========================================================
# POST /api/alumnos
# Crear alumno
# =========================================================

@alumno_bp.route("", methods=["POST"])
def crear_alumno():

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
        "fecha_de_inicio"
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
        # Validar DNI
        # ---------------------------------------------

        if AlumnoRepository.obtener_por_dni(data["dni"]):

            return jsonify({
                "status": "ERROR",
                "mensaje": "El DNI ya está registrado"
            }), 409

        # ---------------------------------------------
        # Validar email
        # ---------------------------------------------

        if AlumnoRepository.obtener_por_email(data["email"]):

            return jsonify({
                "status": "ERROR",
                "mensaje": "El email ya está registrado"
            }), 409

        # ---------------------------------------------
        # Validar usuario
        # ---------------------------------------------

        if AlumnoRepository.obtener_por_usuario(data["usuario"]):

            return jsonify({
                "status": "ERROR",
                "mensaje": "El usuario ya está registrado"
            }), 409

        # ---------------------------------------------
        # Hash contraseña
        # ---------------------------------------------

        password_hash = bcrypt.hashpw(
            data["contrasenia"].encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        datos = {
            "dni": data["dni"],
            "nombre": data["nombre"],
            "apellido": data["apellido"],
            "email": data["email"],
            "telefono": data.get("telefono"),
            "fecha_nacimiento": data.get("fecha_nacimiento"),
            "contacto_emergencia": data.get("contacto_emergencia"),
            "avatar": data.get("avatar"),

            "usuario": data["usuario"],
            "contrasenia": password_hash,

            "centro_id": data["centro_id"],
            "profesor_id": data["profesor_id"],
            "fecha_de_inicio": data["fecha_de_inicio"]
        }

        nuevo_alumno = AlumnoRepository.crear(datos)

        return jsonify({
            "status": "OK",
            "mensaje": "Alumno creado correctamente",
            "alumno": nuevo_alumno
        }), 201

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo crear el alumno",
            "detalle": str(e)
        }), 500


# =========================================================
# PUT /api/alumnos/<id>
# Actualizar alumno
# =========================================================

@alumno_bp.route("/<int:alumno_id>", methods=["PUT"])
def actualizar_alumno(alumno_id):

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
        "centro_id",
        "profesor_id",
        "fecha_de_inicio",
        "estado"
    ]

    campos_faltantes = [
        campo
        for campo in campos_obligatorios
        if campo not in data
    ]

    if campos_faltantes:
        return jsonify({
            "status": "ERROR",
            "mensaje": "Faltan campos obligatorios",
            "campos": campos_faltantes
        }), 400

    estados_validos = [
        "ACTIVO",
        "PAUSADO",
        "INACTIVO"
    ]

    if data["estado"] not in estados_validos:
        return jsonify({
            "status": "ERROR",
            "mensaje": "Estado de alumno inválido",
            "estados_validos": estados_validos
        }), 400

    try:

        alumno = AlumnoRepository.obtener_por_id(alumno_id)

        if not alumno:
            return jsonify({
                "status": "ERROR",
                "mensaje": "Alumno no encontrado"
            }), 404

        datos = {
            "dni": data["dni"],
            "nombre": data["nombre"],
            "apellido": data["apellido"],
            "email": data["email"],
            "telefono": data.get("telefono"),
            "fecha_nacimiento": data.get("fecha_nacimiento"),
            "contacto_emergencia": data.get("contacto_emergencia"),
            "avatar": data.get("avatar"),

            "usuario": data["usuario"],

            "centro_id": data["centro_id"],
            "profesor_id": data["profesor_id"],
            "fecha_de_inicio": data["fecha_de_inicio"],
            "estado": data["estado"]
        }

        actualizado = AlumnoRepository.actualizar(
            alumno_id,
            datos
        )

        if not actualizado:
            return jsonify({
                "status": "ERROR",
                "mensaje": "No se pudo actualizar el alumno"
            }), 400

        alumno_actualizado = (
            AlumnoRepository.obtener_por_id(alumno_id)
        )

        return jsonify({
            "status": "OK",
            "mensaje": "Alumno actualizado correctamente",
            "alumno": alumno_actualizado
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo actualizar el alumno",
            "detalle": str(e)
        }), 500


# =========================================================
# DELETE /api/alumnos/<id>
# Baja lógica
# =========================================================

@alumno_bp.route("/<int:alumno_id>", methods=["DELETE"])
def eliminar_alumno(alumno_id):

    try:

        alumno = AlumnoRepository.obtener_por_id(alumno_id)

        if not alumno:
            return jsonify({
                "status": "ERROR",
                "mensaje": "Alumno no encontrado"
            }), 404

        eliminado = AlumnoRepository.eliminar(alumno_id)

        if not eliminado:
            return jsonify({
                "status": "ERROR",
                "mensaje": "No se pudo dar de baja el alumno"
            }), 400

        return jsonify({
            "status": "OK",
            "mensaje": "Alumno dado de baja correctamente"
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo eliminar el alumno",
            "detalle": str(e)
        }), 500