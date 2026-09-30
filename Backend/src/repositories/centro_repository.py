from database.connection import get_db_connection


class CentroRepository:

    # =========================================================
    # LISTAR CENTROS
    # =========================================================

    @staticmethod
    def listar(incluir_inactivos=False):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    id AS centro_id,
                    nombre,
                    direccion,
                    telefono,
                    activo,
                    captura
                FROM centro
            """

            if not incluir_inactivos:
                query += """
                    WHERE activo = TRUE
                """

            query += """
                ORDER BY nombre ASC
            """

            cursor.execute(query)

            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # OBTENER CENTRO POR ID
    # =========================================================

    @staticmethod
    def obtener_por_id(centro_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    id AS centro_id,
                    nombre,
                    direccion,
                    telefono,
                    activo,
                    captura
                FROM centro
                WHERE id = %s
                LIMIT 1
            """

            cursor.execute(query, (centro_id,))

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # OBTENER CENTRO POR NOMBRE
    # =========================================================

    @staticmethod
    def obtener_por_nombre(nombre):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    id AS centro_id,
                    nombre,
                    direccion,
                    telefono,
                    activo,
                    captura
                FROM centro
                WHERE nombre = %s
                LIMIT 1
            """

            cursor.execute(query, (nombre,))

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # CREAR CENTRO
    # =========================================================

    @staticmethod
    def crear(datos):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            query = """
                INSERT INTO centro (
                    nombre,
                    direccion,
                    telefono,
                    captura
                )
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    datos["nombre"],
                    datos.get("direccion"),
                    datos.get("telefono"),
                    datos.get("captura")
                )
            )

            centro_id = cursor.lastrowid

            conn.commit()

            return centro_id

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # ACTUALIZAR CENTRO
    # =========================================================

    @staticmethod
    def actualizar(centro_id, datos):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            query = """
                UPDATE centro
                SET
                    nombre = %s,
                    direccion = %s,
                    telefono = %s,
                    activo = %s,
                    captura = %s
                WHERE id = %s
            """

            cursor.execute(
                query,
                (
                    datos["nombre"],
                    datos.get("direccion"),
                    datos.get("telefono"),
                    datos.get("activo", True),
                    datos.get("captura"),
                    centro_id
                )
            )

            if cursor.rowcount == 0:
                return False

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
    def eliminar(centro_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            query = """
                UPDATE centro
                SET activo = FALSE
                WHERE id = %s
            """

            cursor.execute(query, (centro_id,))

            if cursor.rowcount == 0:
                return False

            conn.commit()

            return True

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()