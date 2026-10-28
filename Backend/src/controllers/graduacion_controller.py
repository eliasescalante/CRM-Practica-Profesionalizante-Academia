#agregado al docs
from flask import Blueprint, request, jsonify

from src.repositories.graduacion_repository import GraduacionRepository
from src.utils.auth import token_required, roles_required
from src.utils.permisos import es_alumno, exigir_alumno_propio


graduacion_bp = Blueprint(
    "graduaciones",
    __name__,
    url_prefix="/api/graduaciones"
)


# =========================================================
# LISTAR GRADUACIONES
# =========================================================

@graduacion_bp.route("", methods=["GET"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def listar_graduaciones():

    usuario = request.usuario

    if es_alumno(usuario):

        if not usuario.get("alumno_id"):

            return jsonify({
                "status": "ERROR",
                "mensaje": "Tu usuario no está asociado a un alumno"
            }), 403

        graduaciones = GraduacionRepository.listar_por_alumno(
            usuario["alumno_id"]
        )

    else:

        graduaciones = GraduacionRepository.listar()

    return jsonify(graduaciones), 200


# =========================================================
# OBTENER GRADUACIÓN
# =========================================================

@graduacion_bp.route("/<int:graduacion_id>", methods=["GET"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def obtener_graduacion(graduacion_id):

    graduacion = GraduacionRepository.obtener_por_id(
        graduacion_id
    )

    if not graduacion:

        return jsonify({
            "error": "Graduación no encontrada"
        }), 404

    sin_permiso = exigir_alumno_propio(
        request.usuario,
        graduacion.get("alumno_id")
    )

    if sin_permiso:
        return sin_permiso

    return jsonify(graduacion), 200


# =========================================================
# LISTAR GRADUACIONES DE UN ALUMNO
# =========================================================

@graduacion_bp.route(
    "/alumno/<int:alumno_id>",
    methods=["GET"]
)
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def listar_graduaciones_alumno(alumno_id):

    sin_permiso = exigir_alumno_propio(
        request.usuario,
        alumno_id
    )

    if sin_permiso:
        return sin_permiso

    graduaciones = GraduacionRepository.listar_por_alumno(
        alumno_id
    )

    return jsonify(graduaciones), 200


# =========================================================
# CREAR GRADUACIÓN
# =========================================================

@graduacion_bp.route("", methods=["POST"])
@token_required
@roles_required("PROFESOR", "ADMIN")
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