#ya agregado a docs
from flask import Blueprint, request, jsonify

from src.repositories.chat_repository import ChatRepository
from src.utils.auth import token_required, roles_required


# =========================================================
# BLUEPRINT
# =========================================================

chat_bp = Blueprint(
    "chat",
    __name__,
    url_prefix="/api/chat"
)


# =========================================================
# LISTAR MENSAJES DE UN CENTRO
# =========================================================

@chat_bp.route("/centro/<int:centro_id>", methods=["GET"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def listar_mensajes_centro(centro_id):

    try:

        mensajes = ChatRepository.listar_por_centro(centro_id)

        return jsonify({
            "status": "OK",
            "cantidad": len(mensajes),
            "mensajes": mensajes
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudieron obtener los mensajes",
            "detalle": str(e)
        }), 500


# =========================================================
# OBTENER UN MENSAJE
# =========================================================

@chat_bp.route("/<int:mensaje_id>", methods=["GET"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def obtener_mensaje(mensaje_id):

    try:

        mensaje = ChatRepository.obtener_por_id(mensaje_id)

        if not mensaje:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Mensaje no encontrado"
            }), 404

        return jsonify({
            "status": "OK",
            "mensaje": mensaje
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo obtener el mensaje",
            "detalle": str(e)
        }), 500


# =========================================================
# CREAR MENSAJE
# =========================================================

@chat_bp.route("", methods=["POST"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def crear_mensaje():

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se recibieron datos"
        }), 400


    campos_obligatorios = [
        "centro_id",
        "emisor_persona_id",
        "mensaje"
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


    # El emisor siempre es el usuario autenticado: evita que un usuario
    # publique mensajes haciéndose pasar por otra persona.
    data["emisor_persona_id"] = request.usuario["persona_id"]


    try:

        mensaje_id = ChatRepository.crear(data)

        mensaje_creado = ChatRepository.obtener_por_id(
            mensaje_id
        )


        return jsonify({
            "status": "OK",
            "mensaje": "Mensaje enviado correctamente",
            "chat": mensaje_creado
        }), 201


    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo enviar el mensaje",
            "detalle": str(e)
        }), 500


# =========================================================
# ELIMINAR MENSAJE
# =========================================================

@chat_bp.route("/<int:mensaje_id>", methods=["DELETE"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def eliminar_mensaje(mensaje_id):

    try:

        mensaje = ChatRepository.obtener_por_id(mensaje_id)

        if not mensaje:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Mensaje no encontrado"
            }), 404


        # Solo el autor del mensaje o un ADMIN pueden eliminarlo.
        usuario_token = request.usuario

        es_autor = (
            mensaje["emisor_persona_id"] == usuario_token["persona_id"]
        )
        es_admin = usuario_token["rol"] == "ADMIN"

        if not (es_autor or es_admin):

            return jsonify({
                "status": "ERROR",
                "mensaje": "No tiene permiso para eliminar este mensaje"
            }), 403


        eliminado = ChatRepository.eliminar(mensaje_id)


        if not eliminado:

            return jsonify({
                "status": "ERROR",
                "mensaje": "No se pudo eliminar el mensaje"
            }), 400


        return jsonify({
            "status": "OK",
            "mensaje": "Mensaje eliminado correctamente"
        }), 200


    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo eliminar el mensaje",
            "detalle": str(e)
        }), 500

