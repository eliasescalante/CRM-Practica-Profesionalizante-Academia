import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():

    opciones = {}

    # MySQL en la nube (Railway, Aiven, Clever Cloud, etc.) suele exigir
    # TLS. Con DB_SSL=1 se activa sin verificar el certificado; si el
    # proveedor da un CA, se puede apuntar con DB_SSL_CA.
    if os.getenv('DB_SSL', '0') == '1':
        opciones['ssl_disabled'] = False
        opciones['ssl_verify_cert'] = os.getenv('DB_SSL_VERIFY', '0') == '1'

        ssl_ca = os.getenv('DB_SSL_CA')

        if ssl_ca:
            opciones['ssl_ca'] = ssl_ca

    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', os.getenv('DB_PASS', '')),
        database=os.getenv('DB_NAME', 'crm_artes_marciales'),
        **opciones
    )