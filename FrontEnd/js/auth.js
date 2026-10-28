/* =========================================================
   Tien Long Hu - Login y registro
   ---------------------------------------------------------
   - Login real contra POST /api/auth/login
   - Guarda el token y redirige al panel (que muestra una vista
     distinta según el rol: ALUMNO vs PROFESOR/ADMIN)
   - Registro de alumno: POST /api/auth/register
   - Registro de profesor: POST /api/auth/register-profesor
     (queda pendiente de habilitación)
   - Las sedes y profesores del alta salen de los GET públicos
   ========================================================= */

(function () {
  'use strict';

  const $ = UI.qs;
  const $$ = UI.qsa;

  /* ---------------------------------------------------------
     Nodos
     --------------------------------------------------------- */

  const tabLogin = $('#tab-login');
  const tabRegistro = $('#tab-registro');
  const panelLogin = $('#panel-login');
  const panelRegistro = $('#panel-registro');

  const tabAlumno = $('#tab-alumno');
  const tabProfesor = $('#tab-profesor');
  const wrapAlumno = $('#wrap-alumno');
  const wrapProfesor = $('#wrap-profesor');

  const formLogin = $('#form-login');
  const loginUsuario = $('#login-usuario');
  const loginClave = $('#login-clave');
  const loginRecordar = $('#login-recordar');
  const loginEnviar = $('#login-enviar');
  const avisoLogin = $('#login-aviso');

  const formAlumno = $('#form-alumno');
  const alEnviar = $('#al-enviar');
  const alCentro = $('#al-centro');
  const alProfesor = $('#al-profesor');
  const alInicio = $('#al-inicio');
  const avisoRegistro = $('#registro-aviso');

  const formProfesor = $('#form-profesor');
  const prEnviar = $('#pr-enviar');

  /* Estado del formulario de alumno */
  let sedes = [];
  let profesores = [];
  let opcionesCargadas = false;
  let cargandoOpciones = false;

  /* ---------------------------------------------------------
     Mensajes según cómo se llegó a esta página
     --------------------------------------------------------- */

  const MOTIVOS = {
    expirado: ['Tu sesión expiró. Volvé a ingresar.', 'aviso'],
    'sin-sesion': ['Necesitás ingresar para ver tu panel.', 'info'],
    saliste: ['Cerraste sesión. ¡Hasta la próxima!', 'ok'],
    registrado: ['Cuenta creada. Ya podés ingresar.', 'ok']
  };

  function leerMotivo() {
    const parametros = new URLSearchParams(location.search);
    const motivo = parametros.get('motivo');

    if (!motivo || !MOTIVOS[motivo]) {
      return;
    }

    const datos = MOTIVOS[motivo];
    UI.mostrarMensaje(avisoLogin, datos[0], datos[1]);
  }

  /* ---------------------------------------------------------
     Si ya hay una sesión guardada, vamos directo al panel
     (validando el token antes para no mandar a un panel roto)
     --------------------------------------------------------- */

  async function saltarSiHaySesion() {
    if (!API.haySesion()) {
      return;
    }

    const resultado = await API.auth.me();

    if (resultado.ok) {
      location.replace('panel.html');
      return;
    }

    if (API.sesionInvalida(resultado)) {
      API.limpiarSesion();
    }
  }

  /* ---------------------------------------------------------
     Tabs
     --------------------------------------------------------- */

  function activarVista(nombre) {
    const esLogin = nombre === 'login';

    tabLogin.setAttribute('aria-selected', String(esLogin));
    tabRegistro.setAttribute('aria-selected', String(!esLogin));
    panelLogin.hidden = !esLogin;
    panelRegistro.hidden = esLogin;

    if (!esLogin) {
      cargarOpciones();
    }

    const destino = esLogin ? panelLogin : panelRegistro;
    destino.focus({ preventScroll: true });
  }

  function activarTipo(nombre) {
    const esAlumno = nombre === 'alumno';

    tabAlumno.setAttribute('aria-selected', String(esAlumno));
    tabProfesor.setAttribute('aria-selected', String(!esAlumno));
    wrapAlumno.hidden = !esAlumno;
    wrapProfesor.hidden = esAlumno;

    if (esAlumno) {
      cargarOpciones();
    }

    (esAlumno ? wrapAlumno : wrapProfesor).focus({ preventScroll: true });
  }

  tabLogin.addEventListener('click', function () {
    activarVista('login');
  });

  tabRegistro.addEventListener('click', function () {
    activarVista('registro');
  });

  tabAlumno.addEventListener('click', function () {
    activarTipo('alumno');
  });

  tabProfesor.addEventListener('click', function () {
    activarTipo('profesor');
  });

  /* Navegación con flechas dentro de cada tablist */
  function flechas(contenedor, manejador) {
    contenedor.addEventListener('keydown', function (evento) {
      if (evento.key !== 'ArrowLeft' && evento.key !== 'ArrowRight') {
        return;
      }

      evento.preventDefault();
      manejador(evento.key === 'ArrowRight' ? 1 : -1);
    });
  }

  flechas($('.auth-tabs'), function (paso) {
    activarVista(paso > 0 ? 'registro' : 'login');
  });

  flechas($('.auth-switch'), function (paso) {
    activarTipo(paso > 0 ? 'profesor' : 'alumno');
  });

  $$('[data-ir]').forEach(function (boton) {
    boton.addEventListener('click', function () {
      activarVista(boton.getAttribute('data-ir'));
    });
  });

  /* ---------------------------------------------------------
     Mostrar / ocultar contraseñas
     --------------------------------------------------------- */

  $$('.ver-clave').forEach(function (boton) {
    boton.addEventListener('click', function () {
      const input = document.getElementById(boton.getAttribute('data-ver'));

      if (!input) {
        return;
      }

      const mostrar = input.type === 'password';

      input.type = mostrar ? 'text' : 'password';
      boton.textContent = mostrar ? 'Ocultar' : 'Ver';
      boton.setAttribute('aria-pressed', String(mostrar));
      input.focus({ preventScroll: true });
    });
  });

  /* ---------------------------------------------------------
     Botones en estado "enviando"
     --------------------------------------------------------- */

  function enviando(boton, texto) {
    if (!boton.dataset.htmlOriginal) {
      boton.dataset.htmlOriginal = boton.innerHTML;
    }

    boton.disabled = true;
    boton.textContent = texto;
  }

  function listo(boton) {
    boton.disabled = false;

    if (boton.dataset.htmlOriginal) {
      boton.innerHTML = boton.dataset.htmlOriginal;
    }
  }

  /* ---------------------------------------------------------
     Login
     --------------------------------------------------------- */

  formLogin.addEventListener('submit', async function (evento) {
    evento.preventDefault();
    UI.ocultarMensaje(avisoLogin);

    const usuario = loginUsuario.value.trim();
    const contrasenia = loginClave.value;

    if (!usuario || !contrasenia) {
      UI.mostrarMensaje(
        avisoLogin,
        'Completá tu usuario (o email) y tu contraseña.',
        'error'
      );
      (!usuario ? loginUsuario : loginClave).focus();
      return;
    }

    enviando(loginEnviar, 'Ingresando…');

    const resultado = await API.auth.login(usuario, contrasenia);

    if (!resultado.ok) {
      listo(loginEnviar);
      UI.mostrarMensaje(
        avisoLogin,
        API.mensaje(resultado),
        resultado.status === 403 ? 'aviso' : 'error'
      );
      loginClave.select();
      return;
    }

    API.guardarSesion(
      resultado.data.token,
      resultado.data.usuario,
      loginRecordar.checked
    );

    location.replace('panel.html');
  });

  /* ---------------------------------------------------------
     Sedes y profesores para el alta de alumno
     --------------------------------------------------------- */

  function opcion(valor, texto) {
    const nodo = document.createElement('option');

    nodo.value = String(valor);
    nodo.textContent = texto;

    return nodo;
  }

  function limpiarSelect(select) {
    while (select.firstChild) {
      select.removeChild(select.firstChild);
    }
  }

  function poblarSedes() {
    limpiarSelect(alCentro);

    if (!sedes.length) {
      alCentro.appendChild(opcion('', 'No hay sedes disponibles'));
      alCentro.disabled = true;
      return;
    }

    alCentro.disabled = false;
    alCentro.appendChild(opcion('', 'Elegí tu sede'));

    sedes.forEach(function (sede) {
      alCentro.appendChild(
        opcion(sede.centro_id, sede.nombre + (sede.direccion ? ' · ' + sede.direccion : ''))
      );
    });

    if (sedes.length === 1) {
      alCentro.value = String(sedes[0].centro_id);
      poblarProfesores();
    }
  }

  function profesoresDeCentro(centroId) {
    if (!centroId) {
      return [];
    }

    return profesores.filter(function (profesor) {
      return (profesor.centros || []).some(function (centro) {
        return String(centro.centro_id) === String(centroId);
      });
    });
  }

  function poblarProfesores() {
    const centroId = alCentro.value;
    limpiarSelect(alProfesor);

    if (!centroId) {
      alProfesor.appendChild(opcion('', 'Elegí una sede primero'));
      return;
    }

    const disponibles = profesoresDeCentro(centroId);

    if (!disponibles.length) {
      alProfesor.appendChild(opcion('', 'No hay profesores en esta sede'));
      return;
    }

    alProfesor.appendChild(opcion('', 'Elegí tu profesor'));

    disponibles.forEach(function (profesor) {
      const nombre = (profesor.nombre || '') + ' ' + (profesor.apellido || '');
      alProfesor.appendChild(
        opcion(profesor.profesor_id, nombre.trim() || 'Profesor ' + profesor.profesor_id)
      );
    });

    if (disponibles.length === 1) {
      alProfesor.value = String(disponibles[0].profesor_id);
    }
  }

  alCentro.addEventListener('change', poblarProfesores);

  async function cargarOpciones() {
    if (opcionesCargadas || cargandoOpciones) {
      return;
    }

    cargandoOpciones = true;

    const respuestas = await Promise.all([
      API.get('/api/centros'),
      API.get('/api/profesores')
    ]);

    const centrosOk = respuestas[0];
    const profesoresOk = respuestas[1];

    cargandoOpciones = false;

    if (!centrosOk.ok || !profesoresOk.ok) {
      limpiarSelect(alCentro);
      alCentro.appendChild(opcion('', 'No se pudieron cargar las sedes'));
      alCentro.disabled = true;

      UI.mostrarMensaje(
        avisoRegistro,
        'No pudimos cargar las sedes y profesores. ' +
          API.mensaje(!centrosOk.ok ? centrosOk : profesoresOk),
        'error'
      );
      return;
    }

    sedes = centrosOk.data.centros || [];
    profesores = profesoresOk.data.profesores || [];
    opcionesCargadas = true;

    poblarSedes();
  }

  /* ---------------------------------------------------------
     Alta de alumno
     --------------------------------------------------------- */

  function valor(id) {
    const campo = document.getElementById(id);

    if (!campo) {
      return '';
    }

    return String(campo.value || '').trim();
  }

  function hoyISO() {
    const fecha = new Date();
    const mes = String(fecha.getMonth() + 1).padStart(2, '0');
    const dia = String(fecha.getDate()).padStart(2, '0');

    return fecha.getFullYear() + '-' + mes + '-' + dia;
  }

  function prepararFormularios() {
    if (alInicio) {
      alInicio.value = hoyISO();
    }

    const nacimiento = $('#al-nacimiento');

    if (nacimiento) {
      nacimiento.max = hoyISO();
    }
  }

  formAlumno.addEventListener('submit', async function (evento) {
    evento.preventDefault();
    UI.ocultarMensaje(avisoRegistro);

    if (!formAlumno.reportValidity()) {
      return;
    }

    if (!alProfesor.value) {
      UI.mostrarMensaje(
        avisoRegistro,
        'Elegí el profesor con el que vas a entrenar.',
        'error'
      );
      alProfesor.focus();
      return;
    }

    const datos = {
      dni: valor('al-dni'),
      nombre: valor('al-nombre'),
      apellido: valor('al-apellido'),
      email: valor('al-email'),
      usuario: valor('al-usuario'),
      contrasenia: document.getElementById('al-clave').value,
      centro_id: Number(alCentro.value),
      profesor_id: Number(alProfesor.value),
      fecha_inicio: valor('al-inicio')
    };

    const telefono = valor('al-telefono');
    const nacimiento = valor('al-nacimiento');
    const emergencia = valor('al-emergencia');

    if (telefono) {
      datos.telefono = telefono;
    }

    if (nacimiento) {
      datos.fecha_nacimiento = nacimiento;
    }

    if (emergencia) {
      datos.contacto_emergencia = emergencia;
    }

    enviando(alEnviar, 'Creando cuenta…');

    const resultado = await API.auth.registroAlumno(datos);

    listo(alEnviar);

    if (!resultado.ok) {
      UI.mostrarMensaje(avisoRegistro, API.mensaje(resultado), 'error');
      return;
    }

    const usuarioCreado = datos.usuario;

    UI.mostrarMensaje(
      avisoRegistro,
      '¡Listo! Tu cuenta de alumno ya está activa. Te llevamos al ingreso…',
      'ok'
    );
    UI.avisar('Cuenta creada. Ya podés ingresar.', 'ok');

    window.setTimeout(function () {
      formAlumno.reset();
      prepararFormularios();
      loginUsuario.value = usuarioCreado;
      activarVista('login');
      UI.mostrarMensaje(
        avisoLogin,
        'Tu cuenta está creada. Ingresá con tu contraseña.',
        'ok'
      );
      loginClave.focus();
    }, 900);
  });

  /* ---------------------------------------------------------
     Alta de profesor (queda pendiente de aprobación)
     --------------------------------------------------------- */

  formProfesor.addEventListener('submit', async function (evento) {
    evento.preventDefault();
    UI.ocultarMensaje(avisoRegistro);

    if (!formProfesor.reportValidity()) {
      return;
    }

    const datos = {
      dni: valor('pr-dni'),
      nombre: valor('pr-nombre'),
      apellido: valor('pr-apellido'),
      email: valor('pr-email'),
      usuario: valor('pr-usuario'),
      contrasenia: document.getElementById('pr-clave').value
    };

    enviando(prEnviar, 'Enviando solicitud…');

    const resultado = await API.auth.registroProfesor(datos);

    listo(prEnviar);

    if (!resultado.ok) {
      UI.mostrarMensaje(avisoRegistro, API.mensaje(resultado), 'error');
      return;
    }

    UI.mostrarMensaje(
      avisoRegistro,
      resultado.data && resultado.data.mensaje
        ? resultado.data.mensaje
        : 'Registro recibido. Un administrador debe habilitar la cuenta.',
      'ok'
    );
    UI.avisar('Solicitud enviada. Falta la habilitación del administrador.', 'ok');
    formProfesor.reset();
  });

  /* ---------------------------------------------------------
     Arranque
     --------------------------------------------------------- */

  prepararFormularios();
  leerMotivo();

  const parametros = new URLSearchParams(location.search);

  if (location.hash === '#registro' || parametros.get('modo') === 'registro') {
    activarVista('registro');
  }

  saltarSiHaySesion();
})();
