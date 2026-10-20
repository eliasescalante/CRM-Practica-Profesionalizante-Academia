from database.connection import get_db_connection

class UsuarioRepository:

    @staticmethod
    def obtener_por_usuario_o_email(identificador):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                u.id AS usuario_id,
                u.usuario,
                u.contrasenia,
                u.rol,
                u.activo AS usuario_activo,

                p.id AS persona_id,
                p.nombre,
                p.apellido,
                p.email,
                p.avatar,
                p.activo AS persona_activa

            FROM usuario u

            INNER JOIN persona p
                ON u.persona_id = p.id

            WHERE u.usuario = %s
               OR p.email = %s

            LIMIT 1;
        """

        cursor.execute(query, (identificador, identificador))

        usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        return usuario

    @staticmethod
    def registrar_alumno(datos):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            # -------------------------------------------------
            # 1. Crear persona
            # -------------------------------------------------

            query_persona = """
                INSERT INTO persona (
                    dni,
                    nombre,
                    apellido,
                    email,
                    telefono,
                    fecha_nacimiento,
                    contacto_emergencia
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(
                query_persona,
                (
                    datos["dni"],
                    datos["nombre"],
                    datos["apellido"],
                    datos["email"],
                    datos.get("telefono"),
                    datos.get("fecha_nacimiento"),
                    datos.get("contacto_emergencia")
                )
            )

            persona_id = cursor.lastrowid

            # -------------------------------------------------
            # 2. Crear usuario
            # -------------------------------------------------

            query_usuario = """
                INSERT INTO usuario (
                    persona_id,
                    usuario,
                    contrasenia,
                    rol
                )
                VALUES (%s, %s, %s, 'ALUMNO')
            """

            cursor.execute(
                query_usuario,
                (
                    persona_id,
                    datos["usuario"],
                    datos["contrasenia"]
                )
            )

            usuario_id = cursor.lastrowid

            # -------------------------------------------------
            # 3. Crear alumno
            # -------------------------------------------------

            query_alumno = """
                INSERT INTO alumno (
                    persona_id,
                    centro_id,
                    profesor_id,
                    fecha_de_inicio
                )
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                query_alumno,
                (
                    persona_id,
                    datos["centro_id"],
                    datos["profesor_id"],
                    datos["fecha_inicio"]
                )
            )

            alumno_id = cursor.lastrowid

            conn.commit()

            return {
                "usuario_id": usuario_id,
                "persona_id": persona_id,
                "alumno_id": alumno_id
            }

        except Exception:


            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

    @staticmethod
    def registrar_profesor(persona_id, usuario, contrasenia):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query = """
                INSERT INTO usuario (
                    persona_id,
                    usuario,
                    contrasenia,
                    rol
                )
                VALUES (%s, %s, %s, 'PROFESOR')
            """

            cursor.execute(
                query,
                (
                    persona_id,
                    usuario,
                    contrasenia
                )
            )

            usuario_id = cursor.lastrowid

            conn.commit()

            return {
                "usuario_id": usuario_id,
                "persona_id": persona_id,
                "usuario": usuario,
                "rol": "PROFESOR"
            }

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    
    @staticmethod
    def obtener_por_id(usuario_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT
                    u.id AS usuario_id,
                    u.usuario,
                    u.rol,
                    u.activo AS usuario_activo,
                    p.id AS persona_id,
                    p.nombre,
                    p.apellido,
                    p.email,
                    p.avatar,
                    p.activo AS persona_activa
                FROM usuario u
                INNER JOIN persona p
                    ON u.persona_id = p.id
                WHERE u.id = %s
                LIMIT 1
            """

            cursor.execute(query, (usuario_id,))
            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    
    @staticmethod
    def obtener_perfil_por_id(usuario_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT
                    u.id AS usuario_id,
                    u.usuario,
                    u.rol,
                    u.activo AS usuario_activo,
                    p.id AS persona_id,
                    p.dni,
                    p.nombre,
                    p.apellido,
                    p.email,
                    p.telefono,
                    p.fecha_nacimiento,
                    p.contacto_emergencia,
                    p.avatar,
                    p.activo AS persona_activa
                FROM usuario u
                INNER JOIN persona p ON u.persona_id = p.id
                WHERE u.id = %s
                LIMIT 1
            """

            cursor.execute(query, (usuario_id,))
            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar_perfil(usuario_id, datos):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        campos_permitidos = {
            "nombre",
            "apellido",
            "email",
            "telefono",
            "fecha_nacimiento",
            "contacto_emergencia"
        }

        try:
            cursor.execute(
                "SELECT persona_id FROM usuario WHERE id = %s",
                (usuario_id,)
            )
            usuario = cursor.fetchone()

            if not usuario:
                return None

            persona_id = usuario["persona_id"]

            # Verificar que el email no pertenezca a otra persona.
            if "email" in datos:
                cursor.execute(
                    """
                    SELECT id
                    FROM persona
                    WHERE email = %s AND id <> %s
                    LIMIT 1
                    """,
                    (datos["email"], persona_id)
                )

                if cursor.fetchone():
                    raise ValueError("EMAIL_EXISTENTE")

            campos = {
                campo: valor
                for campo, valor in datos.items()
                if campo in campos_permitidos
            }

            if not campos:
                return False

            asignaciones = ", ".join(
                f"{campo} = %s" for campo in campos
            )
            valores = list(campos.values())
            valores.append(persona_id)

            query = f"""
                UPDATE persona
                SET {asignaciones}
                WHERE id = %s
            """

            cursor.execute(query, tuple(valores))
            conn.commit()

            return True

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obtener_hash_contrasenia(usuario_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT contrasenia
                FROM usuario
                WHERE id = %s
                LIMIT 1
                """,
                (usuario_id,)
            )
            resultado = cursor.fetchone()
            return resultado["contrasenia"] if resultado else None

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar_contrasenia(usuario_id, nuevo_hash):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE usuario
                SET contrasenia = %s
                WHERE id = %s
                """,
                (nuevo_hash, usuario_id)
            )

            if cursor.rowcount == 0:
                conn.rollback()
                return False

            conn.commit()
            return True

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obtener_perfil_por_id(usuario_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT
                    u.id AS usuario_id,
                    u.usuario,
                    u.rol,
                    u.activo AS usuario_activo,
                    p.id AS persona_id,
                    p.dni,
                    p.nombre,
                    p.apellido,
                    p.email,
                    p.telefono,
                    p.fecha_nacimiento,
                    p.contacto_emergencia,
                    p.avatar,
                    p.activo AS persona_activa
                FROM usuario u
                INNER JOIN persona p ON u.persona_id = p.id
                WHERE u.id = %s
                LIMIT 1
            """

            cursor.execute(query, (usuario_id,))
            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()