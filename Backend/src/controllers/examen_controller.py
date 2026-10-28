#agregado al docs
from flask import Blueprint, request, jsonify
from src.repositories.examen_repository import ExamenRepository
from src.utils.auth import token_required, roles_required
from src.utils.permisos import (
    denegado,
    es_admin,
    es_alumno,
    exigir_alumno_propio,
    exigir_centro
)


def puede_gestionar_examen(usuario, centro_id, profesor_id):
    """El ADMIN agenda en cualquier sede; el PROFESOR solo sus clases.

    Devuelve una respuesta 403 o None.
    """

    if es_admin(usuario):
        return None

    try:
        propio = int(usuario.get("profesor_id"))
        asignado = int(profesor_id)
    except (TypeError, ValueError):
        return denegado(
            "Solo podés agendar exámenes para tus propias clases"
        )

    if propio != asignado:
        return denegado(
            "Solo podés agendar exámenes para tus propias clases"
        )

    return exigir_centro(usuario, centro_id)


# =========================================================
# BLUEPRINT
# =========================================================

examen_bp = Blueprint(
    "examenes",
    __name__,
    url_prefix="/api/examenes"
)


# =========================================================
# LISTAR EXÁMENES
# =========================================================

@examen_bp.route("/", methods=["GET"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def listar_examenes():

    try:

        incluir_inactivos = (
            request.args.get("todos", "false").lower() == "true"
            and request.usuario.get("rol") in ("ADMIN", "PROFESOR")
        )

        examenes = ExamenRepository.listar(
            incluir_inactivos=incluir_inactivos
        )

        return jsonify({
            "status": "OK",
            "cantidad": len(examenes),
            "examenes": examenes
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Error al listar los exámenes",
            "detalle": str(e)
        }), 500


# =========================================================
# LISTAR PRÓXIMOS EXÁMENES
# =========================================================

@examen_bp.route("/proximos", methods=["GET"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def listar_proximos_examenes():

    try:

        examenes = ExamenRepository.listar_proximos()

        return jsonify({
            "status": "OK",
            "cantidad": len(examenes),
            "examenes": examenes
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Error al listar los próximos exámenes",
            "detalle": str(e)
        }), 500


# =========================================================
# OBTENER EXAMEN POR ID
# =========================================================

@examen_bp.route("/<int:examen_id>", methods=["GET"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def obtener_examen(examen_id):

    try:

        examen = ExamenRepository.obtener_por_id(
            examen_id
        )

        if not examen:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Examen no encontrado"
            }), 404

        return jsonify({
            "status": "OK",
            "examen": examen
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Error al obtener el examen",
            "detalle": str(e)
        }), 500


# =========================================================
# CREAR EXAMEN
# =========================================================

@examen_bp.route("/", methods=["POST"])
@token_required
@roles_required("PROFESOR", "ADMIN")
def crear_examen():

    try:

        datos = request.get_json()

        if not datos:

            return jsonify({
                "status": "ERROR",
                "mensaje": "No se recibieron datos"
            }), 400

        campos_requeridos = [
            "centro_id",
            "profesor_id",
            "titulo",
            "fecha_examen",
            "monto"
        ]

        for campo in campos_requeridos:

            if campo not in datos:

                return jsonify({
                    "status": "ERROR",
                    "mensaje": f"El campo '{campo}' es obligatorio"
                }), 400

        sin_permiso = puede_gestionar_examen(
            request.usuario,
            datos.get("centro_id"),
            datos.get("profesor_id")
        )

        if sin_permiso:
            return sin_permiso

        examen_id = ExamenRepository.crear(datos)

        examen = ExamenRepository.obtener_por_id(
            examen_id
        )

        return jsonify({
            "status": "OK",
            "mensaje": "Examen creado correctamente",
            "examen": examen
        }), 201

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Error al crear el examen",
            "detalle": str(e)
        }), 500


# =========================================================
# ACTUALIZAR EXAMEN
# =========================================================

@examen_bp.route("/<int:examen_id>", methods=["PUT"])
@token_required
@roles_required("PROFESOR", "ADMIN")
def actualizar_examen(examen_id):

    try:

        datos = request.get_json()

        if not datos:

            return jsonify({
                "status": "ERROR",
                "mensaje": "No se recibieron datos"
            }), 400

        campos_requeridos = [
            "centro_id",
            "profesor_id",
            "titulo",
            "fecha_examen",
            "monto"
        ]

        for campo in campos_requeridos:

            if campo not in datos:

                return jsonify({
                    "status": "ERROR",
                    "mensaje": f"El campo '{campo}' es obligatorio"
                }), 400

        examen_actual = ExamenRepository.obtener_por_id(examen_id)

        if not examen_actual:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Examen no encontrado"
            }), 404

        sin_permiso = puede_gestionar_examen(
            request.usuario,
            examen_actual.get("centro_id"),
            examen_actual.get("profesor_id")
        )

        if sin_permiso:
            return sin_permiso

        sin_permiso = puede_gestionar_examen(
            request.usuario,
            datos.get("centro_id"),
            datos.get("profesor_id")
        )

        if sin_permiso:
            return sin_permiso

        actualizado = ExamenRepository.actualizar(
            examen_id,
            datos
        )

        if not actualizado:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Examen no encontrado"
            }), 404

        examen = ExamenRepository.obtener_por_id(
            examen_id
        )

        return jsonify({
            "status": "OK",
            "mensaje": "Examen actualizado correctamente",
            "examen": examen
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Error al actualizar el examen",
            "detalle": str(e)
        }), 500


# =========================================================
# BAJA LÓGICA
# =========================================================

@examen_bp.route("/<int:examen_id>", methods=["DELETE"])
@token_required
@roles_required("PROFESOR", "ADMIN")
def eliminar_examen(examen_id):

    try:

        examen = ExamenRepository.obtener_por_id(examen_id)

        if not examen:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Examen no encontrado"
            }), 404

        sin_permiso = puede_gestionar_examen(
            request.usuario,
            examen.get("centro_id"),
            examen.get("profesor_id")
        )

        if sin_permiso:
            return sin_permiso

        eliminado = ExamenRepository.eliminar(
            examen_id
        )

        if not eliminado:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Examen no encontrado"
            }), 404

        return jsonify({
            "status": "OK",
            "mensaje": "Examen eliminado correctamente"
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Error al eliminar el examen",
            "detalle": str(e)
        }), 500


# =========================================================
# MIS INSCRIPCIONES
# =========================================================

@examen_bp.route("/mis-inscripciones", methods=["GET"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def listar_mis_inscripciones():

    try:

        usuario = request.usuario

        if es_alumno(usuario):

            alumno_id = usuario.get("alumno_id")

            if not alumno_id:

                return jsonify({
                    "status": "ERROR",
                    "mensaje": "Tu usuario no está asociado a un alumno"
                }), 403

        else:

            alumno_id = request.args.get("alumno_id", type=int)

            if not alumno_id:

                return jsonify({
                    "status": "ERROR",
                    "mensaje": "Indicá el alumno_id por query string"
                }), 400

        inscripciones = ExamenRepository.listar_inscripciones_alumno(
            alumno_id
        )

        return jsonify({
            "status": "OK",
            "cantidad": len(inscripciones),
            "inscripciones": inscripciones
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Error al listar las inscripciones",
            "detalle": str(e)
        }), 500


# =========================================================
# LISTAR INSCRIPTOS
# =========================================================

@examen_bp.route(
    "/<int:examen_id>/inscriptos",
    methods=["GET"]
)
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def listar_inscriptos(examen_id):

    try:

        examen = ExamenRepository.obtener_por_id(
            examen_id
        )

        if not examen:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Examen no encontrado"
            }), 404

        inscriptos = ExamenRepository.listar_inscriptos(
            examen_id
        )

        # Un ALUMNO solo puede ver su propia inscripción.
        if es_alumno(request.usuario):

            alumno_id = request.usuario.get("alumno_id")

            inscriptos = [
                inscripto
                for inscripto in inscriptos
                if alumno_id is not None
                and int(inscripto["alumno_id"]) == int(alumno_id)
            ]

        return jsonify({
            "status": "OK",
            "cantidad": len(inscriptos),
            "inscriptos": inscriptos
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Error al listar los inscriptos",
            "detalle": str(e)
        }), 500


# =========================================================
# OBTENER INSCRIPCIÓN
# =========================================================

@examen_bp.route(
    "/inscripciones/<int:inscripcion_id>",
    methods=["GET"]
)
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def obtener_inscripcion(inscripcion_id):

    try:

        inscripcion = ExamenRepository.obtener_inscripcion(
            inscripcion_id
        )

        if not inscripcion:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Inscripción no encontrada"
            }), 404

        sin_permiso = exigir_alumno_propio(
            request.usuario,
            inscripcion.get("alumno_id")
        )

        if sin_permiso:
            return sin_permiso

        return jsonify({
            "status": "OK",
            "inscripcion": inscripcion
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Error al obtener la inscripción",
            "detalle": str(e)
        }), 500


# =========================================================
# INSCRIBIR ALUMNO
# =========================================================

@examen_bp.route(
    "/<int:examen_id>/inscriptos",
    methods=["POST"]
)
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def inscribir_alumno(examen_id):

    try:

        datos = request.get_json()

        if not datos:

            return jsonify({
                "status": "ERROR",
                "mensaje": "No se recibieron datos"
            }), 400

        alumno_id = datos.get("alumno_id")

        usuario = request.usuario

        if es_alumno(usuario):

            if not usuario.get("alumno_id"):

                return jsonify({
                    "status": "ERROR",
                    "mensaje": "Tu usuario no está asociado a un alumno"
                }), 403

            # Un ALUMNO solo puede inscribirse a sí mismo.
            alumno_id = usuario["alumno_id"]

        if not alumno_id:

            return jsonify({
                "status": "ERROR",
                "mensaje": "El campo 'alumno_id' es obligatorio"
            }), 400

        examen = ExamenRepository.obtener_por_id(
            examen_id
        )

        if not examen:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Examen no encontrado"
            }), 404

        if not examen["activo"]:

            return jsonify({
                "status": "ERROR",
                "mensaje": "El examen no está activo"
            }), 400

        existente = ExamenRepository.existe_inscripcion(
            examen_id,
            alumno_id
        )

        if existente:

            return jsonify({
                "status": "ERROR",
                "mensaje": "El alumno ya está inscripto en este examen"
            }), 409

        inscripcion_id = ExamenRepository.inscribir_alumno(
            examen_id,
            alumno_id
        )

        inscripcion = ExamenRepository.obtener_inscripcion(
            inscripcion_id
        )

        return jsonify({
            "status": "OK",
            "mensaje": "Alumno inscripto correctamente",
            "inscripcion": inscripcion
        }), 201

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Error al inscribir al alumno",
            "detalle": str(e)
        }), 500


# =========================================================
# CANCELAR INSCRIPCIÓN
# =========================================================

@examen_bp.route(
    "/inscripciones/<int:inscripcion_id>",
    methods=["DELETE"]
)
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def cancelar_inscripcion(inscripcion_id):

    try:

        inscripcion = ExamenRepository.obtener_inscripcion(
            inscripcion_id
        )

        if not inscripcion:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Inscripción no encontrada"
            }), 404

        sin_permiso = exigir_alumno_propio(
            request.usuario,
            inscripcion.get("alumno_id")
        )

        if sin_permiso:
            return sin_permiso

        eliminado = ExamenRepository.cancelar_inscripcion(
            inscripcion_id
        )

        if not eliminado:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Inscripción no encontrada"
            }), 404

        return jsonify({
            "status": "OK",
            "mensaje": "Inscripción cancelada correctamente"
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Error al cancelar la inscripción",
            "detalle": str(e)
        }), 500

