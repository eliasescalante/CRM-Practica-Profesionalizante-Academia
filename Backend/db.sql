-- =============================================================
-- BASE DE DATOS: CRM ARTES MARCIALES
-- =============================================================
CREATE DATABASE IF NOT EXISTS crm_artes_marciales 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE crm_artes_marciales;

CREATE TABLE IF NOT EXISTS centro (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    direccion VARCHAR(200),
    telefono VARCHAR(50),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    captura VARCHAR(255) NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS persona (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    dni VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    telefono VARCHAR(50),
    fecha_nacimiento DATE,
    contacto_emergencia VARCHAR(150),
    fecha_de_inicio DATE DEFAULT (CURRENT_DATE),
    avatar VARCHAR(255) NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS usuario (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    persona_id BIGINT NOT NULL UNIQUE,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    contrasenia VARCHAR(255) NOT NULL,
    rol ENUM('ADMIN', 'RECEPCION', 'PROFESOR') NOT NULL DEFAULT 'PROFESOR',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_usuario_persona FOREIGN KEY (persona_id) 
        REFERENCES persona(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS profesor (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    persona_id BIGINT NOT NULL UNIQUE,
    centro_id INT NOT NULL,
    fecha_alta DATE NOT NULL DEFAULT (CURRENT_DATE),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_profesor_persona FOREIGN KEY (persona_id) 
        REFERENCES persona(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_profesor_centro FOREIGN KEY (centro_id) 
        REFERENCES centro(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

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

CREATE TABLE IF NOT EXISTS pago (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    alumno_id BIGINT NOT NULL,
    profesor_id BIGINT NOT NULL,
    centro_id INT NOT NULL,
    tipo_concepto ENUM('CUOTA', 'EXAMEN', 'MATRICULA', 'INSUMO', 'OTRO') NOT NULL DEFAULT 'CUOTA',
    descripcion VARCHAR(150) NULL,
    monto DECIMAL(10, 2) NOT NULL,
    metodo_pago ENUM('EFECTIVO', 'TRANSFERENCIA') NOT NULL DEFAULT 'EFECTIVO',
    periodo_mes TINYINT NULL CHECK (periodo_mes BETWEEN 1 AND 12),
    fecha_de_pago DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pago_alumno FOREIGN KEY (alumno_id) 
        REFERENCES alumno(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_pago_profesor FOREIGN KEY (profesor_id) 
        REFERENCES profesor(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_pago_centro FOREIGN KEY (centro_id) 
        REFERENCES centro(id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_persona_dni ON persona(dni);
CREATE INDEX idx_alumno_profesor ON alumno(profesor_id);
CREATE INDEX idx_alumno_centro ON alumno(centro_id);
CREATE INDEX idx_pago_alumno ON pago(alumno_id);
CREATE INDEX idx_pago_profesor ON pago(profesor_id);
CREATE INDEX idx_pago_fecha ON pago(fecha_de_pago);
CREATE INDEX idx_graduacion_alumno ON graduacion(alumno_id);