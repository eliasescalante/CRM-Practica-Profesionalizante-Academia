# BACKEND:

## 🛠️ Tech Stack (Backend & Base de Datos)

* **Lenguaje:** Python 3.x
* **Framework Web:** Flask
* **Base de Datos:** MySQL
* **Entorno de Servidor Local:** XAMPP (Apache + MySQL / phpMyAdmin)
* **Conector BD:** `mysql-connector-python`

---

# FRONTEND:

* **HTML5 + CSS3 + JS (Vanilla)**
* **Sitio Placeholder / Demo:** https://eliasescalante.github.io/CRM-Practica-Profesionalizante-Academia/

---

# Modelo DB de CRM

### Conexiones de Foreign Keys (Relaciones)

#### Entidades Base y Accesos
* **`persona` $\rightarrow$ `usuario`**
  * `persona.id` (PK) $\longrightarrow$ `usuario.persona_id` (FK, UNIQUE) `[1 : 1]`
* **`usuario` $\rightarrow$ `profesor`**
  * `usuario.persona_id` $\longrightarrow$ `profesor.persona_id` (FK, UNIQUE) `[1 : 0..1]`
* **`usuario` $\rightarrow$ `alumno`**
  * `usuario.persona_id` $\longrightarrow$ `alumno.persona_id` (FK, UNIQUE) `[1 : 0..1]`

#### Estructura Operativa y Sedes
* **`profesor` $\leftrightarrow$ `centro` (Relación M:N via `profesor_centro`)**
  * `profesor.id` (PK) $\longrightarrow$ `profesor_centro.profesor_id` (FK) `[1 : N]`
  * `centro.id` (PK) $\longrightarrow$ `profesor_centro.centro_id` (FK) `[1 : N]`
* **`centro` $\rightarrow$ `alumno`**
  * `centro.id` (PK) $\longrightarrow$ `alumno.centro_id` (FK) `[1 : N]`
* **`profesor` $\rightarrow$ `alumno`**
  * `profesor.id` (PK) $\longrightarrow$ `alumno.profesor_id` (FK) `[1 : N]`

#### Asistencia, Graduaciones y Exámenes
* **`alumno` $\rightarrow$ `asistencia`**
  * `alumno.id` (PK) $\longrightarrow$ `asistencia.alumno_id` (FK) `[1 : N]`
* **`centro` $\rightarrow$ `asistencia`**
  * `centro.id` (PK) $\longrightarrow$ `asistencia.centro_id` (FK) `[1 : N]`
* **`alumno` $\rightarrow$ `graduacion`**
  * `alumno.id` (PK) $\longrightarrow$ `graduacion.alumno_id` (FK) `[1 : N]`
* **`centro` $\rightarrow$ `graduacion`**
  * `centro.id` (PK) $\longrightarrow$ `graduacion.centro_id` (FK) `[1 : N]`
* **`centro` $\rightarrow$ `examen_programado`**
  * `centro.id` (PK) $\longrightarrow$ `examen_programado.centro_id` (FK) `[1 : N]`
* **`profesor` $\rightarrow$ `examen_programado`**
  * `profesor.id` (PK) $\longrightarrow$ `examen_programado.profesor_id` (FK) `[1 : N]`
* **`examen_programado` $\rightarrow$ `inscripcion_examen`**
  * `examen_programado.id` (PK) $\longrightarrow$ `inscripcion_examen.examen_id` (FK) `[1 : N]`
* **`alumno` $\rightarrow$ `inscripcion_examen`**
  * `alumno.id` (PK) $\longrightarrow$ `inscripcion_examen.alumno_id` (FK) `[1 : N]`

#### Cobros, Cuotas y Transacciones
* **`alumno` $\rightarrow$ `cuota`**
  * `alumno.id` (PK) $\longrightarrow$ `cuota.alumno_id` (FK) `[1 : N]`
* **`centro` $\rightarrow$ `cuota`**
  * `centro.id` (PK) $\longrightarrow$ `cuota.centro_id` (FK) `[1 : N]`
* **`alumno` $\rightarrow$ `pago`**
  * `alumno.id` (PK) $\longrightarrow$ `pago.alumno_id` (FK) `[1 : N]`
* **`centro` $\rightarrow$ `pago`**
  * `centro.id` (PK) $\longrightarrow$ `pago.centro_id` (FK) `[1 : N]`
* **`cuota` $\rightarrow$ `pago`**
  * `cuota.id` (PK) $\longrightarrow$ `pago.cuota_id` (FK) `[0..1 : 1]`
* **`inscripcion_examen` $\rightarrow$ `pago`**
  * `inscripcion_examen.id` (PK) $\longrightarrow$ `pago.inscripcion_examen_id` (FK) `[0..1 : 1]`
* **`profesor` $\rightarrow$ `pago`**
  * `profesor.id` (PK) $\longrightarrow$ `pago.profesor_id` (FK) `[0..1 : N]`

#### Comunicación y Novedades
* **`usuario` $\rightarrow$ `noticia`**
  * `usuario.id` (PK) $\longrightarrow$ `noticia.autor_usuario_id` (FK) `[1 : N]`
* **`centro` $\rightarrow$ `noticia`**
  * `centro.id` (PK) $\longrightarrow$ `noticia.centro_id` (FK, NULLABLE) `[0..1 : N]` *(NULL = Noticia General)*
* **`centro` $\rightarrow$ `mensaje_chat`**
  * `centro.id` (PK) $\longrightarrow$ `mensaje_chat.centro_id` (FK) `[1 : N]`
* **`persona` $\rightarrow$ `mensaje_chat`**
  * `persona.id` (PK) $\longrightarrow$ `mensaje_chat.emisor_persona_id` (FK) `[1 : N]`

---

#### Diagrama de Entidad-Relaciones (Mermaid)

```mermaid
erDiagram
    PERSONA ||--|| USUARIO : "es"
    USUARIO ||--o| PROFESOR : "rol profesor"
    USUARIO ||--o| ALUMNO : "rol alumno"

    CENTRO ||--o{ PROFESOR_CENTRO : "tiene"
    PROFESOR ||--o{ PROFESOR_CENTRO : "enseña en"

    CENTRO ||--o{ ALUMNO : "pertenece a"
    PROFESOR ||--o{ ALUMNO : "tiene a cargo"

    CENTRO ||--o{ NOTICIA : "publica (específico)"
    USUARIO ||--o{ NOTICIA : "crea"

    CENTRO ||--o{ MENSAJE_CHAT : "canal de"
    PERSONA ||--o{ MENSAJE_CHAT : "envía"

    ALUMNO ||--o{ ASISTENCIA : "registra"
    CENTRO ||--o{ ASISTENCIA : "en centro"

    ALUMNO ||--o{ GRADUACION : "obtiene"
    CENTRO ||--o{ GRADUACION : "en centro"

    ALUMNO ||--o{ CUOTA : "genera"
    CENTRO ||--o{ CUOTA : "pertenece a"

    CENTRO ||--o{ EXAMEN_PROGRAMADO : "organiza"
    PROFESOR ||--o{ EXAMEN_PROGRAMADO : "evalúa"

    EXAMEN_PROGRAMADO ||--o{ INSCRIPCION_EXAMEN : "tiene"
    ALUMNO ||--o{ INSCRIPCION_EXAMEN : "se inscribe"

    ALUMNO ||--o{ PAGO : "realiza"
    CENTRO ||--o{ PAGO : "recibe"
    CUOTA ||--o| PAGO : "asociado a"
    INSCRIPCION_EXAMEN ||--o| PAGO : "asociado a"
    PROFESOR ||--o| PAGO : "referenciado en"

    PERSONA {
        BIGINT id PK
        VARCHAR dni UK
        VARCHAR nombre
        VARCHAR apellido
        VARCHAR email UK
        VARCHAR telefono
        DATE fecha_nacimiento
        VARCHAR contacto_emergencia
        VARCHAR avatar
        BOOLEAN activo
    }

    USUARIO {
        BIGINT id PK
        BIGINT persona_id FK, UK
        VARCHAR usuario UK
        VARCHAR contrasenia
        ENUM rol "ADMIN, PROFESOR, ALUMNO"
        BOOLEAN activo
    }

    PROFESOR {
        BIGINT id PK
        BIGINT persona_id FK, UK
        DATE fecha_alta
        BOOLEAN activo
    }

    ALUMNO {
        BIGINT id PK
        BIGINT persona_id FK, UK
        INT centro_id FK
        BIGINT profesor_id FK
        DATE fecha_de_inicio
        ENUM estado "ACTIVO, PAUSADO, INACTIVO"
        DATE fecha_alta
    }

    CENTRO {
        INT id PK
        VARCHAR nombre UK
        VARCHAR direccion
        VARCHAR telefono
        BOOLEAN activo
        VARCHAR captura
    }

    PROFESOR_CENTRO {
        BIGINT profesor_id PK, FK
        INT centro_id PK, FK
    }

    GRADUACION {
        BIGINT id PK
        BIGINT alumno_id FK
        INT centro_id FK
        VARCHAR grado
        DATE fecha
    }

    ASISTENCIA {
        BIGINT id PK
        BIGINT alumno_id FK
        INT centro_id FK
        DATETIME fecha
        BOOLEAN presente
        VARCHAR observacion
    }

    CUOTA {
        BIGINT id PK
        BIGINT alumno_id FK
        INT centro_id FK
        TINYINT periodo_mes
        INT periodo_anio
        DECIMAL monto
        DATE fecha_vencimiento
        ENUM estado "PENDIENTE, PAGADA, VENCIDA"
        DATETIME fecha_generacion
    }

    EXAMEN_PROGRAMADO {
        BIGINT id PK
        INT centro_id FK
        BIGINT profesor_id FK
        VARCHAR titulo
        DATETIME fecha_examen
        DECIMAL monto
        BOOLEAN activo
    }

    INSCRIPCION_EXAMEN {
        BIGINT id PK
        BIGINT examen_id FK
        BIGINT alumno_id FK
    }

    PAGO {
        BIGINT id PK
        BIGINT alumno_id FK
        BIGINT cuota_id FK
        BIGINT inscripcion_examen_id FK
        BIGINT profesor_id FK
        INT centro_id FK
        ENUM tipo_concepto "CUOTA, EXAMEN, MATRICULA, INSUMO, OTRO"
        VARCHAR descripcion
        DECIMAL monto
        ENUM metodo_pago "EFECTIVO, TRANSFERENCIA"
        VARCHAR comprobante_url
        ENUM estado "PENDIENTE, CONFIRMADO, RECHAZADO"
        DATETIME fecha_registro
        DATETIME fecha_confirmacion
    }

    NOTICIA {
        BIGINT id PK
        BIGINT autor_usuario_id FK
        INT centro_id FK
        VARCHAR titulo
        TEXT contenido
        VARCHAR imagen_url
        DATETIME fecha_publicacion
        BOOLEAN activa
    }

    MENSAJE_CHAT {
        BIGINT id PK
        INT centro_id FK
        BIGINT emisor_persona_id FK
        TEXT mensaje
        DATETIME fecha_hora
    }