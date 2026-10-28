# ya incluido en docs
from flask import Blueprint, request, jsonify

from src.repositories.asistencia_repository import AsistenciaRepository
from src.utils.auth import token_required, roles_required
from src.utils.permisos import (
    es_alumno,
    exigir_alumno_propio,
    exigir_centro
)


asistencia_bp = Blueprint(
    "asistencias",
    __name__,
    url_prefix="/api/asistencias"
)


# =========================================================
# GET /api/asistencias
# Listar asistencias
# =========================================================

@asistencia_bp.route("", methods=["GET"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def listar_asistencias():

    try:

        usuario = request.usuario

        if es_alumno(usuario):

            if not usuario.get("alumno_id"):

                return jsonify({
                    "status": "ERROR",
                    "mensaje": "Tu usuario no está asociado a un alumno"
                }), 403

            asistencias = AsistenciaRepository.listar_por_alumno(
                usuario["alumno_id"]
            )

        else:

            asistencias = AsistenciaRepository.listar()

        return jsonify({
            "status": "OK",
            "cantidad": len(asistencias),
            "asistencias": asistencias
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudieron obtener las asistencias",
            "detalle": str(e)
        }), 500


# =========================================================
# GET /api/asistencias/<id>
# Obtener asistencia
# =========================================================

@asistencia_bp.route("/<int:asistencia_id>", methods=["GET"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def obtener_asistencia(asistencia_id):

    try:

        asistencia = AsistenciaRepository.obtener_por_id(
            asistencia_id
        )

        if not asistencia:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Asistencia no encontrada"
            }), 404

        sin_permiso = exigir_alumno_propio(
            request.usuario,
            asistencia.get("alumno_id")
        )

        if sin_permiso:
            return sin_permiso

        return jsonify({
            "status": "OK",
            "asistencia": asistencia
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo obtener la asistencia",
            "detalle": str(e)
        }), 500


# =========================================================
# GET /api/asistencias/alumno/<id>
# Historial de asistencia de un alumno
# =========================================================

@asistencia_bp.route(
    "/alumno/<int:alumno_id>",
    methods=["GET"]
)
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def listar_asistencias_alumno(alumno_id):

    try:

        sin_permiso = exigir_alumno_propio(
            request.usuario,
            alumno_id
        )

        if sin_permiso:
            return sin_permiso

        asistencias = AsistenciaRepository.listar_por_alumno(
            alumno_id
        )

        return jsonify({
            "status": "OK",
            "cantidad": len(asistencias),
            "asistencias": asistencias
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo obtener el historial del alumno",
            "detalle": str(e)
        }), 500


# =========================================================
# GET /api/asistencias/centro/<id>
# Asistencias de un centro
# =========================================================

@asistencia_bp.route(
    "/centro/<int:centro_id>",
    methods=["GET"]
)
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def listar_asistencias_centro(centro_id):

    try:

        sin_permiso = exigir_centro(
            request.usuario,
            centro_id
        )

        if sin_permiso:
            return sin_permiso

        asistencias = AsistenciaRepository.listar_por_centro(
            centro_id
        )

        return jsonify({
            "status": "OK",
            "cantidad": len(asistencias),
            "asistencias": asistencias
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudieron obtener las asistencias del centro",
            "detalle": str(e)
        }), 500


# =========================================================
# POST /api/asistencias
# Registrar asistencia
# =========================================================

@asistencia_bp.route("", methods=["POST"])
@token_required
@roles_required("PROFESOR", "ADMIN")
def crear_asistencia():

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se recibieron datos"
        }), 400


    campos_obligatorios = [
        "alumno_id",
        "centro_id"
    ]


    campos_faltantes = [
        campo
        for campo in campos_obligatorios
        if data.get(campo) is None
    ]


    if campos_faltantes:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Faltan campos obligatorios",
            "campos": campos_faltantes
        }), 400


    try:

        asistencia_id = AsistenciaRepository.crear({

            "alumno_id": data["alumno_id"],
            "centro_id": data["centro_id"],
            "fecha": data.get("fecha"),
            "presente": data.get("presente", True),
            "observacion": data.get("observacion")

        })


        asistencia = AsistenciaRepository.obtener_por_id(
            asistencia_id
        )


        return jsonify({
            "status": "OK",
            "mensaje": "Asistencia registrada correctamente",
            "asistencia": asistencia
        }), 201


    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo registrar la asistencia",
            "detalle": str(e)
        }), 500


# =========================================================
# PUT /api/asistencias/<id>
# Actualizar asistencia
# =========================================================

@asistencia_bp.route(
    "/<int:asistencia_id>",
    methods=["PUT"]
)
@token_required
@roles_required("PROFESOR", "ADMIN")
def actualizar_asistencia(asistencia_id):

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se recibieron datos"
        }), 400


    campos_obligatorios = [
        "alumno_id",
        "centro_id",
        "fecha",
        "presente"
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

        actualizado = AsistenciaRepository.actualizar(
            asistencia_id,
            {
                "alumno_id": data["alumno_id"],
                "centro_id": data["centro_id"],
                "fecha": data["fecha"],
                "presente": data["presente"],
                "observacion": data.get("observacion")
            }
        )


        if not actualizado:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Asistencia no encontrada"
            }), 404


        asistencia = AsistenciaRepository.obtener_por_id(
            asistencia_id
        )


        return jsonify({
            "status": "OK",
            "mensaje": "Asistencia actualizada correctamente",
            "asistencia": asistencia
        }), 200


    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo actualizar la asistencia",
            "detalle": str(e)
        }), 500


# =========================================================
# DELETE /api/asistencias/<id>
# Eliminar asistencia
# =========================================================

@asistencia_bp.route(
    "/<int:asistencia_id>",
    methods=["DELETE"]
)
@token_required
@roles_required("PROFESOR", "ADMIN")
def eliminar_asistencia(asistencia_id):

    try:

        eliminado = AsistenciaRepository.eliminar(
            asistencia_id
        )


        if not eliminado:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Asistencia no encontrada"
            }), 404


        return jsonify({
            "status": "OK",
            "mensaje": "Asistencia eliminada correctamente"
        }), 200


    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo eliminar la asistencia",
            "detalle": str(e)
        }), 500