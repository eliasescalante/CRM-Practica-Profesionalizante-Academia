from flask import Blueprint, request, jsonify
import bcrypt

from src.repositories.profesor_repository import ProfesorRepository


profesor_bp = Blueprint(
    "profesores",
    __name__,
    url_prefix="/api/profesores"
)


# =========================================================
# GET /api/profesores
# Listar profesores
# =========================================================

@profesor_bp.route("", methods=["GET"])
def listar_profesores():

    try:

        incluir_inactivos = (
            request.args.get("todos", "false").lower() == "true"
        )

        profesores = ProfesorRepository.listar(
            incluir_inactivos=incluir_inactivos
        )

        return jsonify({
            "status": "OK",
            "cantidad": len(profesores),
            "profesores": profesores
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudieron obtener los profesores",
            "detalle": str(e)
        }), 500


# =========================================================
# GET /api/profesores/<id>
# Obtener profesor
# =========================================================

@profesor_bp.route("/<int:profesor_id>", methods=["GET"])
def obtener_profesor(profesor_id):

    try:

        profesor = ProfesorRepository.obtener_por_id(
            profesor_id
        )

        if not profesor:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Profesor no encontrado"
            }), 404

        return jsonify({
            "status": "OK",
            "profesor": profesor
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo obtener el profesor",
            "detalle": str(e)
        }), 500


# =========================================================
# POST /api/profesores
# Crear profesor
# =========================================================

@profesor_bp.route("", methods=["POST"])
def crear_profesor():

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
        "contrasenia"
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


    try:

        # -------------------------------------------------
        # VALIDAR DNI
        # -------------------------------------------------

        if ProfesorRepository.obtener_por_dni(data["dni"]):

            return jsonify({
                "status": "ERROR",
                "mensaje": "El DNI ya está registrado"
            }), 409


        # -------------------------------------------------
        # VALIDAR EMAIL
        # -------------------------------------------------

        if ProfesorRepository.obtener_por_email(data["email"]):

            return jsonify({
                "status": "ERROR",
                "mensaje": "El email ya está registrado"
            }), 409


        # -------------------------------------------------
        # VALIDAR USUARIO
        # -------------------------------------------------

        if ProfesorRepository.obtener_por_usuario(data["usuario"]):

            return jsonify({
                "status": "ERROR",
                "mensaje": "El usuario ya está registrado"
            }), 409


        # -------------------------------------------------
        # HASH PASSWORD
        # -------------------------------------------------

        password_hash = bcrypt.hashpw(
            data["contrasenia"].encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")


        # -------------------------------------------------
        # DATOS
        # -------------------------------------------------

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

            "fecha_alta": data.get("fecha_alta"),

            "centro_ids": data.get("centro_ids", [])
        }


        nuevo_profesor = ProfesorRepository.crear(datos)


        return jsonify({
            "status": "OK",
            "mensaje": "Profesor creado correctamente",
            "profesor": nuevo_profesor
        }), 201


    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo crear el profesor",
            "detalle": str(e)
        }), 500


# =========================================================
# PUT /api/profesores/<id>
# Actualizar profesor
# =========================================================

@profesor_bp.route("/<int:profesor_id>", methods=["PUT"])
def actualizar_profesor(profesor_id):

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
        "activo"
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


    try:

        # -------------------------------------------------
        # EXISTENCIA
        # -------------------------------------------------

        profesor = ProfesorRepository.obtener_por_id(
            profesor_id
        )

        if not profesor:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Profesor no encontrado"
            }), 404


        # -------------------------------------------------
        # DATOS
        # -------------------------------------------------

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

            "activo": data["activo"],

            "centro_ids": data.get("centro_ids")
        }


        actualizado = ProfesorRepository.actualizar(
            profesor_id,
            datos
        )


        if not actualizado:

            return jsonify({
                "status": "ERROR",
                "mensaje": "No se pudo actualizar el profesor"
            }), 400


        return jsonify({
            "status": "OK",
            "mensaje": "Profesor actualizado correctamente"
        }), 200


    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo actualizar el profesor",
            "detalle": str(e)
        }), 500


# =========================================================
# DELETE /api/profesores/<id>
# Baja lógica
# =========================================================

@profesor_bp.route("/<int:profesor_id>", methods=["DELETE"])
def eliminar_profesor(profesor_id):

    try:

        profesor = ProfesorRepository.obtener_por_id(
            profesor_id
        )

        if not profesor:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Profesor no encontrado"
            }), 404


        eliminado = ProfesorRepository.eliminar(
            profesor_id
        )


        if not eliminado:

            return jsonify({
                "status": "ERROR",
                "mensaje": "No se pudo dar de baja el profesor"
            }), 400


        return jsonify({
            "status": "OK",
            "mensaje": "Profesor dado de baja correctamente"
        }), 200


    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo eliminar el profesor",
            "detalle": str(e)
        }), 500