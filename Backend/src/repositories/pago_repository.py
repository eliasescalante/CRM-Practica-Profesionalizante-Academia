#agregado docs
from database.connection import get_db_connection


class PagoRepository:

    # =========================================================
    # LISTAR PAGOS
    # =========================================================

    @staticmethod
    def listar():

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    p.id AS pago_id,

                    p.alumno_id,
                    p.cuota_id,
                    p.inscripcion_examen_id,

                    p.profesor_id,
                    p.centro_id,

                    p.tipo_concepto,
                    p.descripcion,
                    p.monto,
                    p.metodo_pago,
                    p.comprobante_url,

                    p.estado,
                    p.fecha_registro,
                    p.fecha_confirmacion,

                    -- Datos del alumno
                    pa.nombre AS alumno_nombre,
                    pa.apellido AS alumno_apellido,

                    -- Datos del centro
                    c.nombre AS centro_nombre,

                    -- Datos del profesor que confirmó
                    pp.nombre AS profesor_nombre,
                    pp.apellido AS profesor_apellido,

                    -- Datos de la cuota
                    cu.periodo_mes,
                    cu.periodo_anio,
                    cu.fecha_vencimiento,
                    cu.estado AS cuota_estado,

                    -- Datos del examen
                    ep.titulo AS examen_titulo,
                    ep.fecha_examen

                FROM pago p

                INNER JOIN alumno a
                    ON p.alumno_id = a.id

                INNER JOIN persona pa
                    ON a.persona_id = pa.id

                INNER JOIN centro c
                    ON p.centro_id = c.id

                LEFT JOIN profesor pr
                    ON p.profesor_id = pr.id

                LEFT JOIN persona pp
                    ON pr.persona_id = pp.id

                LEFT JOIN cuota cu
                    ON p.cuota_id = cu.id

                LEFT JOIN inscripcion_examen ie
                    ON p.inscripcion_examen_id = ie.id

                LEFT JOIN examen_programado ep
                    ON ie.examen_id = ep.id

                ORDER BY p.fecha_registro DESC
            """

            cursor.execute(query)

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # OBTENER PAGO POR ID
    # =========================================================

    @staticmethod
    def obtener_por_id(pago_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    p.id AS pago_id,

                    p.alumno_id,
                    p.cuota_id,
                    p.inscripcion_examen_id,

                    p.profesor_id,
                    p.centro_id,

                    p.tipo_concepto,
                    p.descripcion,
                    p.monto,
                    p.metodo_pago,
                    p.comprobante_url,

                    p.estado,
                    p.fecha_registro,
                    p.fecha_confirmacion,

                    -- Alumno
                    pa.nombre AS alumno_nombre,
                    pa.apellido AS alumno_apellido,

                    -- Centro
                    c.nombre AS centro_nombre,

                    -- Profesor que confirmó
                    pp.nombre AS profesor_nombre,
                    pp.apellido AS profesor_apellido,

                    -- Cuota
                    cu.periodo_mes,
                    cu.periodo_anio,
                    cu.monto AS cuota_monto,
                    cu.fecha_vencimiento,
                    cu.estado AS cuota_estado,

                    -- Examen
                    ep.titulo AS examen_titulo,
                    ep.fecha_examen,
                    ep.monto AS examen_monto

                FROM pago p

                INNER JOIN alumno a
                    ON p.alumno_id = a.id

                INNER JOIN persona pa
                    ON a.persona_id = pa.id

                INNER JOIN centro c
                    ON p.centro_id = c.id

                LEFT JOIN profesor pr
                    ON p.profesor_id = pr.id

                LEFT JOIN persona pp
                    ON pr.persona_id = pp.id

                LEFT JOIN cuota cu
                    ON p.cuota_id = cu.id

                LEFT JOIN inscripcion_examen ie
                    ON p.inscripcion_examen_id = ie.id

                LEFT JOIN examen_programado ep
                    ON ie.examen_id = ep.id

                WHERE p.id = %s

                LIMIT 1
            """

            cursor.execute(query, (pago_id,))

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # LISTAR PAGOS DE UN ALUMNO
    # =========================================================

    @staticmethod
    def listar_por_alumno(alumno_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    p.id AS pago_id,

                    p.alumno_id,
                    p.cuota_id,
                    p.inscripcion_examen_id,

                    p.profesor_id,
                    p.centro_id,

                    p.tipo_concepto,
                    p.descripcion,
                    p.monto,
                    p.metodo_pago,
                    p.comprobante_url,

                    p.estado,
                    p.fecha_registro,
                    p.fecha_confirmacion,

                    c.nombre AS centro_nombre,

                    cu.periodo_mes,
                    cu.periodo_anio,
                    cu.fecha_vencimiento,
                    cu.estado AS cuota_estado,

                    ep.titulo AS examen_titulo,
                    ep.fecha_examen

                FROM pago p

                INNER JOIN centro c
                    ON p.centro_id = c.id

                LEFT JOIN cuota cu
                    ON p.cuota_id = cu.id

                LEFT JOIN inscripcion_examen ie
                    ON p.inscripcion_examen_id = ie.id

                LEFT JOIN examen_programado ep
                    ON ie.examen_id = ep.id

                WHERE p.alumno_id = %s

                ORDER BY p.fecha_registro DESC
            """

            cursor.execute(query, (alumno_id,))

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # LISTAR PAGOS PENDIENTES
    # =========================================================

    @staticmethod
    def listar_pendientes():

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    p.id AS pago_id,

                    p.alumno_id,
                    p.cuota_id,
                    p.inscripcion_examen_id,

                    p.profesor_id,
                    p.centro_id,

                    p.tipo_concepto,
                    p.descripcion,
                    p.monto,
                    p.metodo_pago,
                    p.comprobante_url,

                    p.estado,
                    p.fecha_registro,
                    p.fecha_confirmacion,

                    pa.nombre AS alumno_nombre,
                    pa.apellido AS alumno_apellido,

                    c.nombre AS centro_nombre,

                    cu.periodo_mes,
                    cu.periodo_anio,
                    cu.fecha_vencimiento,

                    ep.titulo AS examen_titulo,
                    ep.fecha_examen

                FROM pago p

                INNER JOIN alumno a
                    ON p.alumno_id = a.id

                INNER JOIN persona pa
                    ON a.persona_id = pa.id

                INNER JOIN centro c
                    ON p.centro_id = c.id

                LEFT JOIN cuota cu
                    ON p.cuota_id = cu.id

                LEFT JOIN inscripcion_examen ie
                    ON p.inscripcion_examen_id = ie.id

                LEFT JOIN examen_programado ep
                    ON ie.examen_id = ep.id

                WHERE p.estado = 'PENDIENTE'

                ORDER BY p.fecha_registro ASC
            """

            cursor.execute(query)

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # CREAR PAGO
    # =========================================================

    @staticmethod
    def crear(datos):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            query = """
                INSERT INTO pago (
                    alumno_id,
                    cuota_id,
                    inscripcion_examen_id,
                    profesor_id,
                    centro_id,
                    tipo_concepto,
                    descripcion,
                    monto,
                    metodo_pago,
                    comprobante_url,
                    estado
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    'PENDIENTE'
                )
            """

            cursor.execute(
                query,
                (
                    datos["alumno_id"],
                    datos.get("cuota_id"),
                    datos.get("inscripcion_examen_id"),
                    datos.get("profesor_id"),
                    datos["centro_id"],
                    datos["tipo_concepto"],
                    datos.get("descripcion"),
                    datos["monto"],
                    datos["metodo_pago"],
                    datos.get("comprobante_url")
                )
            )

            pago_id = cursor.lastrowid

            conn.commit()

            return pago_id

        except Exception:

            conn.rollback()
            raise

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # CONFIRMAR PAGO
    # =========================================================

    @staticmethod
    def confirmar(pago_id, profesor_id=None):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            # ---------------------------------------------
            # Verificar que exista el pago
            # ---------------------------------------------

            cursor.execute(
                """
                SELECT
                    id,
                    cuota_id,
                    estado
                FROM pago
                WHERE id = %s
                LIMIT 1
                """,
                (pago_id,)
            )

            pago = cursor.fetchone()

            if not pago:
                return False

            cuota_id = pago[1]
            estado_actual = pago[2]

            # ---------------------------------------------
            # Solo se puede confirmar un pago pendiente
            # ---------------------------------------------

            if estado_actual != "PENDIENTE":
                return False

            # ---------------------------------------------
            # Confirmar pago
            # ---------------------------------------------

            cursor.execute(
                """
                UPDATE pago
                SET
                    estado = 'CONFIRMADO',
                    profesor_id = %s,
                    fecha_confirmacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    profesor_id,
                    pago_id
                )
            )

            # ---------------------------------------------
            # Si pertenece a una cuota,
            # marcar la cuota como PAGADA
            # ---------------------------------------------

            if cuota_id:

                cursor.execute(
                    """
                    UPDATE cuota
                    SET estado = 'PAGADA'
                    WHERE id = %s
                    """,
                    (cuota_id,)
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
    # RECHAZAR PAGO
    # =========================================================

    @staticmethod
    def rechazar(pago_id, profesor_id=None):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT
                    id,
                    estado
                FROM pago
                WHERE id = %s
                LIMIT 1
                """,
                (pago_id,)
            )

            pago = cursor.fetchone()

            if not pago:
                return False

            estado_actual = pago[1]

            # ---------------------------------------------
            # Solo se puede rechazar un pago pendiente
            # ---------------------------------------------

            if estado_actual != "PENDIENTE":
                return False

            # ---------------------------------------------
            # Rechazar pago
            # ---------------------------------------------

            cursor.execute(
                """
                UPDATE pago
                SET
                    estado = 'RECHAZADO',
                    profesor_id = %s,
                    fecha_confirmacion = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    profesor_id,
                    pago_id
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