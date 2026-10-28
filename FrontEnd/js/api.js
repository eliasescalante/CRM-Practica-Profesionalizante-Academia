/* =========================================================
   Tien Long Hu - Cliente de la API del CRM
   ---------------------------------------------------------
   Un solo lugar para hablar con el backend:
     - resuelve la URL base
     - guarda y lee el token (localStorage / sessionStorage)
     - normaliza los errores para que la UI muestre el "mensaje"
       real que devuelve Flask

   No usa librerías. Se carga antes que auth.js y panel.js.
   ========================================================= */

const API = (function () {
  'use strict';

  const CLAVE_TOKEN = 'crm.token';
  const CLAVE_USUARIO = 'crm.usuario';
  const CLAVE_BASE = 'crm.apiBase';

  /* ---------------------------------------------------------
     URL base
     ---------------------------------------------------------
     Prioridad:
       1) <meta name="api-base" content="..."> en el HTML
       2) localStorage.crm.apiBase (para probar contra otra IP)
       3) el mismo host desde el que se sirve el front, puerto 4000
          (así funciona también desde el celular en la misma red)
       4) 127.0.0.1:4000 si se abre el HTML como archivo
     --------------------------------------------------------- */
  function resolverBase() {
    const meta = document.querySelector('meta[name="api-base"]');

    if (meta && meta.content) {
      return meta.content.replace(/\/+$/, '');
    }

    try {
      const guardada = window.localStorage.getItem(CLAVE_BASE);
      if (guardada) {
        return guardada.replace(/\/+$/, '');
      }
    } catch (error) {
      /* localStorage bloqueado: seguimos con el default */
    }

    if (location.protocol === 'http:' || location.protocol === 'https:') {
      return location.protocol + '//' + location.hostname + ':4000';
    }

    return 'http://127.0.0.1:4000';
  }

  const BASE = resolverBase();

  /* ---------------------------------------------------------
     Sesión
     --------------------------------------------------------- */

  function almacen(recordar) {
    return recordar ? window.localStorage : window.sessionStorage;
  }

  function otroAlmacen(recordar) {
    return recordar ? window.sessionStorage : window.localStorage;
  }

  function leerDe(clave) {
    try {
      return (
        window.localStorage.getItem(clave) ||
        window.sessionStorage.getItem(clave)
      );
    } catch (error) {
      return null;
    }
  }

  function limpiarSesion() {
    try {
      [window.localStorage, window.sessionStorage].forEach(function (store) {
        store.removeItem(CLAVE_TOKEN);
        store.removeItem(CLAVE_USUARIO);
      });
    } catch (error) {
      /* sin storage disponible */
    }
  }

  function guardarSesion(token, usuario, recordar) {
    const destino = almacen(recordar);
    const sobrante = otroAlmacen(recordar);

    try {
      sobrante.removeItem(CLAVE_TOKEN);
      sobrante.removeItem(CLAVE_USUARIO);

      destino.setItem(CLAVE_TOKEN, token);
      destino.setItem(CLAVE_USUARIO, JSON.stringify(usuario || null));
    } catch (error) {
      /* si no se puede persistir, la sesión vive solo en memoria */
      memoria.token = token;
      memoria.usuario = usuario || null;
    }
  }

  const memoria = { token: null, usuario: null };

  function token() {
    return leerDe(CLAVE_TOKEN) || memoria.token;
  }

  function usuario() {
    const crudo = leerDe(CLAVE_USUARIO);

    if (!crudo) {
      return memoria.usuario;
    }

    try {
      return JSON.parse(crudo);
    } catch (error) {
      return memoria.usuario;
    }
  }

  function haySesion() {
    return Boolean(token());
  }

  /* ---------------------------------------------------------
     Petición genérica
     ---------------------------------------------------------
     Devuelve siempre un objeto { ok, status, data }.
     Nunca lanza: los errores de red también vuelven como dato.
     --------------------------------------------------------- */
  async function pedir(ruta, opciones) {
    const config = opciones || {};
    const method = config.method || 'GET';
    const conAuth = config.auth !== false;

    const headers = { Accept: 'application/json' };
    let body;

    if (config.body instanceof window.FormData) {
      /* Multipart: el navegador arma el Content-Type con el boundary. */
      body = config.body;
    } else if (config.body !== undefined && config.body !== null) {
      headers['Content-Type'] = 'application/json';
      body = JSON.stringify(config.body);
    }

    if (conAuth && token()) {
      headers.Authorization = 'Bearer ' + token();
    }

    let respuesta;

    try {
      respuesta = await fetch(BASE + ruta, {
        method: method,
        headers: headers,
        body: body
      });
    } catch (error) {
      return {
        ok: false,
        status: 0,
        data: {
          status: 'ERROR',
          mensaje:
            'No pudimos conectar con el servidor (' +
            BASE +
            '). Verificá que el backend esté iniciado.'
        }
      };
    }

    const texto = await respuesta.text();
    let data = null;

    if (texto) {
      try {
        data = JSON.parse(texto);
      } catch (error) {
        data = null;
      }
    }

    return { ok: respuesta.ok, status: respuesta.status, data: data };
  }

  /* Saca el mensaje legible de una respuesta de error. */
  function mensaje(resultado) {
    if (!resultado) {
      return 'Ocurrió un error inesperado.';
    }

    const data = resultado.data;

    if (data && typeof data === 'object') {
      let texto = data.mensaje || data.message;

      if (!texto && data.status === 'ERROR') {
        texto = 'La operación no se pudo completar.';
      }

      if (texto && Array.isArray(data.campos) && data.campos.length) {
        texto += ' (' + data.campos.join(', ') + ')';
      }

      if (texto) {
        return texto;
      }
    }

    if (resultado.status === 0) {
      return 'No pudimos conectar con el servidor.';
    }

    if (resultado.status === 401) {
      return 'Tu sesión expiró. Volvé a ingresar.';
    }

    if (resultado.status === 403) {
      return 'No tenés permisos para ver esto.';
    }

    if (resultado.status === 404) {
      return 'No encontramos lo que buscabas.';
    }

    return 'Error ' + resultado.status + ' del servidor.';
  }

  /* ---------------------------------------------------------
     Atajos por endpoint
     --------------------------------------------------------- */

  const auth = {
    login: function (usuarioTexto, contrasenia) {
      return pedir('/api/auth/login', {
        method: 'POST',
        auth: false,
        body: { usuario: usuarioTexto, contrasenia: contrasenia }
      });
    },

    me: function () {
      return pedir('/api/auth/me');
    },

    registroAlumno: function (datos) {
      return pedir('/api/auth/register', {
        method: 'POST',
        auth: false,
        body: datos
      });
    },

    registroProfesor: function (datos) {
      return pedir('/api/auth/register-profesor', {
        method: 'POST',
        auth: false,
        body: datos
      });
    }
  };

  const get = function (ruta) {
    return pedir(ruta);
  };

  const post = function (ruta, body) {
    return pedir(ruta, { method: 'POST', body: body });
  };

  const put = function (ruta, body) {
    return pedir(ruta, { method: 'PUT', body: body });
  };

  const del = function (ruta) {
    return pedir(ruta, { method: 'DELETE' });
  };

  /* Sube la foto de perfil. El backend toma la persona del token. */
  function subirAvatar(archivo, personaId) {
    const datos = new window.FormData();

    datos.append('file', archivo);

    if (personaId) {
      datos.append('persona_id', personaId);
    }

    return pedir('/api/upload/avatar', {
      method: 'POST',
      body: datos
    });
  }

  /* Mantiene sincronizado el usuario guardado en el storage después
     de editar el perfil, sin pedir un login nuevo. */
  function actualizarUsuario(cambios) {
    const actual = usuario() || {};
    const nuevo = Object.assign({}, actual, cambios || {});
    let recordar = false;

    try {
      recordar = Boolean(window.localStorage.getItem(CLAVE_TOKEN));
    } catch (error) {
      recordar = false;
    }

    guardarSesion(token(), nuevo, recordar);

    return nuevo;
  }

  /* ---------------------------------------------------------
     Navegación / guardia de sesión
     --------------------------------------------------------- */

  function irALogin(motivo) {
    let destino = 'login.html';

    if (motivo) {
      destino += '?motivo=' + encodeURIComponent(motivo);
    }

    location.replace(destino);
  }

  function requerirSesion() {
    if (!haySesion()) {
      irALogin('sin-sesion');
      return false;
    }

    return true;
  }

  function cerrarSesion() {
    limpiarSesion();
    memoria.token = null;
    memoria.usuario = null;
    location.replace('login.html?motivo=saliste');
  }

  /* Si el backend dice que el token ya no sirve, cerramos acá.
     Un 403 de permisos (por ejemplo, un ALUMNO pidiendo datos de otro)
     no invalida la sesión. Tampoco un 401 de credenciales: el cambio
     de contraseña responde 401 cuando la actual está mal. */
  function sesionInvalida(resultado) {
    if (!resultado) {
      return false;
    }

    const data = resultado.data || {};
    const detalle = String(data.mensaje || data.message || '');
    const esCredencial = /contrase|credencial|password/i.test(detalle);

    if (resultado.status === 401) {
      return !esCredencial;
    }

    if (resultado.status !== 403) {
      return false;
    }

    return /inactiva|ya no existe|no autenticado/i.test(detalle);
  }

  return {
    base: BASE,
    pedir: pedir,
    get: get,
    post: post,
    put: put,
    del: del,
    subirAvatar: subirAvatar,
    mensaje: mensaje,
    auth: auth,
    token: token,
    usuario: usuario,
    actualizarUsuario: actualizarUsuario,
    haySesion: haySesion,
    guardarSesion: guardarSesion,
    limpiarSesion: limpiarSesion,
    cerrarSesion: cerrarSesion,
    requerirSesion: requerirSesion,
    irALogin: irALogin,
    sesionInvalida: sesionInvalida
  };
})();

window.API = API;
