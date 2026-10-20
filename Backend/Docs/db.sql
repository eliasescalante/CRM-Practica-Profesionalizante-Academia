-- =============================================================
-- BASE DE DATOS MEJORADA: CRM ARTES MARCIALES
-- =============================================================
CREATE DATABASE IF NOT EXISTS crm_artes_marciales 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE crm_artes_marciales;

-- 1. CENTRO DE ENTRENAMIENTO
CREATE TABLE IF NOT EXISTS centro (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    direccion VARCHAR(200),
    telefono VARCHAR(50),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    captura VARCHAR(255) NULL
) ENGINE=InnoDB;

-- 2. PERSONA (Datos compartidos por cualquier rol)
CREATE TABLE IF NOT EXISTS persona (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    dni VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    telefono VARCHAR(50),
    fecha_nacimiento DATE,
    contacto_emergencia VARCHAR(150),
    fecha_de_inicio DATE DEFAULT (CURRENT_DATE),
    avatar VARCHAR(255) NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- 3. USUARIO (Credenciales y Accesos)
CREATE TABLE IF NOT EXISTS usuario (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    persona_id BIGINT NOT NULL UNIQUE,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    contrasenia VARCHAR(255) NOT NULL,
    rol ENUM('ADMIN', 'PROFESOR', 'ALUMNO') NOT NULL DEFAULT 'ALUMNO',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_usuario_persona FOREIGN KEY (persona_id) 
        REFERENCES persona(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 4. PROFESOR
CREATE TABLE IF NOT EXISTS profesor (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    persona_id BIGINT NOT NULL UNIQUE,
    fecha_alta DATE NOT NULL DEFAULT (CURRENT_DATE),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_profesor_persona FOREIGN KEY (persona_id) 
        REFERENCES persona(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 4b. PROFESOR_CENTRO (Permite que un profesor dé clases en múltiples centros)
CREATE TABLE IF NOT EXISTS profesor_centro (
    profesor_id BIGINT NOT NULL,
    centro_id INT NOT NULL,
    PRIMARY KEY (profesor_id, centro_id),
    CONSTRAINT fk_profe_centro_profesor FOREIGN KEY (profesor_id) 
        REFERENCES profesor(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_profe_centro_centro FOREIGN KEY (centro_id) 
        REFERENCES centro(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 5. ALUMNO
CREATE TABLE IF NOT EXISTS alumno (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    persona_id BIGINT NOT NULL UNIQUE,
    centro_id INT NOT NULL,
    profesor_id BIGINT NOT NULL,
    fecha_alta DATE NOT NULL DEFAULT (CURRENT_DATE),
    estado ENUM('ACTIVO', 'PAUSADO', 'INACTIVO') NOT NULL DEFAULT 'ACTIVO',
    CONSTRAINT fk_alumno_persona FOREIGN KEY (persona_id) 
        REFERENCES persona(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_alumno_centro FOREIGN KEY (centro_id) 
        REFERENCES centro(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_alumno_profesor FOREIGN KEY (profesor_id) 
        REFERENCES profesor(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 6. GRADUACIÓN / CINTURONES
CREATE TABLE IF NOT EXISTS graduacion (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    alumno_id BIGINT NOT NULL,
    centro_id INT NOT NULL,
    grado VARCHAR(50) NOT NULL,
    fecha DATE NOT NULL DEFAULT (CURRENT_DATE),
    CONSTRAINT fk_graduacion_alumno FOREIGN KEY (alumno_id) 
        REFERENCES alumno(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_graduacion_centro FOREIGN KEY (centro_id) 
        REFERENCES centro(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 7. CONTROL DE ASISTENCIAS (PRESENTISMOS)
CREATE TABLE IF NOT EXISTS asistencia (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    alumno_id BIGINT NOT NULL,
    centro_id INT NOT NULL,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    presente BOOLEAN NOT NULL DEFAULT TRUE,
    observacion VARCHAR(255) NULL,
    CONSTRAINT fk_asistencia_alumno FOREIGN KEY (alumno_id) 
        REFERENCES alumno(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_asistencia_centro FOREIGN KEY (centro_id) 
        REFERENCES centro(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 8. GESTIÓN DE EXÁMENES
CREATE TABLE IF NOT EXISTS examen_programado (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    centro_id INT NOT NULL,
    profesor_id BIGINT NOT NULL,
    titulo VARCHAR(100) NOT NULL,
    fecha_examen DATETIME NOT NULL,
    monto DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_examen_centro FOREIGN KEY (centro_id) 
        REFERENCES centro(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_examen_profesor FOREIGN KEY (profesor_id) 
        REFERENCES profesor(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS inscripcion_examen (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    examen_id BIGINT NOT NULL,
    alumno_id BIGINT NOT NULL,
    estado_pago ENUM('PENDIENTE', 'CONFIRMADO') NOT NULL DEFAULT 'PENDIENTE',
    CONSTRAINT fk_insc_examen FOREIGN KEY (examen_id) 
        REFERENCES examen_programado(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_insc_alumno FOREIGN KEY (alumno_id) 
        REFERENCES alumno(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 9. GESTIÓN DE PAGOS Y CONFIRMACIONES
CREATE TABLE IF NOT EXISTS pago (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    alumno_id BIGINT NOT NULL,
    profesor_id BIGINT NULL, -- Nullable por si valida un Admin
    centro_id INT NOT NULL,
    tipo_concepto ENUM('CUOTA', 'EXAMEN', 'MATRICULA', 'INSUMO', 'OTRO') NOT NULL DEFAULT 'CUOTA',
    descripcion VARCHAR(150) NULL,
    monto DECIMAL(10, 2) NOT NULL,
    metodo_pago ENUM('EFECTIVO', 'TRANSFERENCIA') NOT NULL DEFAULT 'EFECTIVO',
    periodo_mes TINYINT NULL CHECK (periodo_mes BETWEEN 1 AND 12),
    periodo_anio INT NULL,
    comprobante_url VARCHAR(255) NULL,
    estado ENUM('PENDIENTE', 'CONFIRMADO', 'RECHAZADO') NOT NULL DEFAULT 'PENDIENTE',
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_confirmacion DATETIME NULL,
    CONSTRAINT fk_pago_alumno FOREIGN KEY (alumno_id) 
        REFERENCES alumno(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_pago_profesor FOREIGN KEY (profesor_id) 
        REFERENCES profesor(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_pago_centro FOREIGN KEY (centro_id) 
        REFERENCES centro(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 10. PUBLICACIÓN DE NOTICIAS (DASHBOARD INICIAL)
CREATE TABLE IF NOT EXISTS noticia (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    autor_persona_id BIGINT NOT NULL,
    centro_id INT NULL, -- NULL significa que es Noticia General (todos los centros la ven)
    titulo VARCHAR(150) NOT NULL,
    contenido TEXT NOT NULL,
    imagen_url VARCHAR(255) NULL,
    fecha_publicacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_noticia_autor FOREIGN KEY (autor_persona_id) 
        REFERENCES persona(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_noticia_centro FOREIGN KEY (centro_id) 
        REFERENCES centro(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 11. CHAT DE CENTRO / SALA DE COMUNICACIÓN
CREATE TABLE IF NOT EXISTS mensaje_chat (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    centro_id INT NOT NULL,
    emisor_persona_id BIGINT NOT NULL,
    mensaje TEXT NOT NULL,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_chat_centro FOREIGN KEY (centro_id) 
        REFERENCES centro(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_chat_emisor FOREIGN KEY (emisor_persona_id) 
        REFERENCES persona(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- =============================================================
-- ÍNDICES DE RENDIMIENTO
-- =============================================================
CREATE INDEX idx_persona_dni ON persona(dni);
CREATE INDEX idx_alumno_profesor ON alumno(profesor_id);
CREATE INDEX idx_alumno_centro ON alumno(centro_id);
CREATE INDEX idx_pago_alumno ON pago(alumno_id);
CREATE INDEX idx_pago_estado ON pago(estado);
CREATE INDEX idx_asistencia_alumno ON asistencia(alumno_id);
CREATE INDEX idx_noticia_activa ON noticia(activa, centro_id);
CREATE INDEX idx_chat_centro_fecha ON mensaje_chat(centro_id, fecha_hora);