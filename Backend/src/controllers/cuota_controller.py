#agregado al docs
from flask import Blueprint, request, jsonify

from src.repositories.cuota_repository import CuotaRepository


cuota_bp = Blueprint(
    "cuotas",
    __name__,
    url_prefix="/api/cuotas"
)

# =========================================================
# GET /api/cuotas
# Listar cuotas
# =========================================================

@cuota_bp.route("", methods=["GET"])
def listar_cuotas():

    try:

        cuotas = CuotaRepository.listar()

        return jsonify({
            "status": "OK",
            "cantidad": len(cuotas),
            "cuotas": cuotas
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudieron obtener las cuotas",
            "detalle": str(e)
        }), 500


# =========================================================
# GET /api/cuotas/<id>
# Obtener cuota
# =========================================================

@cuota_bp.route("/<int:cuota_id>", methods=["GET"])
def obtener_cuota(cuota_id):

    try:

        cuota = CuotaRepository.obtener_por_id(cuota_id)

        if not cuota:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Cuota no encontrada"
            }), 404

        return jsonify({
            "status": "OK",
            "cuota": cuota
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo obtener la cuota",
            "detalle": str(e)
        }), 500


# =========================================================
# GET /api/cuotas/alumno/<alumno_id>
# Cuotas de un alumno
# =========================================================

@cuota_bp.route("/alumno/<int:alumno_id>", methods=["GET"])
def listar_cuotas_alumno(alumno_id):

    try:

        cuotas = CuotaRepository.listar_por_alumno(alumno_id)

        return jsonify({
            "status": "OK",
            "cantidad": len(cuotas),
            "cuotas": cuotas
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudieron obtener las cuotas del alumno",
            "detalle": str(e)
        }), 500


# =========================================================
# POST /api/cuotas
# Crear cuota
# =========================================================

@cuota_bp.route("", methods=["POST"])
def crear_cuota():

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se recibieron datos"
        }), 400

    campos_obligatorios = [
        "alumno_id",
        "centro_id",
        "periodo_mes",
        "periodo_anio",
        "monto",
        "fecha_vencimiento"
    ]

    campos_faltantes = [
        campo
        for campo in campos_obligatorios
        if campo not in data or data[campo] in (None, "")
    ]

    if campos_faltantes:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Faltan campos obligatorios",
            "campos": campos_faltantes
        }), 400

    try:

        cuota_id = CuotaRepository.crear(data)

        return jsonify({
            "status": "OK",
            "mensaje": "Cuota creada correctamente",
            "cuota_id": cuota_id
        }), 201

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo crear la cuota",
            "detalle": str(e)
        }), 500


# =========================================================
# PUT /api/cuotas/<id>
# Actualizar cuota
# =========================================================

@cuota_bp.route("/<int:cuota_id>", methods=["PUT"])
def actualizar_cuota(cuota_id):

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se recibieron datos"
        }), 400

    campos_obligatorios = [
        "alumno_id",
        "centro_id",
        "periodo_mes",
        "periodo_anio",
        "monto",
        "fecha_vencimiento",
        "estado"
    ]

    campos_faltantes = [
        campo
        for campo in campos_obligatorios
        if campo not in data or data[campo] in (None, "")
    ]

    if campos_faltantes:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Faltan campos obligatorios",
            "campos": campos_faltantes
        }), 400

    try:

        actualizado = CuotaRepository.actualizar(
            cuota_id,
            data
        )

        if not actualizado:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Cuota no encontrada"
            }), 404

        return jsonify({
            "status": "OK",
            "mensaje": "Cuota actualizada correctamente"
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo actualizar la cuota",
            "detalle": str(e)
        }), 500


# =========================================================
# DELETE /api/cuotas/<id>
# Eliminar cuota
# =========================================================

@cuota_bp.route("/<int:cuota_id>", methods=["DELETE"])
def eliminar_cuota(cuota_id):

    try:

        eliminado = CuotaRepository.eliminar(cuota_id)

        if not eliminado:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Cuota no encontrada"
            }), 404

        return jsonify({
            "status": "OK",
            "mensaje": "Cuota eliminada correctamente"
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo eliminar la cuota",
            "detalle": str(e)
        }), 500