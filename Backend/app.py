import os
from pathlib import Path
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

# BASE_DIR es la raíz del proyecto (donde está el .env y el index.html principal)
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

# Apuntar la carpeta de templates a la raíz del proyecto
app = Flask(__name__, template_folder=str(BASE_DIR))
CORS(app)

# Configuración de base de datos
app.config['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
app.config['DB_USER'] = os.getenv('DB_USER', 'root')
app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD', '')
app.config['DB_NAME'] = os.getenv('DB_NAME', 'crm_artes_marciales')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "API CRM Backend activa",
        "database": app.config['DB_NAME']
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)