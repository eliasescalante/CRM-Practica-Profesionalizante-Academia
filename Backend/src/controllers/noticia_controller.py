#agregado al docs
from flask import Blueprint, request, jsonify

from src.repositories.noticia_repository import NoticiaRepository
from src.utils.auth import token_required, roles_required
from src.utils.permisos import denegado, es_admin, exigir_centro


noticia_bp = Blueprint(
    "noticias",
    __name__,
    url_prefix="/api/noticias"
)


def sede_permitida(usuario, centro_id):
    """El ADMIN publica en cualquier sede (o general); el PROFESOR solo en las suyas.

    Devuelve una respuesta 403 o None.
    """

    if es_admin(usuario):

        return None

    if centro_id in (None, "", 0):

        return denegado(
            "Solo un administrador puede publicar novedades generales"
        )

    return exigir_centro(usuario, centro_id)


# =========================================================
# GET /api/noticias
# Listar noticias
# =========================================================

@noticia_bp.route("", methods=["GET"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def listar_noticias():

    try:

        incluir_inactivas = (
            request.args.get("todos", "false").lower() == "true"
            and request.usuario.get("rol") in ("ADMIN", "PROFESOR")
        )

        noticias = NoticiaRepository.listar(
            incluir_inactivas=incluir_inactivas
        )

        return jsonify({
            "status": "OK",
            "cantidad": len(noticias),
            "noticias": noticias
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudieron obtener las noticias",
            "detalle": str(e)
        }), 500


# =========================================================
# GET /api/noticias/<id>
# Obtener noticia
# =========================================================

@noticia_bp.route("/<int:noticia_id>", methods=["GET"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def obtener_noticia(noticia_id):

    try:

        noticia = NoticiaRepository.obtener_por_id(noticia_id)

        if not noticia:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Noticia no encontrada"
            }), 404

        return jsonify({
            "status": "OK",
            "noticia": noticia
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo obtener la noticia",
            "detalle": str(e)
        }), 500


# =========================================================
# GET /api/noticias/centro/<centro_id>
# Noticias de un centro + generales
# =========================================================

@noticia_bp.route("/centro/<int:centro_id>", methods=["GET"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def listar_noticias_centro(centro_id):

    try:

        noticias = NoticiaRepository.listar_por_centro(centro_id)

        return jsonify({
            "status": "OK",
            "cantidad": len(noticias),
            "noticias": noticias
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudieron obtener las noticias del centro",
            "detalle": str(e)
        }), 500


# =========================================================
# POST /api/noticias
# Crear noticia
# =========================================================

@noticia_bp.route("", methods=["POST"])
@token_required
@roles_required("PROFESOR", "ADMIN")
def crear_noticia():

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se recibieron datos"
        }), 400

    campos_obligatorios = [
        "titulo",
        "contenido"
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

    # El autor siempre es el usuario autenticado: no se acepta del body.
    data["autor_usuario_id"] = request.usuario["usuario_id"]

    sin_permiso = sede_permitida(
        request.usuario,
        data.get("centro_id")
    )

    if sin_permiso:

        return sin_permiso

    try:

        noticia_id = NoticiaRepository.crear(data)

        noticia = NoticiaRepository.obtener_por_id(noticia_id)

        return jsonify({
            "status": "OK",
            "mensaje": "Noticia creada correctamente",
            "noticia": noticia
        }), 201

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo crear la noticia",
            "detalle": str(e)
        }), 500


# =========================================================
# PUT /api/noticias/<id>
# Actualizar noticia
# =========================================================

@noticia_bp.route("/<int:noticia_id>", methods=["PUT"])
@token_required
@roles_required("PROFESOR", "ADMIN")
def actualizar_noticia(noticia_id):

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se recibieron datos"
        }), 400

    campos_obligatorios = [
        "titulo",
        "contenido"
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

    existente = NoticiaRepository.obtener_por_id(noticia_id)

    if not existente:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Noticia no encontrada"
        }), 404

    nuevo_centro = (
        data["centro_id"]
        if "centro_id" in data
        else existente.get("centro_id")
    )

    sin_permiso = (
        sede_permitida(request.usuario, existente.get("centro_id"))
        or sede_permitida(request.usuario, nuevo_centro)
    )

    if sin_permiso:

        return sin_permiso

    try:

        actualizado = NoticiaRepository.actualizar(
            noticia_id,
            data
        )

        if not actualizado:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Noticia no encontrada"
            }), 404

        noticia = NoticiaRepository.obtener_por_id(noticia_id)

        return jsonify({
            "status": "OK",
            "mensaje": "Noticia actualizada correctamente",
            "noticia": noticia
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo actualizar la noticia",
            "detalle": str(e)
        }), 500


# =========================================================
# DELETE /api/noticias/<id>
# Desactivar noticia
# =========================================================

@noticia_bp.route("/<int:noticia_id>", methods=["DELETE"])
@token_required
@roles_required("PROFESOR", "ADMIN")
def eliminar_noticia(noticia_id):

    try:

        existente = NoticiaRepository.obtener_por_id(noticia_id)

        if not existente:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Noticia no encontrada"
            }), 404

        sin_permiso = sede_permitida(
            request.usuario,
            existente.get("centro_id")
        )

        if sin_permiso:

            return sin_permiso

        desactivada = NoticiaRepository.desactivar(noticia_id)

        if not desactivada:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Noticia no encontrada"
            }), 404

        return jsonify({
            "status": "OK",
            "mensaje": "Noticia desactivada correctamente"
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo desactivar la noticia",
            "detalle": str(e)
        }), 500