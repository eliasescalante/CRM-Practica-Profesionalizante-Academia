from database.connection import get_db_connection


class NoticiaRepository:

    # =========================================================
    # LISTAR NOTICIAS
    # =========================================================

    @staticmethod
    def listar(incluir_inactivas=False):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            query = """
                SELECT
                    n.id,
                    n.autor_usuario_id,
                    n.centro_id,
                    n.titulo,
                    n.contenido,
                    n.imagen_url,
                    n.fecha_publicacion,
                    n.activa,

                    CONCAT(p.nombre, ' ', p.apellido) AS autor,

                    c.nombre AS centro

                FROM noticia n

                INNER JOIN usuario u
                    ON n.autor_usuario_id = u.id

                INNER JOIN persona p
                    ON u.persona_id = p.id

                LEFT JOIN centro c
                    ON n.centro_id = c.id
            """

            if not incluir_inactivas:
                query += """
                    WHERE n.activa = TRUE
                """

            query += """
                ORDER BY n.fecha_publicacion DESC
            """

            cursor.execute(query)

            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # OBTENER NOTICIA POR ID
    # =========================================================

    @staticmethod
    def obtener_por_id(noticia_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            cursor.execute(
                """
                SELECT
                    n.id,
                    n.autor_usuario_id,
                    n.centro_id,
                    n.titulo,
                    n.contenido,
                    n.imagen_url,
                    n.fecha_publicacion,
                    n.activa,

                    CONCAT(p.nombre, ' ', p.apellido) AS autor,

                    c.nombre AS centro

                FROM noticia n

                INNER JOIN usuario u
                    ON n.autor_usuario_id = u.id

                INNER JOIN persona p
                    ON u.persona_id = p.id

                LEFT JOIN centro c
                    ON n.centro_id = c.id

                WHERE n.id = %s
                LIMIT 1
                """,
                (noticia_id,)
            )

            return cursor.fetchone()

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # NOTICIAS DE UN CENTRO
    # =========================================================

    @staticmethod
    def listar_por_centro(centro_id):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:

            cursor.execute(
                """
                SELECT
                    n.id,
                    n.autor_usuario_id,
                    n.centro_id,
                    n.titulo,
                    n.contenido,
                    n.imagen_url,
                    n.fecha_publicacion,
                    n.activa,

                    CONCAT(p.nombre, ' ', p.apellido) AS autor,

                    c.nombre AS centro

                FROM noticia n

                INNER JOIN usuario u
                    ON n.autor_usuario_id = u.id

                INNER JOIN persona p
                    ON u.persona_id = p.id

                LEFT JOIN centro c
                    ON n.centro_id = c.id

                WHERE
                    n.activa = TRUE
                    AND (
                        n.centro_id = %s
                        OR n.centro_id IS NULL
                    )

                ORDER BY n.fecha_publicacion DESC
                """,
                (centro_id,)
            )

            return cursor.fetchall()

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # CREAR NOTICIA
    # =========================================================

    @staticmethod
    def crear(datos):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO noticia (
                    autor_usuario_id,
                    centro_id,
                    titulo,
                    contenido,
                    imagen_url
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    datos["autor_usuario_id"],
                    datos.get("centro_id"),
                    datos["titulo"],
                    datos["contenido"],
                    datos.get("imagen_url")
                )
            )

            conn.commit()

            return cursor.lastrowid

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # ACTUALIZAR NOTICIA
    # =========================================================

    @staticmethod
    def actualizar(noticia_id, datos):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                UPDATE noticia
                SET
                    centro_id = %s,
                    titulo = %s,
                    contenido = %s,
                    imagen_url = %s
                WHERE id = %s
                """,
                (
                    datos.get("centro_id"),
                    datos["titulo"],
                    datos["contenido"],
                    datos.get("imagen_url"),
                    noticia_id
                )
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()


    # =========================================================
    # DESACTIVAR NOTICIA
    # =========================================================

    @staticmethod
    def desactivar(noticia_id):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                UPDATE noticia
                SET activa = FALSE
                WHERE id = %s
                """,
                (noticia_id,)
            )

            conn.commit()

            return cursor.rowcount > 0

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()