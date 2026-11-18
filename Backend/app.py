import os

# Cargamos las variables de .env ANTES de importar los módulos
# que leen configuración al momento de importarse (ej: JWT_SECRET en utils/auth.py).
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from src.controllers.main_controller import main_bp
from src.controllers.auth_controller import auth_bp
from src.controllers.alumno_controller import alumno_bp
from src.controllers.profesor_controller import profesor_bp
from src.controllers.upload_controller import upload_bp
from src.controllers.centro_controller import centro_bp
from src.controllers.graduacion_controller import graduacion_bp
from src.controllers.pago_controller import pago_bp
from src.controllers.examen_controller import examen_bp
from src.controllers.asistencia_controller import asistencia_bp
from src.controllers.noticia_controller import noticia_bp
from src.controllers.cuota_controller import cuota_bp
from src.controllers.chat_controller import chat_bp
from src.controllers.perfil_controller import perfil_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_FOLDER = os.path.join(BASE_DIR, 'dashboard')
FRONTEND_FOLDER = os.path.abspath(os.path.join(BASE_DIR, '..', 'FrontEnd'))

app = Flask(__name__, static_folder=DASHBOARD_FOLDER)

# CORS: por defecto queda abierto para desarrollo. En producción, si el
# frontend está en otro dominio, limitar con CORS_ORIGINS (separados por coma).
# CORS_ORIGINS=https://mi-frontend.netlify.app,https://otro-dominio.com
_cors_origenes = [
    origen.strip()
    for origen in (os.getenv('CORS_ORIGINS') or '').split(',')
    if origen.strip()
]

if _cors_origenes:
    CORS(app, resources={r'/api/*': {'origins': _cors_origenes}})
else:
    CORS(app)

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(alumno_bp)
app.register_blueprint(profesor_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(centro_bp)
app.register_blueprint(graduacion_bp)
app.register_blueprint(pago_bp)
app.register_blueprint(examen_bp)
app.register_blueprint(asistencia_bp)
app.register_blueprint(noticia_bp)
app.register_blueprint(cuota_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(perfil_bp)

def _archivo_frontend(ruta):
    return os.path.isfile(os.path.join(FRONTEND_FOLDER, ruta))


def _servir_frontend(ruta):
    return send_from_directory(FRONTEND_FOLDER, ruta)


@app.route('/')
def index():
    """Sirve la landing real si FrontEnd/ está junto al backend."""
    if _archivo_frontend('index.html'):
        return _servir_frontend('index.html')

    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static_files(path):
    """API primero (las rutas de los blueprints ganan), después el frontend.

    Con un solo host, Flask sirve también la landing, el login y el panel.
    Si el frontend está en otro dominio, esta ruta queda de respaldo.
    """

    if path.startswith('api/'):
        return jsonify({
            'status': 'ERROR',
            'mensaje': 'Endpoint no encontrado'
        }), 404

    if _archivo_frontend(path):
        return _servir_frontend(path)

    # El mockup viejo de dashboard/ sigue accesible si existe.
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)

    if _archivo_frontend('index.html'):
        if '.' in os.path.basename(path):
            return jsonify({
                'status': 'ERROR',
                'mensaje': 'Archivo no encontrado'
            }), 404

        return _servir_frontend('index.html')

    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(
        host=os.getenv('HOST', '127.0.0.1'),
        port=int(os.getenv('PORT', 4000)),
        debug=(os.getenv('FLASK_DEBUG', '1') == '1')
    )