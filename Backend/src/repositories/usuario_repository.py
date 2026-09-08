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
            INNER JOIN persona p ON u.persona_id = p.id
            WHERE (u.usuario = %s OR p.email = %s)
            LIMIT 1;
        """
        
        cursor.execute(query, (identificador, identificador))
        usuario = cursor.fetchone()
        
        cursor.close()
        conn.close()
        return usuario