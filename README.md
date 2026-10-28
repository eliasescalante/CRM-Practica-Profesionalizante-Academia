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

Landing page pública de la academia, de una sola página, hecha con HTML, CSS y JavaScript puro. Diseño inspirado en el PDF de referencia de Tien Long Hu / Shen Xin Ling. La landing es solo presentación; el **login, el registro y el panel** sí consumen la API del backend.

### Estructura de carpetas

```
FrontEnd/
├── index.html      # landing pública
├── login.html      # ingreso + alta de alumno y de profesor
├── panel.html      # panel privado (vista alumno / vista staff)
├── css/
│   ├── styles.css  # paleta, tipografía, layout responsive y animaciones
│   ├── comun.css   # alertas, toasts, insignias, estados vacíos y skeletons
│   ├── auth.css    # login y registro
│   └── panel.css   # panel del alumno y del staff
├── js/
│   ├── script.js   # landing: menú móvil, scroll suave, animaciones, barra de lectura, parallax y año del footer
│   ├── api.js      # cliente de la API y manejo de la sesión
│   ├── ui.js       # helpers de DOM, formato de fechas/moneda y mensajes
│   ├── auth.js     # login, registro y selects de sede/profesor
│   ├── panel.js    # guardia de sesión, carga por rol y render del panel
│   ├── panel-ui.js # modal, drawer, confirmaciones y constructores de formulario
│   └── panel-acciones.js # acciones del panel: perfil, alumnos, lista, pagos, exámenes y noticias
└── assets/         # imágenes del PDF de referencia y favicon.svg con la marca
```

### Cómo ejecutarla

1. Levantá el backend (`Backend/app.py`, escucha en `http://127.0.0.1:4000`).
2. Serví `FrontEnd/` con un servidor estático: **Live Server** de VS Code o `python -m http.server 5601 --bind 127.0.0.1` desde la carpeta `FrontEnd`.
3. Abrí `http://127.0.0.1:5601/index.html`. No requiere Node.js, npm ni frameworks.

### Login, registro y panel

- El botón **Login** del header de la landing lleva a `login.html`.
- Se ingresa con **usuario o email** y contraseña. La casilla **Mantener la sesión abierta** guarda el token en `localStorage`; si se destilda, se usa `sessionStorage` y la sesión se cierra al cerrar la pestaña.
- **Alta de alumno**: DNI, nombre, apellido, email, usuario, contraseña (mínimo 8 caracteres), teléfono/nacimiento/emergencia opcionales, sede, profesor y fecha de inicio. Los selects se llenan con los `GET` públicos `/api/centros` y `/api/profesores`. La cuenta queda activa y puede ingresar enseguida.
- **Alta de profesor**: solo datos personales. La cuenta y la ficha de profesor quedan **inactivas** hasta que un `ADMIN` las habilite; el login responde 403 mientras tanto.
- **Panel por rol** (`panel.html`):
  - `ALUMNO`: sede, profesor y fecha de inicio; asistencias, cuotas abiertas, pagos confirmados y graduaciones; listados de cuotas, pagos, exámenes, graduaciones y novedades; canal de mensajes de su sede. Puede editar su perfil y su foto, cambiar la contraseña, declarar un pago (queda `PENDIENTE` hasta que la escuela lo confirme), inscribirse a un examen o cancelar la inscripción y escribirle a la escuela.
  - `PROFESOR` / `ADMIN`: totales de alumnos, profesores, sedes y pagos pendientes; tabla de alumnos con buscador (nombre, DNI, sede o profesor), pagos pendientes, agenda de exámenes y novedades. Puede dar de alta y editar alumnos (con baja lógica), abrir la **ficha 360** de cada alumno desde un drawer (datos, asistencias, cuotas, pagos, graduaciones e inscripciones), tomar lista por sede y fecha, registrar o confirmar pagos, **agendar/editar/eliminar exámenes**, publicar/editar/eliminar noticias y responder los mensajes de la sede. El `ADMIN` además gestiona las **sedes** (alta, edición, baja y reactivación). El perfil propio se edita con el mismo modal del alumno.
  - Los formularios y la ficha se abren dentro de `panel.html` (modal y drawer), sin páginas extra.
- Al entrar, el panel valida la sesión contra `/api/auth/me`. Si el token venció o la cuenta fue deshabilitada, limpia el almacenamiento y vuelve a `login.html?motivo=expirado`.
- La URL de la API se resuelve en este orden: `<meta name="crm-api">` → `localStorage.crm.apiBase` → mismo host en el puerto `4000` → `http://127.0.0.1:4000`.

### Pagos, exámenes, sedes, novedades y mensajes

- **Conceptos de pago**: el formulario (tanto el del alumno como el del staff) habilita `CUOTA` solo si el alumno tiene cuotas en estado `PENDIENTE` o `VENCIDA`, y `EXAMEN` solo si tiene inscripciones a examen activas. Si no hay datos para un concepto, la opción queda deshabilitada con una pista que explica el motivo y el formulario cae en `MATRICULA`. Al elegir `CUOTA` se cargan sus cuotas y el monto se completa solo.
- Las cuotas e inscripciones del modal se piden frescas a la API al abrirlo (no se usa la lista cacheada del panel), así el alumno ve lo que acaba de generarse.
- **Agenda de exámenes**: en la tarjeta **Exámenes programados** el staff usa **Nuevo examen** para cargar título, sede, profesor, fecha y hora, y monto (puede ser 0). Se guarda con `POST /api/examenes/`, se edita con `PUT /api/examenes/<id>` y se da de baja con `DELETE /api/examenes/<id>` (baja lógica: queda `INACTIVO` visible para el staff). Los exámenes activos se listan en `GET /api/examenes/proximos` y los de hoy siguen apareciendo aunque la hora ya haya pasado; el alumno los ve en su panel y se inscribe desde ahí.
- El `PROFESOR` solo agenda exámenes para sus sedes asignadas y para sí mismo, y solo puede editar o eliminar los que tiene asignados. El `ADMIN` puede hacerlo en cualquier sede y con cualquier profesor. La regla se valida en el backend: un `PROFESOR` que intente otra sede u otro docente recibe `403`.
- **Sedes**: solo el `ADMIN` ve la tarjeta **Sedes**. Se crea con `POST /api/centros` (nombre obligatorio; dirección, teléfono e imagen opcionales), se edita con `PUT /api/centros/<id>` y se da de baja con `DELETE /api/centros/<id>` (baja lógica). Las sedes dadas de baja quedan con la insignia `INACTIVA` y se pueden **reactivar**; al guardar se refrescan los selectores de alumnos, exámenes, noticias y mensajes. El `PROFESOR` no ve la tarjeta y el backend rechaza sus intentos con `403`.
- **Novedades**: el staff publica con `POST /api/noticias` y edita con `PUT /api/noticias/<id>` (título, contenido, sede opcional e imagen por URL). El autor sale del token. Eliminar es una baja lógica con `DELETE /api/noticias/<id>`: la noticia queda `INACTIVA`, se sigue viendo en el panel del staff con su insignia pero ya no se muestra a los alumnos ni ofrece acciones.
- El `PROFESOR` solo puede publicar, editar y eliminar novedades de sus sedes asignadas; la opción **General (todas las sedes)** y las noticias de otras sedes quedan reservadas al `ADMIN`. La regla se valida en el backend, no solo en la interfaz: pedir otra sede devuelve `403`.
- El alumno ve en **Novedades** las noticias generales y las de su propia sede (`GET /api/noticias/centro/<id>`); las inactivas solo las ve el staff.
- **Mensajes por sede**: se leen con `GET /api/chat/centro/<id>` y se envían con `POST /api/chat` (máximo 500 caracteres). El alumno escribe en el canal de la sede de su perfil; el staff elige la sede en un selector (el `ADMIN` ve todas, el `PROFESOR` solo las propias). Cada mensaje muestra emisor, rol, avatar y fecha, y los propios se alinean a la derecha.

### Mockup del portal del alumno

En la raíz del repositorio hay un `index.html` aparte: es el **mockup del Portal del Alumno** (HTML + Tailwind por CDN), usado como sitio placeholder. Se publica en GitHub Pages: <https://eliasescalante.github.io/CRM-Practica-Profesionalizante-Academia/>. No forma parte de la landing de `FrontEnd/`.

### Codificación de los archivos

Los archivos de código de `FrontEnd/` (`*.html`, `css/*.css`, `js/*.js`) se guardan en **UTF-8 con BOM** (`EF BB BF`), con un solo BOM por archivo. El `.md` y los assets no llevan BOM.


### Imágenes de los testimonios

Las 3 fotos de los testimonios (`FrontEnd/assets/testimonial-1.jpg`, `FrontEnd/assets/testimonial-2.jpg` y `FrontEnd/assets/testimonial-3.jpg`) se extrajeron de la página 4 del PDF de referencia. `testimonial-3.jpg` no estaba en el paquete original de la plantilla:

## Paleta

El acento de la marca es **verde brillante** | para textos sobre fondos claros y para detalles sobre verde. El rojo se usa solo en detalles puntuales.

## Responsive

La página se adapta a celulares, tablets, notebooks y distintos monitores:


## Dinamismo (JavaScript)

- **Transición fuerte por sección**: cada `<section>` entra con desplazamiento, escala y desenfoque (las pares desde la derecha, las impares desde la izquierda) más un barrido de luz. **Se repite cada vez** que la sección vuelve a entrar en pantalla.
- **Contenido en cascada**: kicker, regla, títulos y tarjetas aparecen escalonados al entrar cada sección.
- Barra de progreso de lectura y header que se compacta al scrollear.
- Parallax suave del hero (solo desktop).
- Efecto de luz que sigue al cursor en tarjetas y testimonios.
- Las cards de testimonios tienen **foto de la persona** en la parte superior
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

El botón del header dice **Login** y lleva a `login.html`, donde están el ingreso y el alta de alumno/profesor.

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
