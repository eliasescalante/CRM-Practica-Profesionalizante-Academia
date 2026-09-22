from database.connection import get_db_connection


class AlumnoRepository:

    @staticmethod
    def listar(incluir_inactivos=False):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT
                    a.id AS alumno_id,
                    a.persona_id,
                    a.centro_id,
                    a.profesor_id,
                    a.fecha_de_inicio,
                    a.fecha_alta,
                    a.estado,

                    p.dni,
                    p.nombre,
                    p.apellido,
                    p.email,
                    p.telefono,
                    p.fecha_nacimiento,
                    p.contacto_emergencia,
                    p.avatar,

                    u.id AS usuario_id,
                    u.usuario,
                    u.rol,
                    u.activo AS usuario_activo,

                    c.nombre AS centro_nombre,

                    pp.nombre AS profesor_nombre,
                    pp.apellido AS profesor_apellido

                FROM alumno a

                INNER JOIN persona p
                    ON a.persona_id = p.id

                INNER JOIN usuario u
                    ON u.persona_id = p.id

                INNER JOIN centro c
                    ON a.centro_id = c.id

                INNER JOIN profesor pr
                    ON a.profesor_id = pr.id

                INNER JOIN persona pp
                    ON pr.persona_id = pp.id
            """

            if not incluir_inactivos:
                query += """
                    WHERE a.estado != 'INACTIVO'
                """

            query += """
                ORDER BY p.apellido ASC, p.nombre ASC
            """

            cursor.execute(query)

            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obtener_por_id(alumno_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT
                    a.id AS alumno_id,
                    a.persona_id,
                    a.centro_id,
                    a.profesor_id,
                    a.fecha_de_inicio,
                    a.fecha_alta,
                    a.estado,

                    p.dni,
                    p.nombre,
                    p.apellido,
                    p.email,
                    p.telefono,
                    p.fecha_nacimiento,
                    p.contacto_emergencia,
                    p.avatar,

                    u.id AS usuario_id,
                    u.usuario,
                    u.rol,
                    u.activo AS usuario_activo,

                    c.nombre AS centro_nombre,

                    pp.nombre AS profesor_nombre,
                    pp.apellido AS profesor_apellido

                FROM alumno a

                INNER JOIN persona p
                    ON a.persona_id = p.id

                INNER JOIN usuario u
                    ON u.persona_id = p.id

                INNER JOIN centro c
                    ON a.centro_id = c.id

                INNER JOIN profesor pr
                    ON a.profesor_id = pr.id

                INNER JOIN persona pp
                    ON pr.persona_id = pp.id

                WHERE a.id = %s

                LIMIT 1
            """

            cursor.execute(query, (alumno_id,))

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obtener_por_dni(dni):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT
                    a.id AS alumno_id,
                    a.persona_id
                FROM alumno a
                INNER JOIN persona p
                    ON a.persona_id = p.id
                WHERE p.dni = %s
                LIMIT 1
            """

            cursor.execute(query, (dni,))

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obtener_por_email(email):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT
                    p.id AS persona_id,
                    p.email
                FROM persona p
                WHERE p.email = %s
                LIMIT 1
            """

            cursor.execute(query, (email,))

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obtener_por_usuario(usuario):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT
                    id AS usuario_id,
                    usuario
                FROM usuario
                WHERE usuario = %s
                LIMIT 1
            """

            cursor.execute(query, (usuario,))

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def crear(datos):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            # ---------------------------------------------
            # 1. Crear persona
            # ---------------------------------------------

            query_persona = """
                INSERT INTO persona (
                    dni,
                    nombre,
                    apellido,
                    email,
                    telefono,
                    fecha_nacimiento,
                    contacto_emergencia,
                    avatar
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
                    datos.get("contacto_emergencia"),
                    datos.get("avatar")
                )
            )

            persona_id = cursor.lastrowid

            # ---------------------------------------------
            # 2. Crear usuario
            # ---------------------------------------------

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

            # ---------------------------------------------
            # 3. Crear alumno
            # ---------------------------------------------

            query_alumno = """
                INSERT INTO alumno (
                    persona_id,
                    centro_id,
                    profesor_id,
                    fecha_de_inicio,
                    estado
                )
                VALUES (%s, %s, %s, %s, 'ACTIVO')
            """

            cursor.execute(
                query_alumno,
                (
                    persona_id,
                    datos["centro_id"],
                    datos["profesor_id"],
                    datos["fecha_de_inicio"]
                )
            )

            alumno_id = cursor.lastrowid

            conn.commit()

            return {
                "alumno_id": alumno_id,
                "persona_id": persona_id,
                "usuario_id": usuario_id
            }

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar(alumno_id, datos):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            # ---------------------------------------------
            # Obtener persona_id
            # ---------------------------------------------

            cursor.execute(
                """
                SELECT persona_id
                FROM alumno
                WHERE id = %s
                LIMIT 1
                """,
                (alumno_id,)
            )

            alumno = cursor.fetchone()

            if not alumno:
                return False

            persona_id = alumno[0]

            # ---------------------------------------------
            # Actualizar persona
            # ---------------------------------------------

            query_persona = """
                UPDATE persona
                SET
                    dni = %s,
                    nombre = %s,
                    apellido = %s,
                    email = %s,
                    telefono = %s,
                    fecha_nacimiento = %s,
                    contacto_emergencia = %s,
                    avatar = %s
                WHERE id = %s
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
                    datos.get("contacto_emergencia"),
                    datos.get("avatar"),
                    persona_id
                )
            )

            # ---------------------------------------------
            # Actualizar alumno
            # ---------------------------------------------

            query_alumno = """
                UPDATE alumno
                SET
                    centro_id = %s,
                    profesor_id = %s,
                    fecha_de_inicio = %s,
                    estado = %s
                WHERE id = %s
            """

            cursor.execute(
                query_alumno,
                (
                    datos["centro_id"],
                    datos["profesor_id"],
                    datos["fecha_de_inicio"],
                    datos["estado"],
                    alumno_id
                )
            )

            # ---------------------------------------------
            # Actualizar usuario
            # ---------------------------------------------

            query_usuario = """
                UPDATE usuario
                SET usuario = %s
                WHERE persona_id = %s
            """

            cursor.execute(
                query_usuario,
                (
                    datos["usuario"],
                    persona_id
                )
            )

            conn.commit()

            return True

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def eliminar(alumno_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            # ---------------------------------------------
            # Obtener persona_id
            # ---------------------------------------------

            cursor.execute(
                """
                SELECT persona_id
                FROM alumno
                WHERE id = %s
                LIMIT 1
                """,
                (alumno_id,)
            )

            alumno = cursor.fetchone()

            if not alumno:
                return False

            persona_id = alumno[0]

            # ---------------------------------------------
            # Baja lógica del alumno
            # ---------------------------------------------

            cursor.execute(
                """
                UPDATE alumno
                SET estado = 'INACTIVO'
                WHERE id = %s
                """,
                (alumno_id,)
            )

            # ---------------------------------------------
            # Desactivar usuario
            # ---------------------------------------------

            cursor.execute(
                """
                UPDATE usuario
                SET activo = FALSE
                WHERE persona_id = %s
                """,
                (persona_id,)
            )

            # ---------------------------------------------
            # Desactivar persona
            # ---------------------------------------------

            cursor.execute(
                """
                UPDATE persona
                SET activo = FALSE
                WHERE id = %s
                """,
                (persona_id,)
            )

            conn.commit()

            return True

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()