# BACKEND:

## 🛠️ Tech Stack (Backend & Base de Datos)

* **Lenguaje:** Python 3.x
* **Framework Web:** Flask
* **Base de Datos:** MySQL
* **Entorno de Servidor Local:** XAMPP (Apache + MySQL / phpMyAdmin)
* **Conector BD:** `mysql-connector-python`

---

# FRONTEND:

## Landing pública — Tien Long Hu / Shen Xin Ling

Landing page pública de la academia, de una sola página, hecha con HTML, CSS y JavaScript puro. Diseño inspirado en el PDF de referencia de Tien Long Hu / Shen Xin Ling. **No consume la API del backend todavía**: es solo presentación.

### Estructura de carpetas

```
FrontEnd/
├── index.html      # estructura y contenido de todas las secciones
├── css/
│   └── styles.css  # paleta, tipografía, layout responsive y animaciones
├── js/
│   └── script.js   # menú móvil, scroll suave, animaciones, barra de lectura, parallax y año del footer
└── assets/         # imágenes del PDF de referencia y favicon.svg con la marca
```

### Cómo ejecutarla

1. Abrí `FrontEnd/index.html` en tu navegador. Para desarrollo, podés usar la extensión **Live Server** de VS Code.
2. No requiere Node.js, npm, frameworks ni backend.

### Mockup del portal del alumno

En la raíz del repositorio hay un `index.html` aparte: es el **mockup del Portal del Alumno** (HTML + Tailwind por CDN), usado como sitio placeholder. Se publica en GitHub Pages: <https://eliasescalante.github.io/CRM-Practica-Profesionalizante-Academia/>. No forma parte de la landing de `FrontEnd/`.

### Codificación de los archivos

Los tres archivos de código (`FrontEnd/index.html`, `FrontEnd/css/styles.css`, `FrontEnd/js/script.js`) se guardan en **UTF-8 con BOM** (`EF BB BF`). El BOM es lo que permite que el Bloc de notas y el VS Code de Windows detecten el UTF-8 y muestren bien los acentos, las comillas tipográficas y las flechas (`★`, `↗`, `·`). Si los editás con una herramienta que los vuelva a guardar sin BOM, la página vuelve a mostrar `Ã©`, `â˜…` o `â†—` en vez de `é`, `★` y `↗`.

Si tenés que editar a mano, mantené el BOM. Para revisarlo rápido:

```powershell
Format-Hex -Path FrontEnd\index.html -Count 3   # debe devolver EF BB BF
```

### Imágenes de los testimonios

Las 3 fotos de los testimonios (`FrontEnd/assets/testimonial-1.jpg`, `FrontEnd/assets/testimonial-2.jpg` y `FrontEnd/assets/testimonial-3.jpg`) se extrajeron de la página 4 del PDF de referencia. `testimonial-3.jpg` no estaba en el paquete original de la plantilla: se recuperó del PDF.

## Paleta

El acento de la marca es **verde brillante** (`--yellow: #3ee87a`), con `--green-ink: #15803d` para textos sobre fondos claros y `--green-deep: #0b3d20` para detalles sobre verde. El rojo (`--red`) se usa solo en detalles puntuales. Si querés cambiar el acento, modificá esas variables en `:root` dentro de `FrontEnd/css/styles.css`.

## Responsive

La página se adapta a celulares, tablets, notebooks y distintos monitores:

- `≥1800px` y `≥2300px`: monitores 2K y ultrawide (ancho máximo ampliado, tipografías y fotos más grandes).
- `1500–1799px`: monitores de 1920.
- `1101–1440px`: notebooks de 1366 y 1440.
- Alto de pantalla ≤ 760px: notebooks apaisadas (hero más compacto).
- `651–900px`: tablets verticales y grandes (grillas a 2 columnas).
- `481–650px`: celulares grandes.
- `≤360px`: celulares chicos.

## Dinamismo (JavaScript)

- **Transición fuerte por sección**: cada `<section>` entra con desplazamiento, escala y desenfoque (las pares desde la derecha, las impares desde la izquierda) más un barrido de luz. **Se repite cada vez** que la sección vuelve a entrar en pantalla.
- **Contenido en cascada**: kicker, regla, títulos y tarjetas aparecen escalonados al entrar cada sección.
- Barra de progreso de lectura y header que se compacta al scrollear.
- Parallax suave del hero (solo desktop).
- Efecto de luz que sigue al cursor en tarjetas y testimonios.
- Las cards de testimonios tienen **foto de la persona** en la parte superior (mismo tratamiento que las cards de disciplinas: degradado inferior, saturación baja y zoom suave al hacer hover).
- Scroll suave con compensación del header y enlace “Saltar al contenido” accesible.

### Cómo se comportan las animaciones

Las transiciones de sección se **repiten cada vez** que una sección entra o sale de pantalla (no solo la primera vez). Para lograrlo, el JS resetea el estado de la sección cuando ya salió del viewport.

El script tiene dos constantes al comienzo:

```js
const FORCE_ANIMATIONS = true;          // true = animaciones siempre activas
const ACCESSIBILITY_REDUCED_MOTION = false; // true = respetar "reducir movimiento" del sistema
```

- `FORCE_ANIMATIONS = true` (valor actual) mantiene siempre las animaciones de sección.
- Poné `ACCESSIBILITY_REDUCED_MOTION = true` si querés que la preferencia de accesibilidad del sistema desactive todo.

### Video de fondo (fuego)

Las secciones `.intro` y `.experiences` tienen `FrontEnd/assets/fire.mp4` de fondo, con un degradado oscuro suave encima para que el texto se lea. El video:

- Se descarga **solo cuando entra en pantalla** (`preload="none"` + `data-src`), para no bajar 35 MB al abrir la página.
- Se pausa al salir de vista y no se carga en móviles (< 651px).
- Se reproduce igual aunque el sistema tenga "reducir movimiento" activado (es decorativo y se pidió explícitamente).

## Accesibilidad y SEO

- Enlace “Saltar al contenido principal” visible con teclado.
- Foco visible en enlaces y botones; navegación operable solo con teclado (menú móvil se cierra con Escape).
- Imágenes con `alt` descriptivo, `width`, `height`, `loading="lazy"` y `decoding="async"` (el hero se precarga con `fetchpriority="high"`).
- Se respeta `prefers-reduced-motion`: si el sistema pide menos movimiento, no se animan las secciones.
- Metadatos Open Graph y Twitter Card para compartir en redes.
- Datos estructurados JSON-LD (`SportsActivityLocation`).

## Botón Login

El botón del header dice **Login** y apunta a `#login`, que por ahora **no existe** (es una página de presentación). Cuando esté el acceso del CRM, reemplazá ese `href` por la URL o por el id de la sección del formulario de ingreso.

## Antes de publicar

- Confirmá el teléfono y el correo de contacto. Se conservaron los datos visibles en el PDF (`923 456 789` y `hola@unsitiogenial.es`) como referencias editables; podrían ser datos de ejemplo.
- Confirmá que los testimonios y nombres pueden publicarse (la nota interna se quitó de la página; queda pendiente la autorización).
- Las tipografías se cargan desde Google Fonts; si no hay conexión, se usan fuentes alternativas.
- Las imágenes se usan como JPG sin optimizar ni formatos modernos (WebP/AVIF); conviene comprimirlas antes de publicar.
- `FrontEnd/assets/fire.mp4` pesa 35 MB: se carga de forma diferida, pero Git lo guarda completo en el historial. Conviene optimizarlo, convertirlo a WebM o excluirlo del repositorio.

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
