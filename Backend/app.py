import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from src.controllers.main_controller import main_bp
from src.controllers.auth_controller import auth_bp

DASHBOARD_FOLDER = os.path.join(os.path.dirname(__file__), 'dashboard')

app = Flask(__name__, static_folder=DASHBOARD_FOLDER)
CORS(app)

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static_files(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    # Si la ruta no existe en 'dashboard', dejamos que pase a otros manejadores
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=4000)