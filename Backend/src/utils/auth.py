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

        # Verificar contra la BD que la cuenta siga activa y usar su rol
        # actual. Así, al deshabilitar a un usuario, su token deja de servir
        # y los cambios de rol se aplican sin esperar a que expire el JWT.
        try:

            from src.repositories.usuario_repository import (
                UsuarioRepository
            )

            usuario_db = UsuarioRepository.obtener_por_id(
                usuario["usuario_id"]
            )

        except Exception:

            return jsonify({
                "status": "ERROR",
                "mensaje": "No se pudo verificar la sesión"
            }), 503

        if not usuario_db:

            return jsonify({
                "status": "ERROR",
                "mensaje": "El usuario ya no existe"
            }), 401

        if (
            not usuario_db["usuario_activo"]
            or not usuario_db["persona_activa"]
        ):

            return jsonify({
                "status": "ERROR",
                "mensaje": "La cuenta se encuentra inactiva"
            }), 403

        usuario["rol"] = usuario_db["rol"]
        usuario["persona_id"] = usuario_db["persona_id"]
        usuario["alumno_id"] = usuario_db.get("alumno_id")
        usuario["profesor_id"] = usuario_db.get("profesor_id")

        # Guardamos el usuario autenticado
        # para que el endpoint pueda utilizarlo.

        request.usuario = usuario

        return func(*args, **kwargs)

    return wrapper


# =========================================================
# DECORADOR: TOKEN OPCIONAL
# =========================================================
#
# Para vistas de solo lectura que necesitan funcionar también sin
# sesión (por ejemplo, poblar los selects del alta de alumno).
# Si hay token válido deja request.usuario como el usuario autenticado;
# si no hay token, es inválido o la cuenta está inactiva, deja None
# y la vista decide qué mostrar. Nunca corta la petición.

def token_opcional(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        request.usuario = None

        token = obtener_token()

        if not token:
            return func(*args, **kwargs)

        usuario = verificar_token(token)

        if not usuario:
            return func(*args, **kwargs)

        try:

            from src.repositories.usuario_repository import (
                UsuarioRepository
            )

            usuario_db = UsuarioRepository.obtener_por_id(
                usuario["usuario_id"]
            )

        except Exception:
            return func(*args, **kwargs)

        if not usuario_db:
            return func(*args, **kwargs)

        if (
            not usuario_db["usuario_activo"]
            or not usuario_db["persona_activa"]
        ):
            return func(*args, **kwargs)

        usuario["rol"] = usuario_db["rol"]
        usuario["persona_id"] = usuario_db["persona_id"]
        usuario["alumno_id"] = usuario_db.get("alumno_id")
        usuario["profesor_id"] = usuario_db.get("profesor_id")

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