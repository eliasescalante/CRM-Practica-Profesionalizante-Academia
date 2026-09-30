from flask import Blueprint, request, jsonify

from src.repositories.graduacion_repository import GraduacionRepository


graduacion_bp = Blueprint(
    "graduaciones",
    __name__,
    url_prefix="/api/graduaciones"
)


# =========================================================
# LISTAR GRADUACIONES
# =========================================================

@graduacion_bp.route("", methods=["GET"])
def listar_graduaciones():

    graduaciones = GraduacionRepository.listar()

    return jsonify(graduaciones), 200


# =========================================================
# OBTENER GRADUACIÓN
# =========================================================

@graduacion_bp.route("/<int:graduacion_id>", methods=["GET"])
def obtener_graduacion(graduacion_id):

    graduacion = GraduacionRepository.obtener_por_id(
        graduacion_id
    )

    if not graduacion:

        return jsonify({
            "error": "Graduación no encontrada"
        }), 404

    return jsonify(graduacion), 200


# =========================================================
# LISTAR GRADUACIONES DE UN ALUMNO
# =========================================================

@graduacion_bp.route(
    "/alumno/<int:alumno_id>",
    methods=["GET"]
)
def listar_graduaciones_alumno(alumno_id):

    graduaciones = GraduacionRepository.listar_por_alumno(
        alumno_id
    )

    return jsonify(graduaciones), 200


# =========================================================
# CREAR GRADUACIÓN
# =========================================================

@graduacion_bp.route("", methods=["POST"])
def crear_graduacion():

    datos = request.get_json()

    if not datos:

        return jsonify({
            "error": "Debe enviar datos"
        }), 400


    campos_obligatorios = [
        "alumno_id",
        "centro_id",
        "grado",
        "fecha"
    ]

    for campo in campos_obligatorios:

        if campo not in datos:

            return jsonify({
                "error": f"El campo '{campo}' es obligatorio"
            }), 400


    try:

        graduacion_id = GraduacionRepository.crear(
            datos
        )

        graduacion = GraduacionRepository.obtener_por_id(
            graduacion_id
        )

        return jsonify(graduacion), 201

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 400