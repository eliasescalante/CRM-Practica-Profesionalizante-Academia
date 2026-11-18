# Guía de deploy — CRM Tien Long Hu

Esta guía deja el proyecto listo para probarlo online. La recomendación para
esta etapa es **un solo host**: Flask sirve la API **y** el frontend. Es la
opción con menos piezas, sin CORS y con una sola URL para configurar en Google.

---

## 1. Decisión rápida: ¿mismo host o separados?

### Recomendado: mismo host (Flask sirve todo)

- Una sola URL: `https://tu-app.onrender.com`
- Sin problemas de CORS.
- Un solo origen para autorizar en Google.
- El `FrontEnd/` ya se sirve desde `Backend/app.py` si está en la carpeta de al
  lado (que es como está en el repo).
- Subís una sola cosa y actualizás una sola cosa.

### Separado (frontend estático + API aparte)

- Útil si querés CDN, dominios distintos o escalar por separado.
- Requiere configurar `CORS_ORIGINS` y `FrontEnd/js/config.js`.
- Más piezas y más lugares donde equivocarse con el login de Google.

Para la presentación y las primeras pruebas, **elegí el mismo host**.

---

## 2. Qué quedó preparado en el código

- `Backend/app.py` sirve `FrontEnd/` (landing, login y panel) y la API desde el
  mismo servidor. Los endpoints `/api/*` tienen prioridad.
- `PORT`, `HOST` y `FLASK_DEBUG` se leen de variables de entorno.
- `CORS_ORIGINS` permite limitar CORS a dominios concretos.
- `Backend/database/connection.py` soporta MySQL con TLS (`DB_SSL=1`).
- `FrontEnd/js/config.js` permite apuntar la API a otro dominio.
- `FrontEnd/js/api.js` usa el mismo origen cuando el sitio está en un dominio
  público, y `:4000` cuando estás en local.
- `/api/ping` es un health check liviano (no toca la base).
- `Procfile` con el comando de producción.
- `requirements.txt` en la raíz (incluye el de `Backend/`) para que Render y
  Railway detecten Python sin configurar nada extra.
- `Backend/.env.example` con todas las variables.
- `gunicorn` agregado a `requirements.txt` solo para Linux/macOS.

---

## 3. Opción A — Railway (backend + MySQL, la más simple)

1. Subí el repo a GitHub (sin `.env`).
2. En [Railway](https://railway.app/) creá un proyecto nuevo desde el repo.
3. Agregá un servicio **MySQL** al mismo proyecto.
4. En el servicio web, configurá:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn --chdir Backend app:app --bind 0.0.0.0:$PORT`
   - **Health check:** `/api/ping`
5. Cargá las variables de entorno (sección 5). Para la base usá los datos que
   muestra el servicio MySQL de Railway.
6. Importá la base (sección 6).
7. Abrí la URL pública. La landing, el login y el panel salen del mismo host.

> Railway da créditos de prueba. Si se agotan, pasá a la Opción B.

---

## 4. Opción B — Render + Aiven (gratis, con límites)

1. Creá un MySQL gratis en [Aiven](https://aiven.io/) (plan free).
   - Anotá host, puerto, usuario, contraseña y nombre de la base.
   - Aiven exige TLS: `DB_SSL=1`.
2. En [Render](https://render.com/) creá un **Web Service** desde el repo.
   - **Runtime:** Python 3.12
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn --chdir Backend app:app --bind 0.0.0.0:$PORT`
   - **Health check:** `/api/ping`
3. Cargá las variables de entorno (sección 5).
4. Importá la base (sección 6).
5. Abrí la URL `https://tu-app.onrender.com`.

> El plan free de Render duerme el servicio tras unos minutos sin uso. La
> primera visita puede tardar 30–60 segundos. Para la presentación, entrá unos
> minutos antes para "despertarlo".

### Si querés el frontend separado (Netlify)

1. Publicá la carpeta `FrontEnd/` como sitio estático en Netlify.
2. En `FrontEnd/js/config.js` poné la URL del backend:
   ```js
   window.CRM_API_BASE = 'https://tu-app.onrender.com';
   ```
3. En Render agregá:
   ```env
   CORS_ORIGINS=https://tu-frontend.netlify.app
   ```
4. En Google Cloud agregá también el origen de Netlify (sección 7).

---

## 5. Variables de entorno

Copiá `Backend/.env.example` como referencia. En el host cargá:

| Variable | Ejemplo | Notas |
|---|---|---|
| `PORT` | `4000` | En Render/Railway lo asigna el host; no lo pises salvo que sepas. |
| `HOST` | `0.0.0.0` | En producción. |
| `FLASK_DEBUG` | `0` | **Nunca** `1` en producción. |
| `DB_HOST` | `mysql.railway.internal` | El host de tu base. |
| `DB_PORT` | `3306` | El puerto de tu base. |
| `DB_USER` | `root` | Usuario de la base. |
| `DB_PASSWORD` | `...` | Contraseña de la base. |
| `DB_NAME` | `crm_artes_marciales` | Nombre de la base. |
| `DB_SSL` | `1` | Solo si el proveedor exige TLS (Aiven, la mayoría en la nube). |
| `DB_SSL_CA` | `/etc/ssl/ca.pem` | Opcional, si el proveedor da un CA. |
| `JWT_SECRET` | cadena larga y aleatoria | **Cambiala** respecto de local. |
| `CLOUDINARY_CLOUD_NAME` | `...` | Fotos de perfil. |
| `CLOUDINARY_API_KEY` | `...` | |
| `CLOUDINARY_API_SECRET` | `...` | |
| `GOOGLE_CLIENT_ID` | `...apps.googleusercontent.com` | El mismo de local. |
| `GOOGLE_AUTO_ALTA` | `1` | Crea alumno provisorio al entrar con Google. |
| `CORS_ORIGINS` | `https://tu-front.netlify.app` | Solo si el frontend está separado. |

Para generar un secreto nuevo:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## 6. Base de datos: pasar de XAMPP a la nube

Tu XAMPP corre **MariaDB 10.4** y los proveedores dan **MySQL 8**. Revisé el
esquema real y no usa nada problemático (sin `JSON`, sin `CHECK`, sin columnas
generadas, sin `GROUP BY` con columnas sueltas), así que el dump importa tal cual.
Además las contraseñas son hashes bcrypt: se copian y siguen funcionando igual.

La base local es la fuente de verdad. **No uses `Backend/Docs/db.sql` para
producción**: es un esquema viejo y no tiene los datos.

### Exportar (con MySQL/XAMPP encendido)

```powershell
& "C:\xampp2\mysql\bin\mysqldump.exe" -u root `
  --routines --triggers --single-transaction --no-tablespaces `
  --default-character-set=utf8mb4 `
  --result-file=crm_dump.sql crm_artes_marciales
```

Esto genera el dump **sin** `CREATE DATABASE`: sirve cuando la base ya existe en
la nube (lo normal en Aiven y Railway). Usá `--result-file` y no `>`: con `>` en
PowerShell el archivo puede salir en UTF-16 y romper los acentos.

Si el host te deja crear la base vos (por ejemplo un MySQL propio), agregá
`--databases crm_artes_marciales` y el dump crea y selecciona la base solo.

### Importar en la nube

Desde **cmd** (no PowerShell), para que los acentos y la ñ viajen bien:

```bat
"C:\xampp2\mysql\bin\mysql.exe" --default-character-set=utf8mb4 ^
  -h TU_HOST -P TU_PUERTO -u TU_USUARIO -p TU_BASE < crm_dump.sql
```

Si tu cliente es MySQL 8, el mismo comando sirve. Alternativas cómodas si no
querés instalar el cliente: la consola web de Aiven o **Adminer/phpMyAdmin** del
panel del proveedor (importar el `.sql`).

> No uses `Get-Content crm_dump.sql | mysql`: PowerShell reescribe el texto y
> puede convertir `Pérez` en `PÃ©rez`.

Después verificá desde la app: `/api/status` debe decir `database: OK`.

### Datos reales: armá un dump de demo

La base tiene nombres, DNI, emails y teléfonos de alumnos reales (varios
menores). Si el deploy va a quedar público, no subas esos datos tal cual:
duplicá la base, reemplazá los datos personales por ficticios y subí **esa**
copia. XAMPP queda como fuente de verdad y backup de la academia.

### Si el plan free te queda chico o duerme

- Para la **demo**, si preferís no migrar nada: `cloudflared tunnel --url
  http://localhost:4000` publica tu Flask local con HTTPS en segundos. Sirve para
  mostrar, pero la notebook tiene que estar prendida y la URL cambia en cada
  arranque (y Google exige registrar ese origen).
- Para producción real, un MySQL pago chico (Aiven, Railway o el hosting de la
  escuela) con backups automáticos es lo que corresponde.

> Si preferís arrancar de cero, `db.sql` crea las tablas pero no los usuarios.
> Para una demo conviene importar el dump completo.

---

## 7. Google: origen de producción

El error `no registered origin` es de Google, no de la base ni del backend: la
petición nunca llega al CRM.

En [Google Cloud Console](https://console.cloud.google.com/), proyecto
`crm-academia-artes-marciales` (número `780727382867`):

1. **APIs y servicios → Credenciales →** cliente OAuth
   `780727382867-9sseanlsavmf92h782p33e0doollakos`.
2. **Orígenes de JavaScript autorizados** → agregá el origen exacto, sin ruta ni
   barra final:
   - Local con Live Server: `http://localhost:5500` y `http://127.0.0.1:5500`
   - Local con Flask sirviendo todo: `http://localhost:4000` y
     `http://127.0.0.1:4000`
   - Producción: `https://tu-app.onrender.com`
   - Si el frontend está en Netlify: `https://tu-frontend.netlify.app`
3. **Pantalla de consentimiento → Usuarios de prueba:** agregá las cuentas de
   Google con las que vas a probar.
4. Guardá y esperá unos minutos. Probá en incógnito.

> El origen tiene que coincidir con `location.origin` (protocolo + host +
> puerto). Si abrís el HTML con `file://`, Google no lo acepta nunca.

---

## 8. Checklist después del deploy

- [ ] `https://tu-app.onrender.com/api/ping` responde `{"status":"OK"}`.
- [ ] `/api/status` muestra `database: OK` y `cloudinary: OK`.
- [ ] La landing carga con estilos e imágenes.
- [ ] Se puede iniciar sesión con usuario y contraseña.
- [ ] El panel del alumno y el del staff cargan datos.
- [ ] Se puede subir una foto de perfil (Cloudinary).
- [ ] "Continuar con Google" abre el selector y crea la cuenta provisoria.
- [ ] El alumno puede cambiar su contraseña desde **Mi perfil**.
- [ ] En celular se ve bien (probá 390 px de ancho).
- [ ] Reiniciá el servicio y verificá que la sesión sigue funcionando.

---

## 9. Seguridad y mantenimiento

- `FLASK_DEBUG=0` en producción (el modo debug expone información y permite
  ejecución de código).
- `JWT_SECRET` distinto del de desarrollo.
- `.env` fuera del repositorio; solo se versiona `.env.example`.
- HTTPS obligatorio (Render/Railway lo dan gratis).
- Backups: activá el backup automático del proveedor de MySQL o programá un
  `mysqldump` periódico.
- Las fotos van a Cloudinary, así que no necesitás disco persistente.
- Si el servicio duerme (plan free), la primera visita es lenta: avisá en la
  presentación o usá un plan pago temporal.

---

## 10. Problemas típicos

| Síntoma | Causa probable | Solución |
|---|---|---|
| `no registered origin` | El origen no está en el cliente OAuth | Agregarlo en Google Cloud (sección 7). |
| `invalid_client` | Client ID distinto o cliente borrado | Verificar que el ID del `.env` exista en el proyecto correcto. |
| `database: ERROR` | Variables DB_* mal cargadas o falta `DB_SSL=1` | Revisar la sección 5. |
| `cloudinary: ERROR` | Faltan las claves | Cargar `CLOUDINARY_*`. |
| El frontend pega a `:4000` en producción | `CRM_API_BASE` o el origen no se resolvió | Revisar `js/config.js`; en mismo host debe quedar vacío. |
| CORS bloqueado | Frontend separado sin `CORS_ORIGINS` | Cargar el dominio exacto. |
| La base se conecta en local pero no en la nube | Falta TLS | `DB_SSL=1`. |
| Los cambios de Google tardan | Propagación | Esperar unos minutos y probar en incógnito. |
