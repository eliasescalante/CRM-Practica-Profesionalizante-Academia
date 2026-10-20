USE crm_artes_marciales;

-- ============================================================
-- 1. MOVER fecha_de_inicio DE persona A alumno
-- ============================================================

ALTER TABLE alumno
ADD COLUMN fecha_de_inicio DATE NULL AFTER profesor_id;

-- Copiar los datos existentes desde persona
UPDATE alumno a
INNER JOIN persona p ON a.persona_id = p.id
SET a.fecha_de_inicio = p.fecha_de_inicio;

-- Una vez copiados los datos, eliminamos el campo de persona
ALTER TABLE persona
DROP COLUMN fecha_de_inicio;

-- Ahora hacemos que sea obligatorio
ALTER TABLE alumno
MODIFY COLUMN fecha_de_inicio DATE NOT NULL;


-- ============================================================
-- 2. RELACIONAR PAGO CON INSCRIPCION_EXAMEN
-- ============================================================

ALTER TABLE pago
ADD COLUMN inscripcion_examen_id BIGINT NULL AFTER alumno_id;

ALTER TABLE pago
ADD CONSTRAINT fk_pago_inscripcion_examen
FOREIGN KEY (inscripcion_examen_id)
REFERENCES inscripcion_examen(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;


-- ============================================================
-- 3. ELIMINAR estado_pago DE inscripcion_examen
-- ============================================================

ALTER TABLE inscripcion_examen
DROP COLUMN estado_pago;


-- ============================================================
-- 4. AGREGAR FECHA DE VENCIMIENTO A PAGO
-- ============================================================

ALTER TABLE pago
ADD COLUMN fecha_vencimiento DATE NULL AFTER monto;


-- ============================================================
-- 5. CAMBIAR AUTOR DE NOTICIA
-- ============================================================

-- Primero agregamos la nueva columna
ALTER TABLE noticia
ADD COLUMN autor_usuario_id BIGINT NULL AFTER id;

-- Copiamos el usuario correspondiente a cada persona
UPDATE noticia n
INNER JOIN usuario u
    ON n.autor_persona_id = u.persona_id
SET n.autor_usuario_id = u.id;

-- Creamos la FK
ALTER TABLE noticia
ADD CONSTRAINT fk_noticia_autor_usuario
FOREIGN KEY (autor_usuario_id)
REFERENCES usuario(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Eliminamos la relación anterior
ALTER TABLE noticia
DROP FOREIGN KEY fk_noticia_autor;

ALTER TABLE noticia
DROP COLUMN autor_persona_id;

-- Hacemos obligatorio el autor
ALTER TABLE noticia
MODIFY COLUMN autor_usuario_id BIGINT NOT NULL;


-- ============================================================
-- FIN DE LA MIGRACIÓN
-- ============================================================



USE crm_artes_marciales;

-- ============================================================
-- 1. CREAR TABLA CUOTA
-- ============================================================

CREATE TABLE IF NOT EXISTS cuota (

    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    alumno_id BIGINT NOT NULL,

    centro_id INT NOT NULL,

    periodo_mes TINYINT NOT NULL,

    periodo_anio INT NOT NULL,

    monto DECIMAL(10,2) NOT NULL,

    fecha_vencimiento DATE NOT NULL,

    estado ENUM(
        'PENDIENTE',
        'PAGADA',
        'VENCIDA'
    ) NOT NULL DEFAULT 'PENDIENTE',

    fecha_generacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_cuota_alumno
        FOREIGN KEY (alumno_id)
        REFERENCES alumno(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_cuota_centro
        FOREIGN KEY (centro_id)
        REFERENCES centro(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT uq_cuota_alumno_periodo
        UNIQUE (alumno_id, periodo_mes, periodo_anio)

) ENGINE=InnoDB;


-- ============================================================
-- 2. AGREGAR CUOTA_ID A PAGO
-- ============================================================

ALTER TABLE pago
ADD COLUMN cuota_id BIGINT NULL AFTER alumno_id;


-- ============================================================
-- 3. CREAR RELACIÓN PAGO → CUOTA
-- ============================================================

ALTER TABLE pago
ADD CONSTRAINT fk_pago_cuota
FOREIGN KEY (cuota_id)
REFERENCES cuota(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;


-- ============================================================
-- 4. ELIMINAR DATOS QUE AHORA PERTENECEN A CUOTA
-- ============================================================

ALTER TABLE pago
DROP COLUMN periodo_mes;

ALTER TABLE pago
DROP COLUMN periodo_anio;

ALTER TABLE pago
DROP COLUMN fecha_vencimiento;


-- ============================================================
-- 5. ÍNDICES
-- ============================================================

CREATE INDEX idx_cuota_alumno
ON cuota(alumno_id);

CREATE INDEX idx_cuota_estado
ON cuota(estado);

CREATE INDEX idx_cuota_vencimiento
ON cuota(fecha_vencimiento);

CREATE INDEX idx_pago_cuota
ON pago(cuota_id);