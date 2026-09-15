from flask import Blueprint, jsonify
from database.connection import get_db_connection
from database.cloudinary_connection import check_cloudinary_connection

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def bienvenida():
    db_estado = "Desconectado"
    cld_estado = "Desconectado"
    cld_detalle = None
    
    # 1. Validación de MySQL
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            conn.close()
            db_estado = "Conectado exitosamente al server XAMPP (Apache) y MySQL"
    except Exception as e:
        db_estado = f"Error DB: {str(e)}"

    # 2. Validación de Cloudinary
    cld_res = check_cloudinary_connection()
    cld_estado = cld_res.get("mensaje")

    # Evaluar estado general
    is_ok = ("Conectado exitosamente" in db_estado) and (cld_res.get("status") == "OK")

    return jsonify({
        "mensaje": "API CRM de Artes Marciales",
        "estado": "Online" if is_ok else "Parcial / Inactivo",
        "database": db_estado,
        "cloudinary": cld_estado
    }), (200 if is_ok else 500)