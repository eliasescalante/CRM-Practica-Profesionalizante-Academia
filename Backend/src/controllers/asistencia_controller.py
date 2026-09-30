from flask import Blueprint, request, jsonify

from src.repositories.asistencia_repository import AsistenciaRepository


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
def listar_asistencias():

    try:

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
def listar_asistencias_alumno(alumno_id):

    try:

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
def listar_asistencias_centro(centro_id):

    try:

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