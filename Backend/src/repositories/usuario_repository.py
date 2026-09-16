from database.connection import get_db_connection


class UsuarioRepository:

    @staticmethod
    def obtener_por_usuario_o_email(identificador):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                u.id AS usuario_id,
                u.usuario,
                u.contrasenia,
                u.rol,
                u.activo AS usuario_activo,

                p.id AS persona_id,
                p.nombre,
                p.apellido,
                p.email,
                p.avatar,
                p.activo AS persona_activa

            FROM usuario u

            INNER JOIN persona p
                ON u.persona_id = p.id

            WHERE u.usuario = %s
               OR p.email = %s

            LIMIT 1;
        """

        cursor.execute(query, (identificador, identificador))

        usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        return usuario

    @staticmethod
    def registrar_alumno(datos):

        conn = get_db_connection()
        cursor = conn.cursor()

        try:

            # -------------------------------------------------
            # 1. Crear persona
            # -------------------------------------------------

            query_persona = """
                INSERT INTO persona (
                    dni,
                    nombre,
                    apellido,
                    email,
                    telefono,
                    fecha_nacimiento,
                    contacto_emergencia
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
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
                    datos.get("contacto_emergencia")
                )
            )

            persona_id = cursor.lastrowid

            # -------------------------------------------------
            # 2. Crear usuario
            # -------------------------------------------------

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

            # -------------------------------------------------
            # 3. Crear alumno
            # -------------------------------------------------

            query_alumno = """
                INSERT INTO alumno (
                    persona_id,
                    centro_id,
                    profesor_id,
                    fecha_de_inicio
                )
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                query_alumno,
                (
                    persona_id,
                    datos["centro_id"],
                    datos["profesor_id"],
                    datos["fecha_inicio"]
                )
            )

            alumno_id = cursor.lastrowid

            conn.commit()

            return {
                "usuario_id": usuario_id,
                "persona_id": persona_id,
                "alumno_id": alumno_id
            }

        except Exception:


            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()