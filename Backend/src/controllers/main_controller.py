from flask import Blueprint, jsonify
from database.connection import get_db_connection

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def bienvenida():
    try:
        conn = get_db_connection()
        if conn.is_connected():
            conn.close()
            return jsonify({
                "mensaje": "API CRM de Artes Marciales",
                "estado": "Online",
                "database": "Conectado exitosamente al server Xaamp (Apache) y MySQL",
            }), 200
    except Exception as e:
        return jsonify({
            "mensaje": "API CRM de Artes Marciales",
            "estado": "Inactivo",
            "database": "Desconectado",
            "error_detalle": str(e)
        }), 500