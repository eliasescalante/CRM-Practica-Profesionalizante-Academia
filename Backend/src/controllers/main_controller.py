from flask import Blueprint, jsonify

from database.connection import get_db_connection
from database.cloudinary_connection import check_cloudinary_connection


main_bp = Blueprint("main", __name__)


@main_bp.route("/api/status", methods=["GET"])
def status():

    # ---------------------------------------------
    # MYSQL
    # ---------------------------------------------

    db_estado = "ERROR"

    try:

        conn = get_db_connection()

        if conn and conn.is_connected():
            db_estado = "OK"
            conn.close()

    except Exception as e:

        db_estado = f"ERROR: {str(e)}"


    # ---------------------------------------------
    # CLOUDINARY
    # ---------------------------------------------

    cloudinary_resultado = check_cloudinary_connection()

    cloudinary_estado = cloudinary_resultado.get("status")


    # ---------------------------------------------
    # SERVER
    # ---------------------------------------------

    server_estado = "OK"


    # ---------------------------------------------
    # ESTADO GENERAL
    # ---------------------------------------------

    todo_ok = (
        db_estado == "OK"
        and cloudinary_estado == "OK"
        and server_estado == "OK"
    )


    return jsonify({

        "server": server_estado,

        "database": db_estado,

        "cloudinary": cloudinary_estado,

        "status": "OK" if todo_ok else "ERROR"

    }), 200 if todo_ok else 500