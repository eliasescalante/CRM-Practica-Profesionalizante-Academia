from database.connection import get_db_connection


class ProfesorRepository:

    # =========================================================
    # LISTAR PROFESORES
    # =========================================================

    @staticmethod
    def listar(incluir_inactivos=False):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT
                    pr.id AS profesor_id,
                    pr.persona_id,
                    pr.fecha_alta,
                    pr.activo AS profesor_activo,

                    p.dni,
                    p.nombre,
                    p.apellido,
                    p.email,
                    p.telefono,
                    p.fecha_nacimiento,
                    p.contacto_emergencia,
                    p.avatar,
                    p.activo AS persona_activa,

                    u.id AS usuario_id,
                    u.usuario,
                    u.rol,
                    u.activo AS usuario_activo

                FROM profesor pr

                INNER JOIN persona p
                    ON pr.persona_id = p.id

                LEFT JOIN usuario u
                    ON u.persona_id = p.id
            """

            if not incluir_inactivos:
                query += """
                    WHERE pr.activo = TRUE
                    AND p.activo = TRUE
                    AND (u.activo = TRUE OR u.activo IS NULL)
                """

            query += """
                ORDER BY p.apellido ASC, p.nombre ASC
            """

            cursor.execute(query)
            profesores = cursor.fetchall()

            # Adjuntamos centros
            for profesor in profesores:
                profesor["centros"] = ProfesorRepository.obtener_centros_con_conexion(
                    cursor, profesor["profesor_id"]
                )

            return profesores

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # OBTENER PROFESOR POR ID
    # =========================================================

    @staticmethod
    def obtener_por_id(profesor_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT
                    pr.id AS profesor_id,
                    pr.persona_id,
                    pr.fecha_alta,
                    pr.activo AS profesor_activo,

                    p.dni,
                    p.nombre,
                    p.apellido,
                    p.email,
                    p.telefono,
                    p.fecha_nacimiento,
                    p.contacto_emergencia,
                    p.avatar,
                    p.activo AS persona_activa,

                    u.id AS usuario_id,
                    u.usuario,
                    u.rol,
                    u.activo AS usuario_activo

                FROM profesor pr

                INNER JOIN persona p
                    ON pr.persona_id = p.id

                LEFT JOIN usuario u
                    ON u.persona_id = p.id

                WHERE pr.id = %s

                LIMIT 1
            """

            cursor.execute(query, (profesor_id,))
            profesor = cursor.fetchone()

            if not profesor:
                return None

            profesor["centros"] = ProfesorRepository.obtener_centros_con_conexion(
                cursor, profesor_id
            )

            return profesor

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # HELPER: OBTENER CENTROS USANDO EL MISMO CURSOR
    # =========================================================

    @staticmethod
    def obtener_centros_con_conexion(cursor, profesor_id):
        query = """
            SELECT
                c.id AS centro_id,
                c.nombre AS centro_nombre,
                c.direccion,
                c.telefono,
                c.activo

            FROM profesor_centro pc

            INNER JOIN centro c
                ON pc.centro_id = c.id

            WHERE pc.profesor_id = %s

            ORDER BY c.nombre ASC
        """
        cursor.execute(query, (profesor_id,))
        return cursor.fetchall()


    # =========================================================
    # OBTENER CENTROS DE UN PROFESOR (MÉTODO PÚBLICO EXTERNO)
    # =========================================================

    @staticmethod
    def obtener_centros(profesor_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            return ProfesorRepository.obtener_centros_con_conexion(cursor, profesor_id)
        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # BUSCAR POR DNI
    # =========================================================

    @staticmethod
    def obtener_por_dni(dni):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            query = """
                SELECT
                    pr.id AS profesor_id,
                    pr.persona_id
                FROM profesor pr

                INNER JOIN persona p
                    ON pr.persona_id = p.id

                WHERE p.dni = %s

                LIMIT 1
            """
            cursor.execute(query, (dni,))
            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # BUSCAR POR EMAIL
    # =========================================================

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


    # =========================================================
    # BUSCAR POR USUARIO
    # =========================================================

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


    # =========================================================
    # CREAR PROFESOR
    # =========================================================

    @staticmethod
    def crear(datos):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query_persona = """
                INSERT INTO persona (
                    dni, nombre, apellido, email, telefono,
                    fecha_nacimiento, contacto_emergencia, avatar
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

            query_usuario = """
                INSERT INTO usuario (
                    persona_id, usuario, contrasenia, rol, activo
                )
                VALUES (%s, %s, %s, 'PROFESOR', TRUE)
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

            query_profesor = """
                INSERT INTO profesor (
                    persona_id, fecha_alta, activo
                )
                VALUES (%s, %s, TRUE)
            """

            cursor.execute(
                query_profesor,
                (
                    persona_id,
                    datos.get("fecha_alta")
                )
            )
            profesor_id = cursor.lastrowid

            centros = datos.get("centro_ids", [])
            for centro_id in centros:
                query_centro = """
                    INSERT INTO profesor_centro (profesor_id, centro_id)
                    VALUES (%s, %s)
                """
                cursor.execute(query_centro, (profesor_id, centro_id))

            conn.commit()

            return {
                "profesor_id": profesor_id,
                "persona_id": persona_id,
                "usuario_id": usuario_id
            }

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # ACTUALIZAR PROFESOR
    # =========================================================

    @staticmethod
    def actualizar(profesor_id, datos):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT persona_id FROM profesor WHERE id = %s LIMIT 1",
                (profesor_id,)
            )
            profesor = cursor.fetchone()

            if not profesor:
                return False

            persona_id = profesor[0]

            query_persona = """
                UPDATE persona
                SET
                    dni = %s, nombre = %s, apellido = %s, email = %s,
                    telefono = %s, fecha_nacimiento = %s,
                    contacto_emergencia = %s, avatar = %s
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

            query_usuario = "UPDATE usuario SET usuario = %s WHERE persona_id = %s"
            cursor.execute(query_usuario, (datos["usuario"], persona_id))

            query_profesor = "UPDATE profesor SET activo = %s WHERE id = %s"
            cursor.execute(query_profesor, (datos["activo"], profesor_id))

            if "centro_ids" in datos and datos["centro_ids"] is not None:
                cursor.execute("DELETE FROM profesor_centro WHERE profesor_id = %s", (profesor_id,))
                for centro_id in datos["centro_ids"]:
                    cursor.execute(
                        "INSERT INTO profesor_centro (profesor_id, centro_id) VALUES (%s, %s)",
                        (profesor_id, centro_id)
                    )

            conn.commit()
            return True

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # BAJA LÓGICA
    # =========================================================

    @staticmethod
    def eliminar(profesor_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT persona_id FROM profesor WHERE id = %s LIMIT 1", (profesor_id,))
            profesor = cursor.fetchone()

            if not profesor:
                return False

            persona_id = profesor[0]

            cursor.execute("UPDATE profesor SET activo = FALSE WHERE id = %s", (profesor_id,))
            cursor.execute("UPDATE persona SET activo = FALSE WHERE id = %s", (persona_id,))
            cursor.execute("UPDATE usuario SET activo = FALSE WHERE persona_id = %s", (persona_id,))

            conn.commit()
            return True

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()