import os
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import request, jsonify


# =========================================================
# CONFIGURACIÓN JWT
# =========================================================

JWT_SECRET = os.getenv("JWT_SECRET")

JWT_ALGORITHM = "HS256"

JWT_EXPIRATION_HOURS = 8


# =========================================================
# GENERAR TOKEN
# =========================================================

def generar_token(usuario):

    if not JWT_SECRET:
        raise Exception("JWT_SECRET no está configurado")

    ahora = datetime.now(timezone.utc)

    payload = {
        "usuario_id": usuario["usuario_id"],
        "persona_id": usuario["persona_id"],
        "rol": usuario["rol"],
        "iat": ahora,
        "exp": ahora + timedelta(hours=JWT_EXPIRATION_HOURS)
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM
    )

    return token


# =========================================================
# OBTENER TOKEN DEL HEADER
# =========================================================

def obtener_token():

    authorization = request.headers.get("Authorization")

    if not authorization:
        return None

    partes = authorization.split(" ")

    if len(partes) != 2:
        return None

    esquema = partes[0]
    token = partes[1]

    if esquema.lower() != "bearer":
        return None

    return token


# =========================================================
# DECODIFICAR TOKEN
# =========================================================

def verificar_token(token):

    if not JWT_SECRET:
        raise Exception("JWT_SECRET no está configurado")

    try:

        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        return payload

    except jwt.ExpiredSignatureError:

        return None

    except jwt.InvalidTokenError:

        return None


# =========================================================
# DECORADOR: TOKEN OBLIGATORIO
# =========================================================

def token_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        token = obtener_token()

        if not token:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Token de autenticación requerido"
            }), 401

        usuario = verificar_token(token)

        if not usuario:

            return jsonify({
                "status": "ERROR",
                "mensaje": "Token inválido o expirado"
            }), 401

        # Guardamos el usuario autenticado
        # para que el endpoint pueda utilizarlo.

        request.usuario = usuario

        return func(*args, **kwargs)

    return wrapper


# =========================================================
# DECORADOR: ROLES PERMITIDOS
# =========================================================

def roles_required(*roles):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            usuario = getattr(request, "usuario", None)

            if not usuario:

                return jsonify({
                    "status": "ERROR",
                    "mensaje": "Usuario no autenticado"
                }), 401

            rol_usuario = usuario.get("rol")

            if rol_usuario not in roles:

                return jsonify({
                    "status": "ERROR",
                    "mensaje": "No tenés permisos para realizar esta acción"
                }), 403

            return func(*args, **kwargs)

        return wrapper

    return decorator