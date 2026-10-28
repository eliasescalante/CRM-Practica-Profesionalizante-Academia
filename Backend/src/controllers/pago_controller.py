#agregado a docs
from flask import Blueprint, request, jsonify

from src.repositories.pago_repository import PagoRepository
from src.repositories.cuota_repository import CuotaRepository
from src.repositories.examen_repository import ExamenRepository
from src.utils.auth import token_required, roles_required
from src.utils.permisos import (
    es_alumno,
    exigir_alumno_propio,
    datos_alumno
)


pago_bp = Blueprint(
    "pagos",
    __name__,
    url_prefix="/api/pagos"
)


# =========================================================
# GET /api/pagos
# Listar todos los pagos
# =========================================================

@pago_bp.route("", methods=["GET"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def listar_pagos():

    try:

        usuario = request.usuario

        if es_alumno(usuario):

            if not usuario.get("alumno_id"):

                return jsonify({
                    "status": "ERROR",
                    "mensaje": "Tu usuario no está asociado a un alumno"
                }), 403

            pagos = PagoRepository.listar_por_alumno(
                usuario["alumno_id"]
            )

        else:

            pagos = PagoRepository.listar()

        return jsonify({
            "status": "OK",
            "cantidad": len(pagos),
            "pagos": pagos
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudieron obtener los pagos",
            "detalle": str(e)
        }), 500


# =========================================================
# GET /api/pagos/<id>
# Obtener pago
# =========================================================

@pago_bp.route("/<int:pago_id>", methods=["GET"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def obtener_pago(pago_id):

    try:

        pago = PagoRepository.obtener_por_id(
            pago_id
        )

        if not pago:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Pago no encontrado"
            }), 404

        sin_permiso = exigir_alumno_propio(
            request.usuario,
            pago.get("alumno_id")
        )

        if sin_permiso:
            return sin_permiso

        return jsonify({
            "status": "OK",
            "pago": pago
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo obtener el pago",
            "detalle": str(e)
        }), 500


# =========================================================
# GET /api/pagos/alumno/<id>
# Listar pagos de un alumno
# =========================================================

@pago_bp.route(
    "/alumno/<int:alumno_id>",
    methods=["GET"]
)
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def listar_pagos_alumno(alumno_id):

    try:

        sin_permiso = exigir_alumno_propio(
            request.usuario,
            alumno_id
        )

        if sin_permiso:
            return sin_permiso

        pagos = PagoRepository.listar_por_alumno(
            alumno_id
        )

        return jsonify({
            "status": "OK",
            "cantidad": len(pagos),
            "pagos": pagos
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudieron obtener los pagos del alumno",
            "detalle": str(e)
        }), 500


# =========================================================
# GET /api/pagos/pendientes
# Listar pagos pendientes de confirmación
# =========================================================

@pago_bp.route(
    "/pendientes",
    methods=["GET"]
)
@token_required
@roles_required("PROFESOR", "ADMIN")
def listar_pagos_pendientes():

    try:

        pagos = PagoRepository.listar_pendientes()

        return jsonify({
            "status": "OK",
            "cantidad": len(pagos),
            "pagos": pagos
        }), 200

    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudieron obtener los pagos pendientes",
            "detalle": str(e)
        }), 500


# =========================================================
# POST /api/pagos
# Registrar pago
# =========================================================

@pago_bp.route("", methods=["POST"])
@token_required
@roles_required('ADMIN', 'PROFESOR', 'ALUMNO')
def crear_pago():

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se recibieron datos"
        }), 400


    # -----------------------------------------------------
    # Campos obligatorios
    # -----------------------------------------------------

    campos_obligatorios = [
        "alumno_id",
        "centro_id",
        "tipo_concepto",
        "monto",
        "metodo_pago"
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


    # -----------------------------------------------------
    # Validar tipo de concepto
    # -----------------------------------------------------

    tipos_validos = [
        "CUOTA",
        "EXAMEN",
        "MATRICULA",
        "INSUMO",
        "OTRO"
    ]

    if data["tipo_concepto"] not in tipos_validos:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Tipo de concepto inválido",
            "valores_validos": tipos_validos
        }), 400


    # -----------------------------------------------------
    # Validar método de pago
    # -----------------------------------------------------

    metodos_validos = [
        "EFECTIVO",
        "TRANSFERENCIA"
    ]

    if data["metodo_pago"] not in metodos_validos:

        return jsonify({
            "status": "ERROR",
            "mensaje": "Método de pago inválido",
            "valores_validos": metodos_validos
        }), 400


    # -----------------------------------------------------
    # Validar monto
    # -----------------------------------------------------

    try:

        monto = float(data["monto"])

        if monto <= 0:

            return jsonify({
                "status": "ERROR",
                "mensaje": "El monto debe ser mayor a cero"
            }), 400

    except (TypeError, ValueError):

        return jsonify({
            "status": "ERROR",
            "mensaje": "El monto debe ser numérico"
        }), 400


    # -----------------------------------------------------
    # Un ALUMNO solo puede declarar pagos propios
    # -----------------------------------------------------

    usuario = request.usuario

    if es_alumno(usuario):

        if not usuario.get("alumno_id"):

            return jsonify({
                "status": "ERROR",
                "mensaje": "Tu usuario no está asociado a un alumno"
            }), 403

        alumno = datos_alumno(usuario["alumno_id"])

        if not alumno or not alumno.get("centro_id"):

            return jsonify({
                "status": "ERROR",
                "mensaje": "Tu alumno no tiene una sede asignada"
            }), 400

        data["alumno_id"] = alumno["alumno_id"]
        data["centro_id"] = alumno["centro_id"]
        data["profesor_id"] = alumno.get("profesor_id")


    # -----------------------------------------------------
    # Validar relaciones según concepto
    # -----------------------------------------------------

    if (
        data["tipo_concepto"] == "CUOTA"
        and not data.get("cuota_id")
    ):

        return jsonify({
            "status": "ERROR",
            "mensaje": "Un pago de tipo CUOTA requiere cuota_id"
        }), 400


    if (
        data["tipo_concepto"] == "EXAMEN"
        and not data.get("inscripcion_examen_id")
    ):

        return jsonify({
            "status": "ERROR",
            "mensaje": (
                "Un pago de tipo EXAMEN requiere "
                "inscripcion_examen_id"
            )
        }), 400


    # -----------------------------------------------------
    # La cuota o inscripción deben ser del mismo alumno
    # -----------------------------------------------------

    if data.get("cuota_id"):

        cuota = CuotaRepository.obtener_por_id(
            data["cuota_id"]
        )

        if not cuota:

            return jsonify({
                "status": "ERROR",
                "mensaje": "La cuota indicada no existe"
            }), 400

        if int(cuota["alumno_id"]) != int(data["alumno_id"]):

            return jsonify({
                "status": "ERROR",
                "mensaje": "La cuota no pertenece al alumno indicado"
            }), 400


    if data.get("inscripcion_examen_id"):

        inscripcion = ExamenRepository.obtener_inscripcion(
            data["inscripcion_examen_id"]
        )

        if not inscripcion:

            return jsonify({
                "status": "ERROR",
                "mensaje": "La inscripción indicada no existe"
            }), 400

        if int(inscripcion["alumno_id"]) != int(data["alumno_id"]):

            return jsonify({
                "status": "ERROR",
                "mensaje": (
                    "La inscripción no pertenece al alumno indicado"
                )
            }), 400


    try:

        datos = {
            "alumno_id": data["alumno_id"],
            "cuota_id": data.get("cuota_id"),
            "inscripcion_examen_id": data.get(
                "inscripcion_examen_id"
            ),

            "profesor_id": data.get("profesor_id"),
            "centro_id": data["centro_id"],

            "tipo_concepto": data["tipo_concepto"],
            "descripcion": data.get("descripcion"),

            "monto": monto,

            "metodo_pago": data["metodo_pago"],
            "comprobante_url": data.get("comprobante_url")
        }


        pago_id = PagoRepository.crear(datos)


        pago = PagoRepository.obtener_por_id(
            pago_id
        )


        return jsonify({
            "status": "OK",
            "mensaje": "Pago registrado correctamente",
            "pago": pago
        }), 201


    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo registrar el pago",
            "detalle": str(e)
        }), 500


# =========================================================
# PUT /api/pagos/<id>/confirmar
# Confirmar pago
# =========================================================

@pago_bp.route(
    "/<int:pago_id>/confirmar",
    methods=["PUT"]
)
@token_required
@roles_required("ADMIN")
def confirmar_pago(pago_id):

    data = request.get_json(silent=True) or {}

    profesor_id = data.get("profesor_id")


    try:

        pago = PagoRepository.obtener_por_id(
            pago_id
        )

        if not pago:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Pago no encontrado"
            }), 404


        if pago["estado"] != "PENDIENTE":

            return jsonify({
                "status": "ERROR",
                "mensaje": (
                    "El pago no puede confirmarse porque "
                    f"su estado actual es '{pago['estado']}'"
                )
            }), 409


        confirmado = PagoRepository.confirmar(
            pago_id,
            profesor_id
        )


        if not confirmado:

            return jsonify({
                "status": "ERROR",
                "mensaje": "No se pudo confirmar el pago"
            }), 400


        pago_actualizado = PagoRepository.obtener_por_id(
            pago_id
        )


        return jsonify({
            "status": "OK",
            "mensaje": "Pago confirmado correctamente",
            "pago": pago_actualizado
        }), 200


    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo confirmar el pago",
            "detalle": str(e)
        }), 500


# =========================================================
# PUT /api/pagos/<id>/rechazar
# Rechazar pago
# =========================================================

@pago_bp.route(
    "/<int:pago_id>/rechazar",
    methods=["PUT"]
)
@token_required
@roles_required("ADMIN")
def rechazar_pago(pago_id):

    data = request.get_json(silent=True) or {}

    profesor_id = data.get("profesor_id")


    try:

        pago = PagoRepository.obtener_por_id(
            pago_id
        )

        if not pago:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Pago no encontrado"
            }), 404


        if pago["estado"] != "PENDIENTE":

            return jsonify({
                "status": "ERROR",
                "mensaje": (
                    "El pago no puede rechazarse porque "
                    f"su estado actual es '{pago['estado']}'"
                )
            }), 409


        rechazado = PagoRepository.rechazar(
            pago_id,
            profesor_id
        )


        if not rechazado:

            return jsonify({
                "status": "ERROR",
                "mensaje": "No se pudo rechazar el pago"
            }), 400


        pago_actualizado = PagoRepository.obtener_por_id(
            pago_id
        )


        return jsonify({
            "status": "OK",
            "mensaje": "Pago rechazado correctamente",
            "pago": pago_actualizado
        }), 200


    except Exception as e:

        return jsonify({
            "status": "ERROR",
            "mensaje": "No se pudo rechazar el pago",
            "detalle": str(e)
        }), 500