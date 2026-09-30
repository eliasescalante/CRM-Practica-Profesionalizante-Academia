from database.connection import get_db_connection


class ExamenRepository:

    # =========================================================
    # LISTAR EXÁMENES
    # =========================================================

    @staticmethod
    def listar(incluir_inactivos=False):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    ep.id AS examen_id,
                    ep.centro_id,
                    ep.profesor_id,
                    ep.titulo,
                    ep.fecha_examen,
                    ep.monto,
                    ep.activo,

                    c.nombre AS centro_nombre,

                    pp.nombre AS profesor_nombre,
                    pp.apellido AS profesor_apellido,

                    (
                        SELECT COUNT(*)
                        FROM inscripcion_examen ie
                        WHERE ie.examen_id = ep.id
                    ) AS cantidad_inscriptos

                FROM examen_programado ep

                INNER JOIN centro c
                    ON ep.centro_id = c.id

                INNER JOIN profesor pr
                    ON ep.profesor_id = pr.id

                INNER JOIN persona pp
                    ON pr.persona_id = pp.id
            """

            if not incluir_inactivos:
                query += """
                    WHERE ep.activo = TRUE
                """

            query += """
                ORDER BY ep.fecha_examen ASC
            """

            cursor.execute(query)

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # LISTAR PRÓXIMOS EXÁMENES
    # =========================================================

    @staticmethod
    def listar_proximos():

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    ep.id AS examen_id,
                    ep.centro_id,
                    ep.profesor_id,
                    ep.titulo,
                    ep.fecha_examen,
                    ep.monto,
                    ep.activo,

                    c.nombre AS centro_nombre,

                    pp.nombre AS profesor_nombre,
                    pp.apellido AS profesor_apellido,

                    (
                        SELECT COUNT(*)
                        FROM inscripcion_examen ie
                        WHERE ie.examen_id = ep.id
                    ) AS cantidad_inscriptos

                FROM examen_programado ep

                INNER JOIN centro c
                    ON ep.centro_id = c.id

                INNER JOIN profesor pr
                    ON ep.profesor_id = pr.id

                INNER JOIN persona pp
                    ON pr.persona_id = pp.id

                WHERE ep.activo = TRUE
                  AND ep.fecha_examen >= NOW()

                ORDER BY ep.fecha_examen ASC
            """

            cursor.execute(query)

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # OBTENER EXAMEN POR ID
    # =========================================================

    @staticmethod
    def obtener_por_id(examen_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    ep.id AS examen_id,
                    ep.centro_id,
                    ep.profesor_id,
                    ep.titulo,
                    ep.fecha_examen,
                    ep.monto,
                    ep.activo,

                    c.nombre AS centro_nombre,

                    pp.nombre AS profesor_nombre,
                    pp.apellido AS profesor_apellido,

                    (
                        SELECT COUNT(*)
                        FROM inscripcion_examen ie
                        WHERE ie.examen_id = ep.id
                    ) AS cantidad_inscriptos

                FROM examen_programado ep

                INNER JOIN centro c
                    ON ep.centro_id = c.id

                INNER JOIN profesor pr
                    ON ep.profesor_id = pr.id

                INNER JOIN persona pp
                    ON pr.persona_id = pp.id

                WHERE ep.id = %s

                LIMIT 1
            """

            cursor.execute(query, (examen_id,))

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # CREAR EXAMEN
    # =========================================================

    @staticmethod
    def crear(datos):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            query = """
                INSERT INTO examen_programado (
                    centro_id,
                    profesor_id,
                    titulo,
                    fecha_examen,
                    monto,
                    activo
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    TRUE
                )
            """

            cursor.execute(
                query,
                (
                    datos["centro_id"],
                    datos["profesor_id"],
                    datos["titulo"],
                    datos["fecha_examen"],
                    datos["monto"]
                )
            )

            examen_id = cursor.lastrowid

            conn.commit()

            return examen_id

        except Exception:

            conn.rollback()
            raise

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # ACTUALIZAR EXAMEN
    # =========================================================

    @staticmethod
    def actualizar(examen_id, datos):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT id
                FROM examen_programado
                WHERE id = %s
                LIMIT 1
                """,
                (examen_id,)
            )

            examen = cursor.fetchone()

            if not examen:
                return False

            query = """
                UPDATE examen_programado
                SET
                    centro_id = %s,
                    profesor_id = %s,
                    titulo = %s,
                    fecha_examen = %s,
                    monto = %s,
                    activo = %s
                WHERE id = %s
            """

            cursor.execute(
                query,
                (
                    datos["centro_id"],
                    datos["profesor_id"],
                    datos["titulo"],
                    datos["fecha_examen"],
                    datos["monto"],
                    datos.get("activo", True),
                    examen_id
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
    # BAJA LÓGICA
    # =========================================================

    @staticmethod
    def eliminar(examen_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                UPDATE examen_programado
                SET activo = FALSE
                WHERE id = %s
                """,
                (examen_id,)
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
    # LISTAR INSCRIPTOS
    # =========================================================

    @staticmethod
    def listar_inscriptos(examen_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    ie.id AS inscripcion_id,
                    ie.examen_id,
                    ie.alumno_id,

                    p.nombre,
                    p.apellido,
                    p.dni,
                    p.email,
                    p.avatar,

                    a.centro_id,
                    c.nombre AS centro_nombre,

                    (
                        SELECT
                            pa.estado
                        FROM pago pa
                        WHERE pa.inscripcion_examen_id = ie.id
                        ORDER BY pa.fecha_registro DESC
                        LIMIT 1
                    ) AS estado_pago,

                    (
                        SELECT
                            pa.id
                        FROM pago pa
                        WHERE pa.inscripcion_examen_id = ie.id
                        ORDER BY pa.fecha_registro DESC
                        LIMIT 1
                    ) AS pago_id

                FROM inscripcion_examen ie

                INNER JOIN alumno a
                    ON ie.alumno_id = a.id

                INNER JOIN persona p
                    ON a.persona_id = p.id

                INNER JOIN centro c
                    ON a.centro_id = c.id

                WHERE ie.examen_id = %s

                ORDER BY p.apellido ASC, p.nombre ASC
            """

            cursor.execute(query, (examen_id,))

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # OBTENER INSCRIPCIÓN
    # =========================================================

    @staticmethod
    def obtener_inscripcion(inscripcion_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    ie.id AS inscripcion_id,
                    ie.examen_id,
                    ie.alumno_id,

                    ep.titulo AS examen_titulo,
                    ep.fecha_examen,
                    ep.monto AS examen_monto,

                    p.nombre AS alumno_nombre,
                    p.apellido AS alumno_apellido,

                    (
                        SELECT
                            pa.estado
                        FROM pago pa
                        WHERE pa.inscripcion_examen_id = ie.id
                        ORDER BY pa.fecha_registro DESC
                        LIMIT 1
                    ) AS estado_pago

                FROM inscripcion_examen ie

                INNER JOIN examen_programado ep
                    ON ie.examen_id = ep.id

                INNER JOIN alumno a
                    ON ie.alumno_id = a.id

                INNER JOIN persona p
                    ON a.persona_id = p.id

                WHERE ie.id = %s

                LIMIT 1
            """

            cursor.execute(
                query,
                (inscripcion_id,)
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # VERIFICAR INSCRIPCIÓN EXISTENTE
    # =========================================================

    @staticmethod
    def existe_inscripcion(examen_id, alumno_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    id AS inscripcion_id
                FROM inscripcion_examen
                WHERE examen_id = %s
                  AND alumno_id = %s
                LIMIT 1
            """

            cursor.execute(
                query,
                (
                    examen_id,
                    alumno_id
                )
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # INSCRIBIR ALUMNO
    # =========================================================

    @staticmethod
    def inscribir_alumno(examen_id, alumno_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            query = """
                INSERT INTO inscripcion_examen (
                    examen_id,
                    alumno_id
                )
                VALUES (
                    %s,
                    %s
                )
            """

            cursor.execute(
                query,
                (
                    examen_id,
                    alumno_id
                )
            )

            inscripcion_id = cursor.lastrowid

            conn.commit()

            return inscripcion_id

        except Exception:

            conn.rollback()
            raise

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # CANCELAR INSCRIPCIÓN
    # =========================================================

    @staticmethod
    def cancelar_inscripcion(inscripcion_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT id
                FROM inscripcion_examen
                WHERE id = %s
                LIMIT 1
                """,
                (inscripcion_id,)
            )

            inscripcion = cursor.fetchone()

            if not inscripcion:
                return False

            cursor.execute(
                """
                DELETE FROM inscripcion_examen
                WHERE id = %s
                """,
                (inscripcion_id,)
            )

            conn.commit()

            return True

        except Exception:

            conn.rollback()
            raise

        finally:

            cursor.close()
            conn.close()