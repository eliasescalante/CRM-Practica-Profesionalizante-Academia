#agregado docs
from database.connection import get_db_connection


class AsistenciaRepository:

    # =========================================================
    # LISTAR ASISTENCIAS
    # =========================================================

    @staticmethod
    def listar():

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    a.id AS asistencia_id,
                    a.alumno_id,
                    a.centro_id,
                    a.fecha,
                    a.presente,
                    a.observacion,

                    p.nombre AS alumno_nombre,
                    p.apellido AS alumno_apellido,

                    c.nombre AS centro_nombre

                FROM asistencia a

                INNER JOIN alumno al
                    ON a.alumno_id = al.id

                INNER JOIN persona p
                    ON al.persona_id = p.id

                INNER JOIN centro c
                    ON a.centro_id = c.id

                ORDER BY a.fecha DESC
            """

            cursor.execute(query)

            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # OBTENER ASISTENCIA POR ID
    # =========================================================

    @staticmethod
    def obtener_por_id(asistencia_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    a.id AS asistencia_id,
                    a.alumno_id,
                    a.centro_id,
                    a.fecha,
                    a.presente,
                    a.observacion,

                    p.nombre AS alumno_nombre,
                    p.apellido AS alumno_apellido,

                    c.nombre AS centro_nombre

                FROM asistencia a

                INNER JOIN alumno al
                    ON a.alumno_id = al.id

                INNER JOIN persona p
                    ON al.persona_id = p.id

                INNER JOIN centro c
                    ON a.centro_id = c.id

                WHERE a.id = %s

                LIMIT 1
            """

            cursor.execute(query, (asistencia_id,))

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # LISTAR ASISTENCIAS DE UN ALUMNO
    # =========================================================

    @staticmethod
    def listar_por_alumno(alumno_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    a.id AS asistencia_id,
                    a.alumno_id,
                    a.centro_id,
                    a.fecha,
                    a.presente,
                    a.observacion,

                    c.nombre AS centro_nombre

                FROM asistencia a

                INNER JOIN centro c
                    ON a.centro_id = c.id

                WHERE a.alumno_id = %s

                ORDER BY a.fecha DESC
            """

            cursor.execute(query, (alumno_id,))

            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # LISTAR ASISTENCIAS DE UN CENTRO
    # =========================================================

    @staticmethod
    def listar_por_centro(centro_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    a.id AS asistencia_id,
                    a.alumno_id,
                    a.centro_id,
                    a.fecha,
                    a.presente,
                    a.observacion,

                    p.nombre AS alumno_nombre,
                    p.apellido AS alumno_apellido

                FROM asistencia a

                INNER JOIN alumno al
                    ON a.alumno_id = al.id

                INNER JOIN persona p
                    ON al.persona_id = p.id

                WHERE a.centro_id = %s

                ORDER BY a.fecha DESC
            """

            cursor.execute(query, (centro_id,))

            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # CREAR ASISTENCIA
    # =========================================================

    @staticmethod
    def crear(datos):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            query = """
                INSERT INTO asistencia (
                    alumno_id,
                    centro_id,
                    fecha,
                    presente,
                    observacion
                )
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    datos["alumno_id"],
                    datos["centro_id"],
                    datos.get("fecha"),
                    datos.get("presente", True),
                    datos.get("observacion")
                )
            )

            asistencia_id = cursor.lastrowid

            conn.commit()

            return asistencia_id

        except Exception:

            conn.rollback()
            raise

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # ACTUALIZAR ASISTENCIA
    # =========================================================

    @staticmethod
    def actualizar(asistencia_id, datos):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT id
                FROM asistencia
                WHERE id = %s
                LIMIT 1
                """,
                (asistencia_id,)
            )

            asistencia = cursor.fetchone()

            if not asistencia:
                return False

            query = """
                UPDATE asistencia
                SET
                    alumno_id = %s,
                    centro_id = %s,
                    fecha = %s,
                    presente = %s,
                    observacion = %s
                WHERE id = %s
            """

            cursor.execute(
                query,
                (
                    datos["alumno_id"],
                    datos["centro_id"],
                    datos["fecha"],
                    datos["presente"],
                    datos.get("observacion"),
                    asistencia_id
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


    # =========================================================
    # ELIMINAR ASISTENCIA
    # =========================================================

    @staticmethod
    def eliminar(asistencia_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT id
                FROM asistencia
                WHERE id = %s
                LIMIT 1
                """,
                (asistencia_id,)
            )

            asistencia = cursor.fetchone()

            if not asistencia:
                return False

            cursor.execute(
                """
                DELETE FROM asistencia
                WHERE id = %s
                """,
                (asistencia_id,)
            )

            conn.commit()

            return True

        except Exception:

            conn.rollback()
            raise

        finally:

            cursor.close()
            conn.close()