#agregado docs
from database.connection import get_db_connection


class CuotaRepository:

    # =========================================================
    # LISTAR CUOTAS
    # =========================================================

    @staticmethod
    def listar():

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    c.id AS cuota_id,
                    c.alumno_id,
                    c.centro_id,
                    c.periodo_mes,
                    c.periodo_anio,
                    c.monto,
                    c.fecha_vencimiento,
                    c.estado,
                    c.fecha_generacion,

                    p.nombre AS alumno_nombre,
                    p.apellido AS alumno_apellido,

                    ce.nombre AS centro_nombre

                FROM cuota c

                INNER JOIN alumno a
                    ON c.alumno_id = a.id

                INNER JOIN persona p
                    ON a.persona_id = p.id

                INNER JOIN centro ce
                    ON c.centro_id = ce.id

                ORDER BY
                    c.fecha_vencimiento ASC
            """

            cursor.execute(query)

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # OBTENER CUOTA POR ID
    # =========================================================

    @staticmethod
    def obtener_por_id(cuota_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    c.id AS cuota_id,
                    c.alumno_id,
                    c.centro_id,
                    c.periodo_mes,
                    c.periodo_anio,
                    c.monto,
                    c.fecha_vencimiento,
                    c.estado,
                    c.fecha_generacion,

                    p.nombre AS alumno_nombre,
                    p.apellido AS alumno_apellido,

                    ce.nombre AS centro_nombre

                FROM cuota c

                INNER JOIN alumno a
                    ON c.alumno_id = a.id

                INNER JOIN persona p
                    ON a.persona_id = p.id

                INNER JOIN centro ce
                    ON c.centro_id = ce.id

                WHERE c.id = %s

                LIMIT 1
            """

            cursor.execute(query, (cuota_id,))

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # CUOTAS DE UN ALUMNO
    # =========================================================

    @staticmethod
    def listar_por_alumno(alumno_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    c.id AS cuota_id,
                    c.alumno_id,
                    c.centro_id,
                    c.periodo_mes,
                    c.periodo_anio,
                    c.monto,
                    c.fecha_vencimiento,
                    c.estado,
                    c.fecha_generacion,

                    ce.nombre AS centro_nombre

                FROM cuota c

                INNER JOIN centro ce
                    ON c.centro_id = ce.id

                WHERE c.alumno_id = %s

                ORDER BY
                    c.periodo_anio DESC,
                    c.periodo_mes DESC
            """

            cursor.execute(query, (alumno_id,))

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # CREAR CUOTA
    # =========================================================

    @staticmethod
    def crear(datos):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            query = """
                INSERT INTO cuota (
                    alumno_id,
                    centro_id,
                    periodo_mes,
                    periodo_anio,
                    monto,
                    fecha_vencimiento,
                    estado
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                )
            """

            cursor.execute(
                query,
                (
                    datos["alumno_id"],
                    datos["centro_id"],
                    datos["periodo_mes"],
                    datos["periodo_anio"],
                    datos["monto"],
                    datos["fecha_vencimiento"],
                    datos.get("estado", "PENDIENTE")
                )
            )

            cuota_id = cursor.lastrowid

            conn.commit()

            return cuota_id

        except Exception:

            conn.rollback()
            raise

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # ACTUALIZAR CUOTA
    # =========================================================

    @staticmethod
    def actualizar(cuota_id, datos):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            query = """
                UPDATE cuota
                SET
                    alumno_id = %s,
                    centro_id = %s,
                    periodo_mes = %s,
                    periodo_anio = %s,
                    monto = %s,
                    fecha_vencimiento = %s,
                    estado = %s
                WHERE id = %s
            """

            cursor.execute(
                query,
                (
                    datos["alumno_id"],
                    datos["centro_id"],
                    datos["periodo_mes"],
                    datos["periodo_anio"],
                    datos["monto"],
                    datos["fecha_vencimiento"],
                    datos["estado"],
                    cuota_id
                )
            )

            actualizado = cursor.rowcount > 0

            conn.commit()

            return actualizado

        except Exception:

            conn.rollback()
            raise

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # ELIMINAR CUOTA
    # =========================================================

    @staticmethod
    def eliminar(cuota_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            query = """
                DELETE FROM cuota
                WHERE id = %s
            """

            cursor.execute(query, (cuota_id,))

            eliminado = cursor.rowcount > 0

            conn.commit()

            return eliminado

        except Exception:

            conn.rollback()
            raise

        finally:

            cursor.close()
            conn.close()