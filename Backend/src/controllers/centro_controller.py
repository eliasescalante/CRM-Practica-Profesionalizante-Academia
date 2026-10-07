#agregado al docs
from flask import Blueprint, request, jsonify

from src.repositories.centro_repository import CentroRepository


centro_bp = Blueprint(
    "centros",
    __name__,
    url_prefix="/api/centros"
)


# =========================================================
# GET /api/centros
# Listar centros
# =========================================================

@centro_bp.route("", methods=["GET"])
def listar_centros():

    try:

        incluir_inactivos = (
            request.args.get("todos", "false").lower() == "true"
        )

        centros = CentroRepository.listar(
            incluir_inactivos=incluir_inactivos
        )

        return jsonify({
            "status": "OK",
            "cantidad": len(centros),
            "centros": centros
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudieron obtener los centros",
            "detalle": str(e)
        }), 500


# =========================================================
# GET /api/centros/<id>
# Obtener centro
# =========================================================

@centro_bp.route("/<int:centro_id>", methods=["GET"])
def obtener_centro(centro_id):

    try:

        centro = CentroRepository.obtener_por_id(centro_id)

        if not centro:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Centro no encontrado"
            }), 404

        return jsonify({
            "status": "OK",
            "centro": centro
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo obtener el centro",
            "detalle": str(e)
        }), 500


# =========================================================
# POST /api/centros
# Crear centro
# =========================================================

@centro_bp.route("", methods=["POST"])
def crear_centro():

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se recibieron datos"
        }), 400


    # -----------------------------------------------------
    # Validar campos obligatorios
    # -----------------------------------------------------

    if not data.get("nombre"):

        return jsonify({
            "status": "ERROR",
            "mensaje": "El nombre del centro es obligatorio"
        }), 400


    try:

        # -------------------------------------------------
        # Verificar nombre duplicado
        # -------------------------------------------------

        centro_existente = CentroRepository.obtener_por_nombre(
            data["nombre"]
        )

        if centro_existente:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Ya existe un centro con ese nombre"
            }), 409


        # -------------------------------------------------
        # Crear centro
        # -------------------------------------------------

        centro_id = CentroRepository.crear(data)

        centro = CentroRepository.obtener_por_id(
            centro_id
        )

        return jsonify({
            "status": "OK",
            "mensaje": "Centro creado correctamente",
            "centro": centro
        }), 201


    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo crear el centro",
            "detalle": str(e)
        }), 500


# =========================================================
# PUT /api/centros/<id>
# Actualizar centro
# =========================================================

@centro_bp.route("/<int:centro_id>", methods=["PUT"])
def actualizar_centro(centro_id):

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se recibieron datos"
        }), 400


    try:

        # -------------------------------------------------
        # Verificar existencia
        # -------------------------------------------------

        centro = CentroRepository.obtener_por_id(
            centro_id
        )

        if not centro:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Centro no encontrado"
            }), 404


        # -------------------------------------------------
        # Validar nombre
        # -------------------------------------------------

        if not data.get("nombre"):

            return jsonify({
                "status": "ERROR",
                "mensaje": "El nombre del centro es obligatorio"
            }), 400


        # -------------------------------------------------
        # Verificar nombre duplicado
        # -------------------------------------------------

        centro_nombre = CentroRepository.obtener_por_nombre(
            data["nombre"]
        )

        if (
            centro_nombre
            and centro_nombre["centro_id"] != centro_id
        ):

            return jsonify({
                "status": "ERROR",
                "mensaje": "Ya existe otro centro con ese nombre"
            }), 409


        # -------------------------------------------------
        # Actualizar
        # -------------------------------------------------

        actualizado = CentroRepository.actualizar(
            centro_id,
            data
        )

        if not actualizado:

            return jsonify({
                "status": "ERROR",
                "mensaje": "No se pudo actualizar el centro"
            }), 400


        centro_actualizado = CentroRepository.obtener_por_id(
            centro_id
        )

        return jsonify({
            "status": "OK",
            "mensaje": "Centro actualizado correctamente",
            "centro": centro_actualizado
        }), 200


    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo actualizar el centro",
            "detalle": str(e)
        }), 500


# =========================================================
# DELETE /api/centros/<id>
# Baja lógica
# =========================================================

@centro_bp.route("/<int:centro_id>", methods=["DELETE"])
def eliminar_centro(centro_id):

    try:

        centro = CentroRepository.obtener_por_id(
            centro_id
        )

        if not centro:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Centro no encontrado"
            }), 404


        eliminado = CentroRepository.eliminar(
            centro_id
        )

        if not eliminado:

            return jsonify({
                "status": "ERROR",
                "mensaje": "No se pudo dar de baja el centro"
            }), 400


        return jsonify({
            "status": "OK",
            "mensaje": "Centro dado de baja correctamente"
        }), 200


    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo eliminar el centro",
            "detalle": str(e)
        }), 500