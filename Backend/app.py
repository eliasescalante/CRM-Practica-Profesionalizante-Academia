from flask import Flask
from flask_cors import CORS
from src.controllers.main_controller import main_bp
from src.controllers.auth_controller import auth_bp

app = Flask(__name__)
CORS(app)

# Registro del controlador principal
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)