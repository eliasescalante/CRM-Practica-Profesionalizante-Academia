
from flask import Blueprint, request, jsonify
import bcrypt

from src.repositories.usuario_repository import UsuarioRepository
from src.utils.auth import token_required


perfil_bp = Blueprint(
    "perfil",
    __name__,
    url_prefix="/api/perfil"
)


@perfil_bp.route("", methods=["GET"])
@token_required
def obtener_perfil():
    usuario_token = request.usuario

    try:
        perfil = UsuarioRepository.obtener_perfil_por_id(
            usuario_token["usuario_id"]
        )

        if not perfil:
            return jsonify({
                "status": "ERROR",
                "mensaje": "Usuario no encontrado"
            }), 404

        if not perfil["usuario_activo"] or not perfil["persona_activa"]:
            return jsonify({
                "status": "ERROR",
                "mensaje": "La cuenta se encuentra inactiva"
            }), 403

        return jsonify({
            "status": "OK",
            "perfil": perfil
        }), 200

    except Exception as e:
        print("ERROR AL OBTENER PERFIL:", repr(e))
        return jsonify({
            "status": "ERROR",
            "mensaje": "Error al obtener el perfil"
        }), 500


@perfil_bp.route("", methods=["PUT"])
@token_required
def actualizar_perfil():
    usuario_token = request.usuario
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or not datos:
        return jsonify({
            "status": "ERROR",
            "mensaje": "Se deben enviar los datos a actualizar"
        }), 400

    campos_permitidos = {
        "nombre",
        "apellido",
        "email",
        "telefono",
        "fecha_nacimiento",
        "contacto_emergencia"
    }

    campos_invalidos = set(datos.keys()) - campos_permitidos

    if campos_invalidos:
        return jsonify({
            "status": "ERROR",
            "mensaje": "Se enviaron campos no permitidos",
            "campos": sorted(campos_invalidos)
        }), 400

    for campo in ("nombre", "apellido", "email"):
        if campo in datos and (
            not isinstance(datos[campo], str) or not datos[campo].strip()
        ):
            return jsonify({
                "status": "ERROR",
                "mensaje": f"El campo {campo} no puede estar vacío"
            }), 400

    if "email" in datos:
        datos["email"] = datos["email"].strip()

    try:
        actualizado = UsuarioRepository.actualizar_perfil(
            usuario_token["usuario_id"],
            datos
        )

        if actualizado is None:
            return jsonify({
                "status": "ERROR",
                "mensaje": "Usuario no encontrado"
            }), 404

        if not actualizado:
            return jsonify({
                "status": "ERROR",
                "mensaje": "No hay datos válidos para actualizar"
            }), 400

        perfil = UsuarioRepository.obtener_perfil_por_id(
            usuario_token["usuario_id"]
        )

        return jsonify({
            "status": "OK",
            "mensaje": "Perfil actualizado correctamente",
            "perfil": perfil
        }), 200

    except ValueError as e:
        if str(e) == "EMAIL_EXISTENTE":
            return jsonify({
                "status": "ERROR",
                "mensaje": "El email ya está registrado"
            }), 409
        raise

    except Exception:
        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo actualizar el perfil"
        }), 500


@perfil_bp.route("/password", methods=["PUT"])
@token_required
def cambiar_contrasenia():
    usuario_id = request.usuario["usuario_id"]
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "status": "ERROR",
            "mensaje": "Se deben enviar las contraseñas"
        }), 400

    contrasenia_actual = datos.get("contrasenia_actual")
    contrasenia_nueva = datos.get("contrasenia_nueva")

    if not contrasenia_actual or not contrasenia_nueva:
        return jsonify({
            "status": "ERROR",
            "mensaje": "Se requiere la contraseña actual y la nueva"
        }), 400

    if not isinstance(contrasenia_actual, str) or not isinstance(
        contrasenia_nueva, str
    ):
        return jsonify({
            "status": "ERROR",
            "mensaje": "Las contraseñas deben ser texto"
        }), 400

    if len(contrasenia_nueva) < 8:
        return jsonify({
            "status": "ERROR",
            "mensaje": "La nueva contraseña debe tener al menos 8 caracteres"
        }), 400

    try:
        hash_actual = UsuarioRepository.obtener_hash_contrasenia(usuario_id)

        if not hash_actual:
            return jsonify({
                "status": "ERROR",
                "mensaje": "Usuario no encontrado"
            }), 404

        if not bcrypt.checkpw(
            contrasenia_actual.encode("utf-8"),
            hash_actual.encode("utf-8")
        ):
            return jsonify({
                "status": "ERROR",
                "mensaje": "La contraseña actual es incorrecta"
            }), 401

        nuevo_hash = bcrypt.hashpw(
            contrasenia_nueva.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        actualizado = UsuarioRepository.actualizar_contrasenia(
            usuario_id,
            nuevo_hash
        )

        if not actualizado:
            return jsonify({
                "status": "ERROR",
                "mensaje": "No se pudo actualizar la contraseña"
            }), 404

        return jsonify({
            "status": "OK",
            "mensaje": "Contraseña actualizada correctamente"
        }), 200

    except Exception:
        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo cambiar la contraseña"
        }), 500
