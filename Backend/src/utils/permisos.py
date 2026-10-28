"""Reglas de acceso a los datos del propio usuario.

El token ya trae el rol, el persona_id y (gracias a auth.py) el alumno_id y
profesor_id de la cuenta. Estas funciones evitan que un ALUMNO lea o escriba
información de otros alumnos enviando un id distinto en la URL o en el body.
"""

from flask import jsonify

from database.connection import get_db_connection


# =========================================================
# RESPUESTAS
# =========================================================

def denegado(mensaje="No tenés permisos para acceder a estos datos"):

    return jsonify({
        "status": "ERROR",
        "mensaje": mensaje
    }), 403


# =========================================================
# ROLES
# =========================================================

def es_alumno(usuario):

    return bool(usuario) and usuario.get("rol") == "ALUMNO"


def es_admin(usuario):

    return bool(usuario) and usuario.get("rol") == "ADMIN"


def es_staff(usuario):

    return bool(usuario) and usuario.get("rol") in ("ADMIN", "PROFESOR")


# =========================================================
# ALUMNO PROPIO
# =========================================================

def alumno_propio(usuario, alumno_id):
    """True si el usuario puede operar sobre ese alumno.

    El staff puede operar sobre cualquier alumno; un ALUMNO solo sobre el
    suyo. Si el token no tiene alumno_id asociado, se niega el acceso.
    """

    if not es_alumno(usuario):
        return True

    propio = usuario.get("alumno_id")

    if propio is None or alumno_id is None:
        return False

    try:

        return int(propio) == int(alumno_id)

    except (TypeError, ValueError):

        return False


def exigir_alumno_propio(usuario, alumno_id):
    """Devuelve una respuesta 403 si el ALUMNO no es el dueño, o None."""

    if alumno_propio(usuario, alumno_id):
        return None

    return denegado(
        "Solo podés acceder a la información de tu propio alumno"
    )


# =========================================================
# DATOS DEL ALUMNO
# =========================================================

def datos_alumno(alumno_id):
    """Devuelve centro_id y profesor_id del alumno, o None si no existe."""

    if alumno_id is None:
        return None

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                a.id AS alumno_id,
                a.centro_id,
                a.profesor_id,
                a.estado
            FROM alumno a
            WHERE a.id = %s
            LIMIT 1
            """,
            (alumno_id,)
        )

        return cursor.fetchone()

    finally:

        cursor.close()
        conn.close()


# =========================================================
# CENTROS DEL USUARIO
# =========================================================

def centros_del_usuario(usuario):
    """IDs de sede a los que pertenece el usuario autenticado."""

    if not usuario:
        return set()

    if es_admin(usuario):
        return None  # None significa "todas"

    if es_alumno(usuario):

        alumno = datos_alumno(usuario.get("alumno_id"))

        if not alumno or not alumno.get("centro_id"):
            return set()

        return {int(alumno["centro_id"])}

    profesor_id = usuario.get("profesor_id")

    if not profesor_id:
        return set()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT centro_id
            FROM profesor_centro
            WHERE profesor_id = %s
            """,
            (profesor_id,)
        )

        return {
            int(fila["centro_id"])
            for fila in cursor.fetchall()
            if fila.get("centro_id") is not None
        }

    finally:

        cursor.close()
        conn.close()


def puede_acceder_centro(usuario, centro_id):
    """True si el usuario puede ver/operar sobre esa sede."""

    if not usuario or centro_id is None:
        return False

    if es_admin(usuario):
        return True

    sedes = centros_del_usuario(usuario)

    try:

        return int(centro_id) in sedes

    except (TypeError, ValueError):

        return False


def exigir_centro(usuario, centro_id):
    """Devuelve una respuesta 403 si la sede no es del usuario, o None."""

    if puede_acceder_centro(usuario, centro_id):
        return None

    return denegado(
        "Solo podés acceder a la información de tu propia sede"
    )
