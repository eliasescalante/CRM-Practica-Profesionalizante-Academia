import os
import cloudinary
import cloudinary.api

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

def check_cloudinary_connection():
    try:
        respuesta = cloudinary.api.ping()
        return {
            "status": "OK",
            "mensaje": "Conectado a Cloudinary exitosa"
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "mensaje": f"Error de conexión con Cloudinary: {str(e)}"
        }