#agregado docs
from database.connection import get_db_connection


class ChatRepository:

    # =========================================================
    # LISTAR MENSAJES DE UN CENTRO
    # =========================================================

    @staticmethod
    def listar_por_centro(centro_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    mc.id AS mensaje_id,
                    mc.centro_id,
                    mc.emisor_persona_id,
                    mc.mensaje,
                    mc.fecha_hora,

                    p.nombre AS emisor_nombre,
                    p.apellido AS emisor_apellido,
                    p.avatar AS emisor_avatar,

                    u.usuario,
                    u.rol

                FROM mensaje_chat mc

                INNER JOIN persona p
                    ON mc.emisor_persona_id = p.id

                LEFT JOIN usuario u
                    ON u.persona_id = p.id

                WHERE mc.centro_id = %s

                ORDER BY mc.fecha_hora ASC
            """

            cursor.execute(
                query,
                (centro_id,)
            )

            return cursor.fetchall()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # OBTENER MENSAJE POR ID
    # =========================================================

    @staticmethod
    def obtener_por_id(mensaje_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    mc.id AS mensaje_id,
                    mc.centro_id,
                    mc.emisor_persona_id,
                    mc.mensaje,
                    mc.fecha_hora,

                    p.nombre AS emisor_nombre,
                    p.apellido AS emisor_apellido,
                    p.avatar AS emisor_avatar,

                    u.usuario,
                    u.rol

                FROM mensaje_chat mc

                INNER JOIN persona p
                    ON mc.emisor_persona_id = p.id

                LEFT JOIN usuario u
                    ON u.persona_id = p.id

                WHERE mc.id = %s

                LIMIT 1
            """

            cursor.execute(
                query,
                (mensaje_id,)
            )

            return cursor.fetchone()

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # CREAR MENSAJE
    # =========================================================

    @staticmethod
    def crear(datos):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            query = """
                INSERT INTO mensaje_chat (
                    centro_id,
                    emisor_persona_id,
                    mensaje
                )
                VALUES (
                    %s,
                    %s,
                    %s
                )
            """

            cursor.execute(
                query,
                (
                    datos["centro_id"],
                    datos["emisor_persona_id"],
                    datos["mensaje"]
                )
            )

            mensaje_id = cursor.lastrowid

            conn.commit()

            return mensaje_id

        except Exception:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()


    # =========================================================
    # ELIMINAR MENSAJE
    # =========================================================

    @staticmethod
    def eliminar(mensaje_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                DELETE FROM mensaje_chat
                WHERE id = %s
                """,
                (mensaje_id,)
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

