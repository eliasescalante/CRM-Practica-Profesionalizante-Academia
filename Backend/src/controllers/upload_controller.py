from flask import Blueprint, request, jsonify
import cloudinary
import cloudinary.uploader
from database.connection import get_db_connection

upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")

@upload_bp.route("/avatar", methods=["POST"])
def subir_avatar():
    try:
        # Verificar si vino un archivo en la petición
        if 'file' not in request.files:
            return jsonify({
                "status": "ERROR",
                "mensaje": "No se envió ningún archivo de imagen"
            }), 400

        file = request.files['file']
        persona_id = request.form.get("persona_id") # Opcional: si queremos impactar directo en BD

        if file.filename == '':
            return jsonify({
                "status": "ERROR",
                "mensaje": "El archivo está vacío"
            }), 400

        # Subir imagen a Cloudinary (se puede guardar en una carpeta específica)
        upload_result = cloudinary.uploader.upload(
            file,
            folder="crm_artes_marciales/avatars"
        )

        avatar_url = upload_result.get("secure_url")

        # Si mandaron la persona_id, actualizamos directamente en la tabla 'persona'
        if persona_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE persona SET avatar = %s WHERE id = %s",
                (avatar_url, persona_id)
            )
            conn.commit()
            cursor.close()
            conn.close()

        return jsonify({
            "status": "OK",
            "mensaje": "Avatar subido exitosamente a Cloudinary",
            "avatar_url": avatar_url
        }), 200

    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "mensaje": "Error al subir la imagen a Cloudinary",
            "detalle": str(e)
        }), 500