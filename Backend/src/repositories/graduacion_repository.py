from database.connection import get_db_connection


class GraduacionRepository:

    # =========================================================
    # LISTAR GRADUACIONES
    # =========================================================

    @staticmethod
    def listar():

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    g.id,
                    g.alumno_id,
                    g.centro_id,
                    g.grado,
                    g.fecha,

                    p.nombre AS alumno_nombre,
                    p.apellido AS alumno_apellido,

                    c.nombre AS centro_nombre

                FROM graduacion g

                INNER JOIN alumno a
                    ON g.alumno_id = a.id

                INNER JOIN persona p
                    ON a.persona_id = p.id

                INNER JOIN centro c
                    ON g.centro_id = c.id

                ORDER BY g.fecha DESC
            """

            cursor.execute(query)

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # OBTENER POR ID
    # =========================================================

    @staticmethod
    def obtener_por_id(graduacion_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    g.id,
                    g.alumno_id,
                    g.centro_id,
                    g.grado,
                    g.fecha,

                    p.nombre AS alumno_nombre,
                    p.apellido AS alumno_apellido,

                    c.nombre AS centro_nombre

                FROM graduacion g

                INNER JOIN alumno a
                    ON g.alumno_id = a.id

                INNER JOIN persona p
                    ON a.persona_id = p.id

                INNER JOIN centro c
                    ON g.centro_id = c.id

                WHERE g.id = %s
            """

            cursor.execute(query, (graduacion_id,))

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # LISTAR POR ALUMNO
    # =========================================================

    @staticmethod
    def listar_por_alumno(alumno_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    g.id,
                    g.alumno_id,
                    g.centro_id,
                    g.grado,
                    g.fecha,
                    c.nombre AS centro_nombre

                FROM graduacion g

                INNER JOIN centro c
                    ON g.centro_id = c.id

                WHERE g.alumno_id = %s

                ORDER BY g.fecha DESC
            """

            cursor.execute(query, (alumno_id,))

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # CREAR GRADUACIÓN
    # =========================================================

    @staticmethod
    def crear(datos):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            query = """
                INSERT INTO graduacion (
                    alumno_id,
                    centro_id,
                    grado,
                    fecha
                )
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    datos["alumno_id"],
                    datos["centro_id"],
                    datos["grado"],
                    datos["fecha"]
                )
            )

            graduacion_id = cursor.lastrowid

            conn.commit()

            return graduacion_id

        except Exception:

            conn.rollback()
            raise

        finally:

            cursor.close()
            conn.close()