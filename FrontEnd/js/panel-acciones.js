/* =========================================================
   Tien Long Hu - Panel: acciones
   ---------------------------------------------------------
   Todo lo que se dispara con data-accion en panel.html:
   perfil, alta/edición/baja de alumnos, ficha 360, tomar
   lista, declarar/registrar/confirmar pagos, inscripciones
   a exámenes y gestión de sedes. Los datos ya cargados viven
   en window.Panel.
   ========================================================= */

(function () {
  'use strict';

  const $ = UI.qs;
  const MESES = [
    'ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN',
    'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'
  ];

  /* ---------------------------------------------------------
     Helpers generales
     --------------------------------------------------------- */

  function panel() {
    return window.Panel || null;
  }

  function sesion() {
    const p = panel();
    return p ? p.usuario() : null;
  }

  function esAdmin() {
    const usuario = sesion();
    return Boolean(usuario) && usuario.rol === 'ADMIN';
  }

  function esStaff() {
    const usuario = sesion();
    return Boolean(usuario) && (usuario.rol === 'ADMIN' || usuario.rol === 'PROFESOR');
  }

  function listaDe(res, clave) {
    if (!res || !res.ok || !res.data) {
      return [];
    }

    if (Array.isArray(res.data)) {
      return res.data;
    }

    return Array.isArray(res.data[clave]) ? res.data[clave] : [];
  }

  function nombreCompleto(persona) {
    if (!persona) {
      return '';
    }

    return [persona.nombre, persona.apellido].filter(Boolean).join(' ');
  }

  function esc(valor) {
    return UI.escapar(UI.texto(valor, ''));
  }

  function escDato(valor) {
    return UI.escapar(UI.texto(valor));
  }

  function periodo(cuota) {
    const mes = Number(cuota.periodo_mes);
    const anio = cuota.periodo_anio;

    if (!mes || !anio) {
      return 'Cuota';
    }

    return MESES[mes - 1] + ' ' + anio;
  }

  function alumnoPorId(alumnoId) {
    const p = panel();

    if (!p) {
      return null;
    }

    return p.alumnos().filter(function (alumno) {
      return Number(alumno.alumno_id) === Number(alumnoId);
    })[0] || null;
  }

  function opcionesCentros() {
    const p = panel();

    if (!p) {
      return [];
    }

    return p.centros().map(function (centro) {
      return {
        valor: centro.centro_id,
        texto:
          centro.nombre +
          (centro.activo === 0 || centro.activo === false ? ' (inactiva)' : '')
      };
    });
  }

  function opcionesProfesores(incluirInactivos) {
    const p = panel();

    if (!p) {
      return [];
    }

    return p
      .profesores()
      .filter(function (profesor) {
        return incluirInactivos || Boolean(profesor.profesor_activo);
      })
      .map(function (profesor) {
        return {
          valor: profesor.profesor_id,
          texto:
            nombreCompleto(profesor) +
            (profesor.profesor_activo ? '' : ' (inactivo)')
        };
      });
  }

  function esCuotaAbierta(cuota) {
    return ['PENDIENTE', 'VENCIDA'].indexOf(
      String((cuota && cuota.estado) || '').toUpperCase()
    ) !== -1;
  }

  function opcionesCuotas(cuotas) {
    return cuotas.map(function (cuota) {
      return {
        valor: cuota.cuota_id,
        texto:
          periodo(cuota) +
          ' · ' +
          UI.moneda(cuota.monto) +
          ' · ' +
          String(cuota.estado || '').toUpperCase()
      };
    });
  }

  function opcionesInscripciones(inscripciones) {
    return inscripciones.map(function (inscripcion) {
      return {
        valor: inscripcion.inscripcion_id,
        texto:
          (inscripcion.titulo || 'Examen') +
          ' · ' +
          UI.formatearFecha(inscripcion.fecha_examen)
      };
    });
  }

  function irALoginSiCaduco(res) {
    if (API.sesionInvalida(res)) {
      API.limpiarSesion();
      API.irALogin('expirado');
      return true;
    }

    return false;
  }

  function mostrarError(res) {
    if (irALoginSiCaduco(res)) {
      return;
    }

    PanelUI.aviso(API.mensaje(res), 'error');
  }

  function avisarErrorDesdePanel(res) {
    if (irALoginSiCaduco(res)) {
      return;
    }

    const p = panel();

    if (p) {
      p.mostrarAlerta(API.mensaje(res), 'error');
    }

    UI.avisar(API.mensaje(res), 'error');
  }

  function refrescar() {
    const p = panel();

    if (!p) {
      return Promise.resolve(false);
    }

    return p.recargar(true);
  }

  function requiereStaff() {
    if (esStaff()) {
      return true;
    }

    UI.avisar('Esta acción es solo para el equipo de la escuela.', 'aviso');
    return false;
  }

  function requiereAdmin() {
    if (esAdmin()) {
      return true;
    }

    UI.avisar('Solo la administración puede gestionar las sedes.', 'aviso');
    return false;
  }

  /* ---------------------------------------------------------
     Perfil
     --------------------------------------------------------- */

  function avatarHtml(perfil, clase) {
    const iniciales = UI.iniciales(perfil.nombre, perfil.apellido);

    if (perfil.avatar) {
      return (
        '<span class="' + clase + ' con-foto">' +
        '<img src="' + esc(perfil.avatar) + '" alt="" />' +
        '</span>'
      );
    }

    return '<span class="' + clase + '">' + esc(iniciales) + '</span>';
  }

  async function cargarPerfil() {
    const p = panel();

    if (!p) {
      return null;
    }

    let perfil = p.perfil();

    if (perfil && perfil.usuario_id) {
      return perfil;
    }

    const res = await API.get('/api/perfil');

    if (!res.ok) {
      avisarErrorDesdePanel(res);
      return null;
    }

    return (res.data && res.data.perfil) || null;
  }

  async function abrirPerfil() {
    if (!sesion()) {
      return;
    }

    const perfil = await cargarPerfil();

    if (!perfil) {
      return;
    }

    const cuerpo =
      '<form id="form-perfil" class="panel-form">' +
      PanelUI.bloqueAlerta() +
      '<div class="perfil-avatar">' +
      avatarHtml(perfil, 'perfil-avatar-foto') +
      '<div class="perfil-avatar-copy">' +
      '<strong>Foto de perfil</strong>' +
      '<p class="pista">JPG o PNG. Se sube a Cloudinary y se ve en el header.</p>' +
      '<div class="perfil-avatar-acciones">' +
      '<input type="file" id="perfil-archivo" accept="image/*" />' +
      '<button type="button" class="panel-btn panel-btn-chico panel-btn-secundario" id="btn-subir-avatar">' +
      'Subir foto</button>' +
      '</div>' +
      '</div>' +
      '</div>' +
      PanelUI.seccion(
        'Datos personales',
        PanelUI.fila(
          PanelUI.campo({
            id: 'perfil-nombre',
            label: 'Nombre',
            valor: perfil.nombre,
            requerido: true,
            autocomplete: 'given-name'
          }),
          PanelUI.campo({
            id: 'perfil-apellido',
            label: 'Apellido',
            valor: perfil.apellido,
            requerido: true,
            autocomplete: 'family-name'
          }),
          PanelUI.campo({
            id: 'perfil-email',
            label: 'Email',
            tipo: 'email',
            valor: perfil.email,
            requerido: true,
            autocomplete: 'email'
          }),
          PanelUI.campo({
            id: 'perfil-telefono',
            label: 'Teléfono',
            tipo: 'tel',
            valor: perfil.telefono,
            autocomplete: 'tel'
          }),
          PanelUI.campo({
            id: 'perfil-nacimiento',
            label: 'Nacimiento',
            tipo: 'date',
            valor: PanelUI.fechaInput(perfil.fecha_nacimiento)
          }),
          PanelUI.campo({
            id: 'perfil-emergencia',
            label: 'Contacto de emergencia',
            valor: perfil.contacto_emergencia,
            placeholder: 'Nombre y teléfono',
            ancho: true
          })
        )
      ) +
      '</form>' +
      PanelUI.seccion(
        'Contraseña',
        '<form id="form-clave" class="panel-form">' +
          '<p class="pista">Mínimo 8 caracteres. La sesión actual sigue abierta.</p>' +
          PanelUI.fila(
            PanelUI.campo({
              id: 'clave-actual',
              label: 'Contraseña actual',
              tipo: 'password',
              requerido: true,
              autocomplete: 'current-password'
            }),
            PanelUI.campo({
              id: 'clave-nueva',
              label: 'Nueva contraseña',
              tipo: 'password',
              requerido: true,
              autocomplete: 'new-password'
            }),
            PanelUI.campo({
              id: 'clave-repetir',
              label: 'Repetir la nueva',
              tipo: 'password',
              requerido: true,
              autocomplete: 'new-password'
            })
          ) +
          '<div class="form-acciones">' +
          '<button type="submit" class="panel-btn panel-btn-chico panel-btn-secundario">' +
          'Cambiar contraseña</button>' +
          '</div>' +
          '</form>'
      );

    PanelUI.abrirModal({
      kicker: 'Mi cuenta',
      titulo: 'Mi perfil',
      ancho: true,
      cuerpo: cuerpo,
      pie:
        PanelUI.boton({
          texto: 'Cerrar',
          accion: 'cerrar-modal'
        }) +
        '<button type="submit" class="panel-btn panel-btn-primario" form="form-perfil" id="btn-perfil-guardar">' +
        'Guardar cambios</button>',
      alAbrir: function () {
        const form = $('#form-perfil');
        const formClave = $('#form-clave');

        $('#btn-subir-avatar').addEventListener('click', async function () {
          const boton = $('#btn-subir-avatar');
          const archivo = $('#perfil-archivo').files[0];

          PanelUI.limpiarAviso();

          if (!archivo) {
            PanelUI.aviso('Elegí una imagen antes de subirla.', 'aviso');
            return;
          }

          if (archivo.type && archivo.type.indexOf('image/') !== 0) {
            PanelUI.aviso('El archivo tiene que ser una imagen.', 'aviso');
            return;
          }

          PanelUI.ocupado(boton, 'Subiendo…');

          const res = await API.subirAvatar(
            archivo,
            esAdmin() ? perfil.persona_id : null
          );

          PanelUI.libre(boton);

          if (!res.ok) {
            mostrarError(res);
            return;
          }

          const url = res.data && res.data.avatar_url;

          UI.avisar('Foto actualizada.', 'ok');
          await refrescar();

          const nueva = await cargarPerfil();
          const foto = $('.perfil-avatar-foto');

          if (nueva && foto) {
            foto.outerHTML = avatarHtml(nueva, 'perfil-avatar-foto');
          } else if (url && foto) {
            foto.classList.add('con-foto');
            foto.innerHTML = '<img src="' + esc(url) + '" alt="" />';
          }

          $('#perfil-archivo').value = '';
        });

        form.addEventListener('submit', async function (evento) {
          evento.preventDefault();
          PanelUI.limpiarAviso();

          if (!form.checkValidity()) {
            form.reportValidity();
            return;
          }

          const boton = $('#btn-perfil-guardar');
          const telefono = PanelUI.valor('perfil-telefono');
          const emergencia = PanelUI.valor('perfil-emergencia');
          const nacimiento = PanelUI.valor('perfil-nacimiento');

          PanelUI.ocupado(boton);

          const res = await API.put('/api/perfil', {
            nombre: PanelUI.valor('perfil-nombre'),
            apellido: PanelUI.valor('perfil-apellido'),
            email: PanelUI.valor('perfil-email'),
            telefono: telefono || null,
            fecha_nacimiento: nacimiento || null,
            contacto_emergencia: emergencia || null
          });

          PanelUI.libre(boton);

          if (!res.ok) {
            mostrarError(res);
            return;
          }

          UI.avisar('Perfil actualizado.', 'ok');
          await refrescar();
          PanelUI.cerrarModal();
        });

        formClave.addEventListener('submit', async function (evento) {
          evento.preventDefault();
          PanelUI.limpiarAviso();

          const actual = PanelUI.valor('clave-actual');
          const nueva = PanelUI.valor('clave-nueva');
          const repetir = PanelUI.valor('clave-repetir');

          if (!actual || !nueva) {
            PanelUI.aviso('Completá la contraseña actual y la nueva.', 'aviso');
            return;
          }

          if (nueva.length < 8) {
            PanelUI.aviso('La nueva contraseña debe tener al menos 8 caracteres.', 'aviso');
            return;
          }

          if (nueva !== repetir) {
            PanelUI.aviso('La nueva contraseña y su repetición no coinciden.', 'aviso');
            return;
          }

          const boton = $('button[type="submit"]', formClave);
          PanelUI.ocupado(boton, 'Cambiando…');

          const res = await API.put('/api/perfil/password', {
            contrasenia_actual: actual,
            contrasenia_nueva: nueva
          });

          PanelUI.libre(boton);

          if (!res.ok) {
            mostrarError(res);
            return;
          }

          formClave.reset();
          UI.avisar('Contraseña actualizada.', 'ok');
        });
      }
    });
  }

  /* ---------------------------------------------------------
     Alta y edición de alumnos
     --------------------------------------------------------- */

  async function asegurarCatalogos() {
    const p = panel();

    if (!p) {
      return false;
    }

    const faltantes = [];

    if (!p.centros().length) {
      faltantes.push(
        API.get('/api/centros?todos=true').then(function (res) {
          return { clave: 'centros', res: res };
        })
      );
    }

    if (!p.profesores().length) {
      faltantes.push(
        API.get('/api/profesores?todos=true').then(function (res) {
          return { clave: 'profesores', res: res };
        })
      );
    }

    if (!faltantes.length) {
      return true;
    }

    const respuestas = await Promise.all(faltantes);

    const nuevos = {};

    respuestas.forEach(function (item) {
      if (!item.res || !item.res.ok) {
        if (item.res) {
          UI.avisar(API.mensaje(item.res), 'error');
        }
        return;
      }

      nuevos[item.clave] = Array.isArray(item.res.data)
        ? item.res.data
        : item.res.data[item.clave] || [];
    });

    p.fijarCatalogos(nuevos.centros, nuevos.profesores);

    return opcionesCentros().length > 0 && opcionesProfesores(false).length > 0;
  }

  function formularioAlumno(alumno) {
    const esNuevo = !alumno;
    const centros = opcionesCentros();
    const profesores = opcionesProfesores(!esNuevo);

    const titulo = esNuevo ? 'Nuevo alumno' : 'Editar alumno';

    let campos =
      PanelUI.fila(
        PanelUI.campo({
          id: 'al-dni',
          label: 'DNI',
          valor: alumno ? alumno.dni : '',
          requerido: true,
          inputmode: 'numeric',
          autocomplete: 'off'
        }),
        PanelUI.campo({
          id: 'al-nombre',
          label: 'Nombre',
          valor: alumno ? alumno.nombre : '',
          requerido: true,
          autocomplete: 'given-name'
        }),
        PanelUI.campo({
          id: 'al-apellido',
          label: 'Apellido',
          valor: alumno ? alumno.apellido : '',
          requerido: true,
          autocomplete: 'family-name'
        }),
        PanelUI.campo({
          id: 'al-email',
          label: 'Email',
          tipo: 'email',
          valor: alumno ? alumno.email : '',
          requerido: true,
          autocomplete: 'email'
        }),
        PanelUI.campo({
          id: 'al-telefono',
          label: 'Teléfono',
          tipo: 'tel',
          valor: alumno ? alumno.telefono : '',
          autocomplete: 'tel'
        }),
        PanelUI.campo({
          id: 'al-nacimiento',
          label: 'Nacimiento',
          tipo: 'date',
          valor: PanelUI.fechaInput(alumno && alumno.fecha_nacimiento)
        }),
        PanelUI.campo({
          id: 'al-emergencia',
          label: 'Contacto de emergencia',
          valor: alumno ? alumno.contacto_emergencia : '',
          placeholder: 'Nombre y teléfono',
          ancho: true
        })
      ) +
      PanelUI.seccion(
        'Acceso y cursada',
        PanelUI.fila(
          PanelUI.campo({
            id: 'al-usuario',
            label: 'Usuario',
            valor: alumno ? alumno.usuario : '',
            requerido: true,
            autocomplete: 'off',
            pista: esNuevo
              ? 'Con este usuario el alumno entra al panel.'
              : 'Cambiar el usuario también cambia el login.'
          }),
          esNuevo
            ? PanelUI.campo({
                id: 'al-clave',
                label: 'Contraseña inicial',
                tipo: 'password',
                requerido: true,
                autocomplete: 'new-password',
                pista: 'Mínimo 8 caracteres.'
              })
            : PanelUI.campo({
                id: 'al-estado',
                label: 'Estado',
                tipo: 'select',
                valor: alumno.estado,
                vacio: false,
                opciones: [
                  { valor: 'ACTIVO', texto: 'Activo' },
                  { valor: 'PAUSADO', texto: 'Pausado' },
                  { valor: 'INACTIVO', texto: 'Inactivo' }
                ],
                requerido: true
              }),
          PanelUI.campo({
            id: 'al-centro',
            label: 'Sede',
            tipo: 'select',
            valor: alumno ? alumno.centro_id : '',
            opciones: centros,
            requerido: true,
            vacio: 'Elegí una sede'
          }),
          PanelUI.campo({
            id: 'al-profesor',
            label: 'Profesor',
            tipo: 'select',
            valor: alumno ? alumno.profesor_id : '',
            opciones: profesores,
            requerido: true,
            vacio: 'Elegí un profesor'
          }),
          PanelUI.campo({
            id: 'al-inicio',
            label: 'Inicio',
            tipo: 'date',
            valor: alumno
              ? PanelUI.fechaInput(alumno.fecha_de_inicio || alumno.fecha_alta)
              : PanelUI.hoyInput(),
            requerido: true
          })
        )
      );

    if (!esNuevo) {
      campos +=
        '<p class="pista">La contraseña del alumno se cambia desde su propio perfil.</p>';
    }

    const botones = esNuevo
      ? PanelUI.boton({ texto: 'Cancelar', accion: 'cerrar-modal' }) +
        '<button type="submit" class="panel-btn panel-btn-primario" form="form-alumno" id="btn-alumno-guardar">' +
        'Crear alumno</button>'
      : PanelUI.boton({
          texto: 'Dar de baja',
          tipo: 'peligro',
          accion: 'baja-alumno',
          idDato: alumno.alumno_id
        }) +
        PanelUI.boton({ texto: 'Cancelar', accion: 'cerrar-modal' }) +
        '<button type="submit" class="panel-btn panel-btn-primario" form="form-alumno" id="btn-alumno-guardar">' +
        'Guardar cambios</button>';

    return {
      titulo: titulo,
      cuerpo:
        '<form id="form-alumno" class="panel-form" data-alumno="' +
        (alumno ? Number(alumno.alumno_id) : '') +
        '">' +
        PanelUI.bloqueAlerta() +
        campos +
        '</form>',
      pie: botones,
      alumno: alumno || null
    };
  }

  async function abrirFormularioAlumno(alumnoId) {
    if (!requiereStaff()) {
      return;
    }

    const listo = await asegurarCatalogos();

    if (!listo) {
      UI.avisar('Faltan sedes o profesores cargados para dar de alta un alumno.', 'aviso');
      return;
    }

    const alumno = alumnoId ? alumnoPorId(alumnoId) : null;
    const armado = formularioAlumno(alumno);
    const esNuevo = !alumno;

    PanelUI.abrirModal({
      kicker: 'Alumnos',
      titulo: armado.titulo,
      ancho: true,
      cuerpo: armado.cuerpo,
      pie: armado.pie,
      alAbrir: function () {
        const form = $('#form-alumno');

        form.addEventListener('submit', async function (evento) {
          evento.preventDefault();
          PanelUI.limpiarAviso();

          if (!form.checkValidity()) {
            form.reportValidity();
            return;
          }

          const boton = $('#btn-alumno-guardar');
          const nacimiento = PanelUI.valor('al-nacimiento');
          const telefono = PanelUI.valor('al-telefono');
          const emergencia = PanelUI.valor('al-emergencia');

          const datos = {
            dni: PanelUI.valor('al-dni'),
            nombre: PanelUI.valor('al-nombre'),
            apellido: PanelUI.valor('al-apellido'),
            email: PanelUI.valor('al-email'),
            telefono: telefono || null,
            fecha_nacimiento: nacimiento || null,
            contacto_emergencia: emergencia || null,
            usuario: PanelUI.valor('al-usuario'),
            centro_id: Number(PanelUI.valor('al-centro')),
            profesor_id: Number(PanelUI.valor('al-profesor')),
            fecha_de_inicio: PanelUI.valor('al-inicio')
          };

          let res;

          PanelUI.ocupado(boton);

          if (esNuevo) {
            datos.contrasenia = PanelUI.valor('al-clave');
            res = await API.post('/api/alumnos', datos);
          } else {
            datos.estado = PanelUI.valor('al-estado');
            datos.avatar = alumno && alumno.avatar ? alumno.avatar : null;
            res = await API.put('/api/alumnos/' + Number(alumno.alumno_id), datos);
          }

          PanelUI.libre(boton);

          if (!res.ok) {
            mostrarError(res);
            return;
          }

          UI.avisar(
            esNuevo ? 'Alumno creado.' : 'Alumno actualizado.',
            'ok'
          );
          PanelUI.cerrarModal();
          await refrescar();
        });
      }
    });
  }

  async function darDeBajaAlumno(alumnoId) {
    if (!requiereStaff()) {
      return;
    }

    const alumno = alumnoPorId(alumnoId);

    if (!alumno) {
      return;
    }

    const confirmado = await PanelUI.confirmar({
      titulo: 'Dar de baja al alumno',
      mensaje:
        'El alumno ' +
        nombreCompleto(alumno) +
        ' quedará INACTIVO y su usuario se desactiva. No se borran sus datos históricos.',
      textoOk: 'Dar de baja'
    });

    if (!confirmado) {
      return;
    }

    const res = await API.del('/api/alumnos/' + Number(alumnoId));

    if (!res.ok) {
      PanelUI.cerrarModal();
      avisarErrorDesdePanel(res);
      return;
    }

    PanelUI.cerrarModal();
    UI.avisar('Alumno dado de baja.', 'ok');
    await refrescar();
  }

  /* ---------------------------------------------------------
     Ficha 360
     --------------------------------------------------------- */

  function datoFicha(etiqueta, valor) {
    return (
      '<div class="ficha-dato">' +
      '<span>' + esc(etiqueta) + '</span>' +
      '<strong>' + escDato(valor) + '</strong>' +
      '</div>'
    );
  }

  function bloqueFicha(titulo, contenido) {
    return (
      '<section class="ficha-bloque">' +
      '<h3>' + esc(titulo) + '</h3>' +
      contenido +
      '</section>'
    );
  }

  function filaFicha(izquierda, derecha, estado) {
    return (
      '<div class="ficha-fila">' +
      '<span class="ficha-fila-principal">' + izquierda + '</span>' +
      '<span class="ficha-fila-lado">' +
      (estado || '') +
      (derecha ? '<b>' + derecha + '</b>' : '') +
      '</span>' +
      '</div>'
    );
  }

  function sinDatos(texto) {
    return '<p class="ficha-vacio">' + esc(texto) + '</p>';
  }

  async function abrirFicha(alumnoId) {
    if (!requiereStaff()) {
      return;
    }

    let alumno = alumnoPorId(alumnoId);

    PanelUI.abrirDrawer({
      kicker: 'Ficha del alumno',
      titulo: 'Cargando…',
      cuerpo: UI.cargando(4)
    });

    const pedidos = [
      API.get('/api/asistencias/alumno/' + Number(alumnoId)),
      API.get('/api/cuotas/alumno/' + Number(alumnoId)),
      API.get('/api/pagos/alumno/' + Number(alumnoId)),
      API.get('/api/graduaciones/alumno/' + Number(alumnoId)),
      API.get('/api/examenes/mis-inscripciones?alumno_id=' + Number(alumnoId))
    ];

    const respuestas = await Promise.allSettled(pedidos);

    if (respuestas.some(function (r) {
      return r.status === 'fulfilled' && irALoginSiCaduco(r.value);
    })) {
      return;
    }

    const asistencias = respuestas[0].status === 'fulfilled'
      ? listaDe(respuestas[0].value, 'asistencias')
      : [];
    const cuotas = respuestas[1].status === 'fulfilled'
      ? listaDe(respuestas[1].value, 'cuotas')
      : [];
    const pagos = respuestas[2].status === 'fulfilled'
      ? listaDe(respuestas[2].value, 'pagos')
      : [];
    const graduaciones = respuestas[3].status === 'fulfilled'
      ? listaDe(respuestas[3].value, 'graduaciones')
      : [];
    const inscripciones = respuestas[4].status === 'fulfilled'
      ? listaDe(respuestas[4].value, 'inscripciones')
      : [];

    if (!alumno) {
      const res = await API.get('/api/alumnos/' + Number(alumnoId));

      if (!res.ok) {
        PanelUI.cerrarDrawer();
        avisarErrorDesdePanel(res);
        return;
      }

      alumno = res.data && res.data.alumno;
    }

    if (!alumno) {
      PanelUI.cerrarDrawer();
      UI.avisar('No encontramos al alumno.', 'error');
      return;
    }

    const presentes = asistencias.filter(function (asistencia) {
      return Boolean(asistencia.presente);
    }).length;

    const abiertas = cuotas.filter(function (cuota) {
      return ['PENDIENTE', 'VENCIDA'].indexOf(
        String(cuota.estado || '').toUpperCase()
      ) !== -1;
    });

    const confirmados = pagos.filter(function (pago) {
      return String(pago.estado || '').toUpperCase() === 'CONFIRMADO';
    });

    const encabezado =
      '<div class="ficha-encabezado">' +
      avatarHtml(alumno, 'ficha-avatar') +
      '<div class="ficha-encabezado-copy">' +
      '<h3>' + esc(nombreCompleto(alumno)) + '</h3>' +
      '<p>' +
      UI.insignia(alumno.estado) +
      (alumno.usuario ? ' <span class="pista">@' + esc(alumno.usuario) + '</span>' : '') +
      '</p>' +
      '</div>' +
      '</div>' +
      '<div class="ficha-acciones">' +
      '<button type="button" class="panel-btn panel-btn-chico panel-btn-secundario" ' +
      'data-accion="editar-alumno" data-id="' + Number(alumno.alumno_id) + '">Editar</button>' +
      '<button type="button" class="panel-btn panel-btn-chico panel-btn-primario" ' +
      'data-accion="registrar-pago" data-id="' + Number(alumno.alumno_id) + '">Registrar pago</button>' +
      '</div>';

    const resumen =
      '<div class="ficha-resumen">' +
      '<div><b>' + asistencias.length + '</b><span>Clases</span></div>' +
      '<div><b>' + (asistencias.length ? Math.round((presentes / asistencias.length) * 100) + '%' : '—') +
      '</b><span>Presente</span></div>' +
      '<div><b>' + abiertas.length + '</b><span>Cuotas abiertas</span></div>' +
      '<div><b>' + UI.moneda(confirmados.reduce(function (total, pago) {
        return total + (Number(pago.monto) || 0);
      }, 0)) + '</b><span>Pagado</span></div>' +
      '</div>';

    const datos =
      '<div class="ficha-datos">' +
      datoFicha('Documento', alumno.dni) +
      datoFicha('Email', alumno.email) +
      datoFicha('Teléfono', alumno.telefono) +
      datoFicha('Nacimiento', UI.formatearFecha(alumno.fecha_nacimiento)) +
      datoFicha('Emergencia', alumno.contacto_emergencia) +
      datoFicha('Sede', alumno.centro_nombre) +
      datoFicha('Profesor', nombreCompleto({
        nombre: alumno.profesor_nombre,
        apellido: alumno.profesor_apellido
      })) +
      datoFicha('Inicio', UI.formatearFecha(alumno.fecha_de_inicio || alumno.fecha_alta)) +
      '</div>';

    const bloqueAsistencias = asistencias.length
      ? asistencias.slice(0, 8).map(function (asistencia) {
          return filaFicha(
            esc(UI.formatearFecha(asistencia.fecha)) +
              (asistencia.observacion
                ? ' <span class="pista">' + esc(asistencia.observacion) + '</span>'
                : ''),
            '',
            UI.insignia(asistencia.presente ? 'PRESENTE' : 'AUSENTE')
          );
        }).join('')
      : sinDatos('Sin asistencias registradas.');

    const bloqueCuotas = cuotas.length
      ? cuotas.slice(0, 6).map(function (cuota) {
          return filaFicha(
            esc(periodo(cuota)),
            UI.moneda(cuota.monto),
            UI.insignia(cuota.estado)
          );
        }).join('')
      : sinDatos('Sin cuotas generadas.');

    const bloquePagos = pagos.length
      ? pagos.slice(0, 6).map(function (pago) {
          return filaFicha(
            esc(UI.formatearFecha(pago.fecha_registro)) +
              ' · ' +
              esc(pago.tipo_concepto || 'Pago'),
            UI.moneda(pago.monto),
            UI.insignia(pago.estado)
          );
        }).join('')
      : sinDatos('Sin pagos registrados.');

    const bloqueGraduaciones = graduaciones.length
      ? graduaciones.map(function (graduacion) {
          return filaFicha(
            esc(graduacion.grado || 'Grado'),
            UI.formatearFecha(graduacion.fecha)
          );
        }).join('')
      : sinDatos('Todavía sin graduaciones.');

    const bloqueInscripciones = inscripciones.length
      ? inscripciones.map(function (inscripcion) {
          return filaFicha(
            esc(inscripcion.titulo || 'Examen') +
              ' <span class="pista">' +
              esc(UI.formatearFecha(inscripcion.fecha_examen)) +
              '</span>',
            UI.moneda(inscripcion.monto),
            UI.insignia(inscripcion.estado_pago || 'INSCRIPTO')
          );
        }).join('')
      : sinDatos('Sin inscripciones a exámenes.');

    PanelUI.abrirDrawer({
      kicker: 'Ficha 360',
      titulo: nombreCompleto(alumno) || 'Alumno',
      cuerpo:
        encabezado +
        resumen +
        bloqueFicha('Datos', datos) +
        bloqueFicha('Asistencias', bloqueAsistencias) +
        bloqueFicha('Cuotas', bloqueCuotas) +
        bloqueFicha('Pagos', bloquePagos) +
        bloqueFicha('Graduaciones', bloqueGraduaciones) +
        bloqueFicha('Exámenes', bloqueInscripciones)
    });
  }

  /* ---------------------------------------------------------
     Tomar lista
     --------------------------------------------------------- */

  function filaLista(alumno, presente) {
    return (
      '<label class="lista-asistencia">' +
      '<input type="checkbox" data-alumno="' + Number(alumno.alumno_id) + '"' +
      (presente ? ' checked' : '') +
      ' />' +
      '<span class="lista-asistencia-copy">' +
      '<strong>' + esc(nombreCompleto(alumno)) + '</strong>' +
      '<small>' + esc(alumno.dni || 'Sin DNI') + '</small>' +
      '</span>' +
      '</label>'
    );
  }

  async function abrirTomarLista() {
    if (!requiereStaff()) {
      return;
    }

    const p = panel();
    const activos = p.alumnos().filter(function (alumno) {
      return String(alumno.estado || '').toUpperCase() === 'ACTIVO';
    });

    if (!activos.length) {
      UI.avisar('No hay alumnos activos para tomar lista.', 'aviso');
      return;
    }

    const res = await API.get('/api/asistencias');
    const existentes = listaDe(res, 'asistencias');
    const centros = p.centros();
    const sedeInicial = centros.length === 1 ? String(centros[0].centro_id) : '';

    PanelUI.abrirModal({
      kicker: 'Asistencias',
      titulo: 'Tomar lista',
      ancho: true,
      cuerpo:
        '<form id="form-lista" class="panel-form">' +
        PanelUI.bloqueAlerta() +
        '<div class="form-grid">' +
        PanelUI.campo({
          id: 'lista-fecha',
          label: 'Fecha de la clase',
          tipo: 'date',
          valor: PanelUI.hoyInput(),
          requerido: true
        }) +
        PanelUI.campo({
          id: 'lista-centro',
          label: 'Sede',
          tipo: 'select',
          valor: sedeInicial,
          vacio: 'Todas las sedes',
          opciones: centros.map(function (centro) {
            return { valor: centro.centro_id, texto: centro.nombre };
          })
        }) +
        '</div>' +
        '<div class="lista-asistencia-cabeza">' +
        '<span>Presentes</span>' +
        '<div class="panel-acciones-fila">' +
        '<button type="button" class="panel-btn panel-btn-mini" data-accion="lista-todos" data-modo="presente">Todos</button>' +
        '<button type="button" class="panel-btn panel-btn-mini" data-accion="lista-todos" data-modo="ausente">Ninguno</button>' +
        '</div>' +
        '</div>' +
        '<div class="lista-asistencias" id="lista-alumnos"></div>' +
        '<div class="panel-form-pie">' +
        PanelUI.campo({
          id: 'lista-observacion',
          label: 'Observación de la clase',
          tipo: 'textarea',
          filas: 2,
          placeholder: 'Opcional: tema, feriado, novedad…'
        }) +
        '</div>' +
        '</form>',
      pie:
        PanelUI.boton({ texto: 'Cancelar', accion: 'cerrar-modal' }) +
        '<button type="submit" class="panel-btn panel-btn-primario" form="form-lista" id="btn-lista-guardar">' +
        'Guardar asistencias</button>',
      alAbrir: function () {
        const form = $('#form-lista');
        const contenedor = $('#lista-alumnos');
        const selectSede = $('#lista-centro');

        function pintarAlumnos() {
          const centro = selectSede.value;
          const filtrados = activos.filter(function (alumno) {
            return !centro || String(alumno.centro_id) === String(centro);
          });

          if (!filtrados.length) {
            contenedor.innerHTML = UI.vacio(
              'Sin alumnos en esta sede',
              'Probá con otra sede o revisá el alta de alumnos.'
            );
            return;
          }

          contenedor.innerHTML = filtrados
            .map(function (alumno) {
              return filaLista(alumno, true);
            })
            .join('');
        }

        selectSede.addEventListener('change', pintarAlumnos);
        pintarAlumnos();

        form.addEventListener('submit', async function (evento) {
          evento.preventDefault();
          PanelUI.limpiarAviso();

          const fecha = PanelUI.valor('lista-fecha');
          const observacion = PanelUI.valor('lista-observacion');
          const marcas = UI.qsa('#lista-alumnos input[type="checkbox"]');

          if (!fecha) {
            PanelUI.aviso('Elegí la fecha de la clase.', 'aviso');
            return;
          }

          if (!marcas.length) {
            PanelUI.aviso('No hay alumnos para registrar.', 'aviso');
            return;
          }

          const yaCargados = {};
          existentes.forEach(function (asistencia) {
            yaCargados[
              Number(asistencia.alumno_id) + '|' + PanelUI.fechaInput(asistencia.fecha)
            ] = true;
          });

          const seleccionados = marcas.map(function (marca) {
            const alumno = alumnoPorId(marca.getAttribute('data-alumno')) || {};
            return {
              alumno: alumno,
              presente: marca.checked
            };
          });

          const pendientes = [];
          let sinSede = 0;
          let repetidos = 0;

          seleccionados.forEach(function (item) {
            if (!item.alumno.centro_id) {
              sinSede += 1;
              return;
            }

            if (yaCargados[Number(item.alumno.alumno_id) + '|' + fecha]) {
              repetidos += 1;
              return;
            }

            pendientes.push(item);
          });

          if (!pendientes.length) {
            PanelUI.aviso(
              repetidos
                ? 'Todos los alumnos elegidos ya tienen asistencia en esa fecha.'
                : 'No se pudo preparar la lista: faltan sedes asignadas.',
              'aviso'
            );
            return;
          }

          const boton = $('#btn-lista-guardar');
          PanelUI.ocupado(boton, 'Guardando…');

          const respuestas = await Promise.allSettled(
            pendientes.map(function (item) {
              return API.post('/api/asistencias', {
                alumno_id: Number(item.alumno.alumno_id),
                centro_id: Number(item.alumno.centro_id),
                fecha: fecha,
                presente: item.presente,
                observacion: observacion || null
              });
            })
          );

          PanelUI.libre(boton);

          const guardadas = respuestas.filter(function (resultado) {
            return resultado.status === 'fulfilled' && resultado.value.ok;
          }).length;

          const errores = respuestas.filter(function (resultado) {
            return resultado.status === 'fulfilled' && !resultado.value.ok;
          });

          if (!guardadas) {
            const primero = errores[0];

            if (primero) {
              mostrarError(primero.value);
            } else {
              PanelUI.aviso('No se pudo guardar la lista.', 'error');
            }

            return;
          }

          let mensaje =
            guardadas +
            (guardadas === 1 ? ' asistencia guardada' : ' asistencias guardadas');

          if (repetidos) {
            mensaje += ' · ' + repetidos + ' ya estaban cargadas';
          }

          if (sinSede) {
            mensaje += ' · ' + sinSede + ' sin sede';
          }

          UI.avisar(mensaje + '.', errores.length ? 'aviso' : 'ok');
          PanelUI.cerrarModal();
          await refrescar();
        });
      }
    });
  }

  /* ---------------------------------------------------------
     Pagos
     --------------------------------------------------------- */

  function camposPago() {
    return (
      PanelUI.fila(
        PanelUI.campo({
          id: 'pago-tipo',
          label: 'Concepto',
          tipo: 'select',
          valor: 'CUOTA',
          vacio: false,
          opciones: [
            { valor: 'CUOTA', texto: 'Cuota mensual' },
            { valor: 'EXAMEN', texto: 'Examen' },
            { valor: 'MATRICULA', texto: 'Matrícula' },
            { valor: 'INSUMO', texto: 'Insumo' },
            { valor: 'OTRO', texto: 'Otro' }
          ],
          requerido: true
        }),
        PanelUI.campo({
          id: 'pago-metodo',
          label: 'Método',
          tipo: 'select',
          valor: 'EFECTIVO',
          vacio: false,
          opciones: [
            { valor: 'EFECTIVO', texto: 'Efectivo' },
            { valor: 'TRANSFERENCIA', texto: 'Transferencia' }
          ],
          requerido: true
        }),
        PanelUI.campo({
          id: 'pago-monto',
          label: 'Monto',
          tipo: 'number',
          min: '0',
          step: '0.01',
          requerido: true,
          inputmode: 'decimal',
          placeholder: '0'
        }),
        PanelUI.campo({
          id: 'pago-cuota',
          label: 'Cuota',
          tipo: 'select',
          vacio: 'Elegí una cuota',
          opciones: []
        }),
        PanelUI.campo({
          id: 'pago-inscripcion',
          label: 'Inscripción a examen',
          tipo: 'select',
          vacio: 'Elegí una inscripción',
          opciones: []
        }),
        PanelUI.campo({
          id: 'pago-descripcion',
          label: 'Descripción',
          tipo: 'textarea',
          filas: 2,
          placeholder: 'Opcional',
          ancho: true
        })
      )
    );
  }

  function conectarPago(form, cuotas, inscripciones, opciones) {
    const config = opciones || {};
    const tipo = $('#pago-tipo');
    const monto = $('#pago-monto');
    const cuota = $('#pago-cuota');
    const inscripcion = $('#pago-inscripcion');
    const pista = $('#pago-pista');

    const hayCuotas = cuotas.length > 0;
    const hayInscripciones = inscripciones.length > 0;
    const cuotaElegida = cuota.value;
    const inscripcionElegida = inscripcion.value;

    cuota.innerHTML =
      '<option value="">Elegí una cuota</option>' +
      opcionesCuotas(cuotas).map(function (opcion) {
        return '<option value="' + esc(opcion.valor) + '">' + esc(opcion.texto) + '</option>';
      }).join('');

    inscripcion.innerHTML =
      '<option value="">Elegí una inscripción</option>' +
      opcionesInscripciones(inscripciones).map(function (opcion) {
        return '<option value="' + esc(opcion.valor) + '">' + esc(opcion.texto) + '</option>';
      }).join('');

    const opcionCuota = tipo.querySelector('option[value="CUOTA"]');
    const opcionExamen = tipo.querySelector('option[value="EXAMEN"]');

    if (opcionCuota) {
      opcionCuota.disabled = !hayCuotas;
    }

    if (opcionExamen) {
      opcionExamen.disabled = !hayInscripciones;
    }

    /* Si el concepto elegido ya no tiene opciones, pasamos a Matrícula:
       así el formulario nunca queda bloqueado por un select vacío. */
    if (
      (tipo.value === 'CUOTA' && !hayCuotas) ||
      (tipo.value === 'EXAMEN' && !hayInscripciones)
    ) {
      tipo.value = 'MATRICULA';
    }

    if (
      cuotaElegida &&
      cuotas.some(function (item) {
        return String(item.cuota_id) === String(cuotaElegida);
      })
    ) {
      cuota.value = cuotaElegida;
    }

    if (
      inscripcionElegida &&
      inscripciones.some(function (item) {
        return String(item.inscripcion_id) === String(inscripcionElegida);
      })
    ) {
      inscripcion.value = inscripcionElegida;
    }

    function actualizarVisibilidad() {
      cuota.closest('.campo').hidden = tipo.value !== 'CUOTA';
      inscripcion.closest('.campo').hidden = tipo.value !== 'EXAMEN';
    }

    function actualizarPista() {
      if (!pista) {
        return;
      }

      let texto = config.pista || '';

      if (!texto) {
        const avisos = [];

        if (!hayCuotas) {
          avisos.push(
            'No hay cuotas abiertas: el concepto Cuota no está disponible.'
          );
        }

        if (!hayInscripciones) {
          avisos.push(
            'No hay inscripciones a examen activas: el concepto Examen no está disponible.'
          );
        }

        texto = avisos.join(' ');
      }

      pista.textContent = texto;
      pista.hidden = !texto;
    }

    function autocompletarMonto() {
      if (tipo.value === 'CUOTA' && cuota.value) {
        const elegida = cuotas.filter(function (item) {
          return String(item.cuota_id) === String(cuota.value);
        })[0];

        if (elegida) {
          monto.value = Number(elegida.monto);
        }
      }

      if (tipo.value === 'EXAMEN' && inscripcion.value) {
        const elegida = inscripciones.filter(function (item) {
          return String(item.inscripcion_id) === String(inscripcion.value);
        })[0];

        if (elegida) {
          monto.value = Number(elegida.monto);
        }
      }
    }

    function elegirUnica() {
      if (tipo.value === 'CUOTA' && cuota.options.length === 2) {
        cuota.selectedIndex = 1;
        autocompletarMonto();
      } else if (tipo.value === 'EXAMEN' && inscripcion.options.length === 2) {
        inscripcion.selectedIndex = 1;
        autocompletarMonto();
      }
    }

    /* Usamos onchange/oninput (no addEventListener) porque conectarPago
       puede ejecutarse varias veces al cambiar de alumno y no queremos
       acumular manejadores con datos viejos. */
    tipo.onchange = function () {
      if (tipo.value === 'CUOTA' && !hayCuotas) {
        tipo.value = 'MATRICULA';
      } else if (tipo.value === 'EXAMEN' && !hayInscripciones) {
        tipo.value = 'MATRICULA';
      }

      actualizarVisibilidad();
      elegirUnica();
    };

    cuota.onchange = autocompletarMonto;
    inscripcion.onchange = autocompletarMonto;

    actualizarVisibilidad();
    actualizarPista();
    elegirUnica();

    return { tipo: tipo, monto: monto, cuota: cuota, inscripcion: inscripcion };
  }

  function validarPago(controles) {
    const tipo = controles.tipo.value;
    const monto = Number(controles.monto.value);

    if (!monto || monto <= 0) {
      PanelUI.aviso('Ingresá un monto mayor a cero.', 'aviso');
      return false;
    }

    if (tipo === 'CUOTA' && !controles.cuota.value) {
      PanelUI.aviso(
        'Elegí una cuota de la lista. Si no aparece ninguna, la escuela todavía no generó cuotas: usá el concepto Matrícula.',
        'aviso'
      );
      return false;
    }

    if (tipo === 'EXAMEN' && !controles.inscripcion.value) {
      PanelUI.aviso(
        'Elegí una inscripción al examen. Si no aparece ninguna, primero inscribite a un examen.',
        'aviso'
      );
      return false;
    }

    return true;
  }

  function cuerpoPago() {
    const tipo = $('#pago-tipo').value;
    const datos = {
      tipo_concepto: tipo,
      monto: Number(PanelUI.valor('pago-monto')),
      metodo_pago: PanelUI.valor('pago-metodo'),
      descripcion: PanelUI.valor('pago-descripcion') || null
    };

    if (tipo === 'CUOTA') {
      datos.cuota_id = Number(PanelUI.valor('pago-cuota'));
    }

    if (tipo === 'EXAMEN') {
      datos.inscripcion_examen_id = Number(PanelUI.valor('pago-inscripcion'));
    }

    return datos;
  }

  async function abrirDeclararPago() {
    const p = panel();
    const usuario = sesion();

    if (!p || !usuario) {
      return;
    }

    if (!usuario.alumno_id) {
      UI.avisar('Tu usuario no está vinculado a una ficha de alumno.', 'aviso');
      return;
    }

    const perfil = await cargarPerfil();

    if (!perfil) {
      return;
    }

    if (!perfil.centro_id) {
      UI.avisar('Tu ficha no tiene una sede asignada.', 'aviso');
      return;
    }

    const respuestas = await Promise.allSettled([
      API.get('/api/cuotas/alumno/' + Number(usuario.alumno_id)),
      API.get('/api/examenes/mis-inscripciones')
    ]);

    const sesionVencida = respuestas.some(function (respuesta) {
      return (
        respuesta.status === 'fulfilled' &&
        irALoginSiCaduco(respuesta.value)
      );
    });

    if (sesionVencida) {
      return;
    }

    /* Pedimos las cuotas e inscripciones frescas: la caché del panel
       puede haber quedado vieja si la escuela generó cuotas después. */
    const cuotas = respuestas[0].status === 'fulfilled'
      ? listaDe(respuestas[0].value, 'cuotas')
      : p.cuotas();

    const abiertas = cuotas.filter(esCuotaAbierta);

    const inscripciones = respuestas[1].status === 'fulfilled'
      ? listaDe(respuestas[1].value, 'inscripciones')
      : p.inscripciones();

    PanelUI.abrirModal({
      kicker: 'Pagos',
      titulo: 'Declarar pago',
      cuerpo:
        '<form id="form-pago" class="panel-form">' +
        PanelUI.bloqueAlerta() +
        '<p class="pista">El pago queda pendiente hasta que la escuela lo confirme.</p>' +
        '<p class="pista pago-pista" id="pago-pista" hidden></p>' +
        camposPago() +
        '</form>',
      pie:
        PanelUI.boton({ texto: 'Cancelar', accion: 'cerrar-modal' }) +
        '<button type="submit" class="panel-btn panel-btn-primario" form="form-pago" id="btn-pago-guardar">' +
        'Declarar pago</button>',
      alAbrir: function () {
        const form = $('#form-pago');
        const controles = conectarPago(form, abiertas, inscripciones);

        form.addEventListener('submit', async function (evento) {
          evento.preventDefault();
          PanelUI.limpiarAviso();

          if (!form.checkValidity()) {
            form.reportValidity();
            return;
          }

          if (!validarPago(controles)) {
            return;
          }

          const boton = $('#btn-pago-guardar');
          const datos = cuerpoPago();

          datos.alumno_id = Number(usuario.alumno_id);
          datos.centro_id = Number(perfil.centro_id);

          PanelUI.ocupado(boton, 'Enviando…');

          const res = await API.post('/api/pagos', datos);

          PanelUI.libre(boton);

          if (!res.ok) {
            mostrarError(res);
            return;
          }

          UI.avisar('Pago declarado. Queda pendiente de confirmación.', 'ok');
          PanelUI.cerrarModal();
          await refrescar();
        });
      }
    });
  }

  function alumnoParaPago(alumnoId) {
    if (alumnoId) {
      return alumnoPorId(alumnoId);
    }

    return null;
  }

  async function abrirRegistrarPago(alumnoId) {
    if (!requiereStaff()) {
      return;
    }

    const p = panel();
    const alumnos = p.alumnos();

    if (!alumnos.length) {
      UI.avisar('Todavía no hay alumnos para registrar un pago.', 'aviso');
      return;
    }

    const preseleccionado = alumnoParaPago(alumnoId);

    PanelUI.abrirModal({
      kicker: 'Cobros',
      titulo: 'Registrar pago',
      ancho: true,
      cuerpo:
        '<form id="form-pago" class="panel-form">' +
        PanelUI.bloqueAlerta() +
        '<div class="form-grid">' +
        PanelUI.campo({
          id: 'pago-alumno',
          label: 'Alumno',
          tipo: 'select',
          valor: preseleccionado ? preseleccionado.alumno_id : '',
          vacio: 'Elegí un alumno',
          opciones: alumnos.map(function (alumno) {
            return {
              valor: alumno.alumno_id,
              texto:
                nombreCompleto(alumno) +
                (alumno.dni ? ' · ' + alumno.dni : '') +
                (String(alumno.estado || '').toUpperCase() === 'ACTIVO'
                  ? ''
                  : ' (' + alumno.estado + ')')
            };
          }),
          requerido: true
        }) +
        '</div>' +
        '<div id="pago-fuentes"></div>' +
        '<p class="pista pago-pista" id="pago-pista" hidden></p>' +
        camposPago() +
        (esAdmin()
          ? '<label class="check pago-confirmar">' +
            '<input type="checkbox" id="pago-confirmar" />' +
            'Confirmar el pago ahora' +
            '</label>'
          : '') +
        '</form>',
      pie:
        PanelUI.boton({ texto: 'Cancelar', accion: 'cerrar-modal' }) +
        '<button type="submit" class="panel-btn panel-btn-primario" form="form-pago" id="btn-pago-guardar">' +
        'Registrar pago</button>',
      alAbrir: function () {
        const form = $('#form-pago');
        const selectAlumno = $('#pago-alumno');
        const contenedorFuentes = $('#pago-fuentes');
        let controles = null;
        let pedidoActual = 0;

        async function cargarFuentes() {
          const alumno = alumnoPorId(selectAlumno.value);
          const numeroPedido = pedidoActual + 1;

          pedidoActual = numeroPedido;
          contenedorFuentes.innerHTML = '<div class="cargando-filas" aria-hidden="true"><span class="cargando-fila"></span></div>';

          if (!alumno) {
            contenedorFuentes.innerHTML = '';
            controles = conectarPago(form, [], [], {
              pista: 'Elegí un alumno para cargar sus cuotas e inscripciones.'
            });
            return;
          }

          const respuestas = await Promise.allSettled([
            API.get('/api/cuotas/alumno/' + Number(alumno.alumno_id)),
            API.get('/api/examenes/mis-inscripciones?alumno_id=' + Number(alumno.alumno_id))
          ]);

          if (pedidoActual !== numeroPedido) {
            return;
          }

          const sesionVencida = respuestas.some(function (respuesta) {
            return (
              respuesta.status === 'fulfilled' &&
              irALoginSiCaduco(respuesta.value)
            );
          });

          if (sesionVencida) {
            return;
          }

          contenedorFuentes.innerHTML = '';

          const cuotas = respuestas[0].status === 'fulfilled'
            ? listaDe(respuestas[0].value, 'cuotas')
            : [];
          const inscripciones = respuestas[1].status === 'fulfilled'
            ? listaDe(respuestas[1].value, 'inscripciones')
            : [];

          controles = conectarPago(
            form,
            cuotas.filter(esCuotaAbierta),
            inscripciones
          );
        }

        selectAlumno.addEventListener('change', cargarFuentes);
        cargarFuentes();

        form.addEventListener('submit', async function (evento) {
          evento.preventDefault();
          PanelUI.limpiarAviso();

          if (!form.checkValidity()) {
            form.reportValidity();
            return;
          }

          const alumno = alumnoPorId(selectAlumno.value);

          if (!alumno) {
            PanelUI.aviso('Elegí un alumno.', 'aviso');
            return;
          }

          if (!alumno.centro_id) {
            PanelUI.aviso('El alumno no tiene una sede asignada.', 'aviso');
            return;
          }

          if (!controles || !validarPago(controles)) {
            return;
          }

          const boton = $('#btn-pago-guardar');
          const datos = cuerpoPago();

          datos.alumno_id = Number(alumno.alumno_id);
          datos.centro_id = Number(alumno.centro_id);
          datos.profesor_id = alumno.profesor_id
            ? Number(alumno.profesor_id)
            : null;

          PanelUI.ocupado(boton, 'Registrando…');

          const res = await API.post('/api/pagos', datos);

          if (!res.ok) {
            PanelUI.libre(boton);
            mostrarError(res);
            return;
          }

          const pago = (res.data && res.data.pago) || {};
          const pagoId = pago.pago_id || pago.id;
          const confirmar = $('#pago-confirmar');

          if (confirmar && confirmar.checked && pagoId) {
            const confirmacion = await API.put(
              '/api/pagos/' + Number(pagoId) + '/confirmar',
              { profesor_id: sesion().profesor_id || null }
            );

            PanelUI.libre(boton);

            if (!confirmacion.ok) {
              UI.avisar(
                'Pago registrado, pero no se pudo confirmar: ' +
                  API.mensaje(confirmacion),
                'aviso'
              );
              PanelUI.cerrarModal();
              await refrescar();
              return;
            }
          } else {
            PanelUI.libre(boton);
          }

          UI.avisar(
            confirmar && confirmar.checked
              ? 'Pago registrado y confirmado.'
              : 'Pago registrado. Queda pendiente de confirmación.',
            'ok'
          );
          PanelUI.cerrarModal();
          await refrescar();
        });
      }
    });
  }

  async function confirmarPago(pagoId) {
    if (!esAdmin()) {
      UI.avisar('Solo la administración puede confirmar pagos.', 'aviso');
      return;
    }

    const confirmado = await PanelUI.confirmar({
      titulo: 'Confirmar pago',
      mensaje: 'El pago va a pasar a estado CONFIRMADO y se acredita en la ficha del alumno.',
      textoOk: 'Confirmar pago',
      peligro: false
    });

    if (!confirmado) {
      return;
    }

    const res = await API.put(
      '/api/pagos/' + Number(pagoId) + '/confirmar',
      { profesor_id: sesion().profesor_id || null }
    );

    if (!res.ok) {
      avisarErrorDesdePanel(res);
      return;
    }

    UI.avisar('Pago confirmado.', 'ok');
    await refrescar();
  }

  /* ---------------------------------------------------------
     Exámenes
     --------------------------------------------------------- */

  async function inscribirExamen(examenId) {
    const p = panel();
    const usuario = sesion();

    if (!p || !usuario) {
      return;
    }

    if (!usuario.alumno_id) {
      UI.avisar('Tu usuario no está vinculado a una ficha de alumno.', 'aviso');
      return;
    }

    const examen = p.examenes().filter(function (item) {
      return Number(item.examen_id) === Number(examenId);
    })[0];

    const confirmado = await PanelUI.confirmar({
      titulo: 'Inscribirme al examen',
      mensaje: examen
        ? '¿Confirmás la inscripción a "' +
          (examen.titulo || 'Examen') +
          '" del ' +
          UI.formatearFecha(examen.fecha_examen) +
          '?'
        : '¿Confirmás la inscripción a este examen?',
      textoOk: 'Inscribirme',
      peligro: false
    });

    if (!confirmado) {
      return;
    }

    const res = await API.post(
      '/api/examenes/' + Number(examenId) + '/inscriptos',
      { alumno_id: Number(usuario.alumno_id) }
    );

    if (!res.ok) {
      UI.avisar(API.mensaje(res), 'error');
      return;
    }

    UI.avisar('Inscripción registrada.', 'ok');
    await refrescar();
  }

  async function cancelarInscripcion(inscripcionId) {
    const confirmado = await PanelUI.confirmar({
      titulo: 'Cancelar inscripción',
      mensaje: 'La inscripción al examen se elimina. Si ya pagaste, hablá con la escuela.',
      textoOk: 'Cancelar inscripción'
    });

    if (!confirmado) {
      return;
    }

    const res = await API.del(
      '/api/examenes/inscripciones/' + Number(inscripcionId)
    );

    if (!res.ok) {
      UI.avisar(API.mensaje(res), 'error');
      return;
    }

    UI.avisar('Inscripción cancelada.', 'ok');
    await refrescar();
  }

  /* ---------------------------------------------------------
     Exámenes: agenda del staff
     --------------------------------------------------------- */

  function valorFechaHora(valor) {
    if (!valor) {
      return '';
    }

    const texto = String(valor);

    /* Flask serializa el datetime como "Thu, 29 Oct 2026 18:30:00 GMT".
       Leemos los componentes tal cual para no correr la hora por zona
       horaria; si ya viene en ISO, alcanza con recortarlo. */
    const iso = texto.match(
      /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})/
    );

    if (iso) {
      return iso[1] + '-' + iso[2] + '-' + iso[3] + 'T' + iso[4] + ':' + iso[5];
    }

    const fecha = new Date(texto);

    if (isNaN(fecha.getTime())) {
      return '';
    }

    const dos = function (numero) {
      return String(numero).padStart(2, '0');
    };

    return (
      fecha.getUTCFullYear() +
      '-' +
      dos(fecha.getUTCMonth() + 1) +
      '-' +
      dos(fecha.getUTCDate()) +
      'T' +
      dos(fecha.getUTCHours()) +
      ':' +
      dos(fecha.getUTCMinutes())
    );
  }

  function fechaExamenParaApi(valor) {
    const limpio = String(valor || '').trim();

    if (!limpio) {
      return '';
    }

    return (limpio.length === 16 ? limpio + ':00' : limpio).replace('T', ' ');
  }

  function profesoresParaExamen(centroId, incluirInactivos, profesorActual) {
    const p = panel();
    const usuario = sesion();

    if (!p || !usuario) {
      return [];
    }

    if (!esAdmin()) {
      const propio = p.profesores().filter(function (profesor) {
        return Number(profesor.profesor_id) === Number(usuario.profesor_id);
      })[0];

      return [
        {
          valor: usuario.profesor_id,
          texto: propio
            ? nombreCompleto(propio)
            : nombreCompleto(usuario) || 'Mi perfil'
        }
      ];
    }

    const profesores = opcionesProfesores(incluirInactivos);
    const centro = Number(centroId);

    if (!centro) {
      return profesores;
    }

    const compatibles = p.profesores().filter(function (profesor) {
      if (!incluirInactivos && !Boolean(profesor.profesor_activo)) {
        return false;
      }

      const sedes = Array.isArray(profesor.centros) ? profesor.centros : [];

      return sedes.some(function (sede) {
        return Number(sede.centro_id) === centro;
      });
    });

    if (!compatibles.length) {
      return profesores;
    }

    const ids = compatibles.map(function (profesor) {
      return Number(profesor.profesor_id);
    });

    const filtrados = profesores.filter(function (opcion) {
      return ids.indexOf(Number(opcion.valor)) !== -1;
    });

    /* Al editar, el docente ya asignado tiene que seguir en la lista aunque
       no figure como profesor de la sede elegida. */
    if (
      profesorActual &&
      !filtrados.some(function (opcion) {
        return Number(opcion.valor) === Number(profesorActual);
      })
    ) {
      const actual = profesores.filter(function (opcion) {
        return Number(opcion.valor) === Number(profesorActual);
      })[0];

      if (actual) {
        filtrados.push(actual);
      }
    }

    return filtrados;
  }

  function abrirFormularioExamen(examenId) {
    if (!requiereStaff()) {
      return;
    }

    const p = panel();
    const usuario = sesion();

    const examen = examenId
      ? p.examenes().filter(function (item) {
          return Number(item.examen_id) === Number(examenId);
        })[0]
      : null;

    if (examenId && !examen) {
      UI.avisar('No encontramos ese examen. Actualizá el panel.', 'aviso');
      return;
    }

    if (
      examen &&
      !esAdmin() &&
      Number(examen.profesor_id) !== Number(usuario.profesor_id)
    ) {
      UI.avisar('Solo podés editar los exámenes que tenés asignados.', 'aviso');
      return;
    }

    if (!esAdmin() && !usuario.profesor_id) {
      UI.avisar(
        'Tu usuario no está vinculado a una ficha de profesor: pedile a la administración que lo asocie.',
        'aviso'
      );
      return;
    }

    const sedes = centrosParaNoticia();

    if (!sedes.length) {
      UI.avisar(
        'No tenés sedes asignadas: pedile a la administración que te asigne una para agendar exámenes.',
        'aviso'
      );
      return;
    }

    const centroInicial = examen && examen.centro_id ? examen.centro_id : '';
    const opcionesSede = sedes.map(function (centro) {
      return { valor: centro.centro_id, texto: centro.nombre };
    });

    const opcionesProfesor = profesoresParaExamen(
      centroInicial,
      Boolean(examen),
      examen && examen.profesor_id ? examen.profesor_id : null
    );

    const profesorInicial =
      examen && examen.profesor_id
        ? examen.profesor_id
        : !esAdmin()
          ? usuario.profesor_id
          : '';

    PanelUI.abrirModal({
      kicker: examen ? 'Editar examen' : 'Nueva fecha',
      titulo: examen ? 'Editar examen' : 'Agendar examen',
      ancho: true,
      cuerpo:
        '<form id="form-examen" class="panel-form">' +
        PanelUI.bloqueAlerta() +
        PanelUI.fila(
          PanelUI.campo({
            id: 'examen-titulo',
            label: 'Título',
            valor: examen ? examen.titulo : '',
            requerido: true,
            placeholder: 'Ej.: Examen de cinturón amarillo'
          }),
          PanelUI.campo({
            id: 'examen-centro',
            label: 'Sede',
            tipo: 'select',
            valor: centroInicial,
            vacio: false,
            opciones: opcionesSede,
            requerido: true
          })
        ) +
        PanelUI.fila(
          PanelUI.campo({
            id: 'examen-profesor',
            label: 'Profesor',
            tipo: 'select',
            valor: profesorInicial,
            vacio: false,
            opciones: opcionesProfesor,
            requerido: true,
            deshabilitado: !esAdmin()
          }),
          PanelUI.campo({
            id: 'examen-fecha',
            label: 'Fecha y hora',
            tipo: 'datetime-local',
            valor: valorFechaHora(examen && examen.fecha_examen),
            requerido: true
          })
        ) +
        PanelUI.fila(
          PanelUI.campo({
            id: 'examen-monto',
            label: 'Monto',
            tipo: 'number',
            valor: examen ? Number(examen.monto) : 0,
            min: 0,
            step: '0.01',
            inputmode: 'decimal',
            requerido: true,
            pista: 'Lo que abona el alumno al inscribirse. Podés dejarlo en 0.'
          })
        ) +
        '</form>',
      pie:
        PanelUI.boton({ texto: 'Cancelar', accion: 'cerrar-modal' }) +
        '<button type="submit" class="panel-btn panel-btn-primario" form="form-examen" id="btn-examen-guardar">' +
        (examen ? 'Guardar cambios' : 'Agendar examen') +
        '</button>',
      alAbrir: function () {
        const form = $('#form-examen');

        form.addEventListener('submit', async function (evento) {
          evento.preventDefault();
          PanelUI.limpiarAviso();

          if (!form.checkValidity()) {
            form.reportValidity();
            return;
          }

          const centro = PanelUI.valor('examen-centro');
          const profesor = PanelUI.valor('examen-profesor');
          const fecha = fechaExamenParaApi(PanelUI.valor('examen-fecha'));
          const monto = Number(PanelUI.valor('examen-monto'));

          const datos = {
            titulo: PanelUI.valor('examen-titulo').trim(),
            centro_id: centro ? Number(centro) : null,
            profesor_id: profesor ? Number(profesor) : null,
            fecha_examen: fecha,
            monto: Number.isFinite(monto) ? monto : 0
          };

          if (!datos.titulo || !datos.centro_id || !datos.profesor_id) {
            PanelUI.aviso('Completá el título, la sede y el profesor.', 'aviso');
            return;
          }

          if (!datos.fecha_examen) {
            PanelUI.aviso('Elegí la fecha y la hora del examen.', 'aviso');
            return;
          }

          const boton = $('#btn-examen-guardar');

          PanelUI.ocupado(boton, 'Guardando…');

          const res = examen
            ? await API.put('/api/examenes/' + Number(examen.examen_id), datos)
            : await API.post('/api/examenes/', datos);

          PanelUI.libre(boton);

          if (!res.ok) {
            mostrarError(res);
            return;
          }

          UI.avisar(
            examen ? 'Examen actualizado.' : 'Examen agendado.',
            'ok'
          );
          PanelUI.cerrarModal();
          await refrescar();
        });
      }
    });
  }

  async function eliminarExamen(examenId) {
    if (!requiereStaff()) {
      return;
    }

    const examen = panel().examenes().filter(function (item) {
      return Number(item.examen_id) === Number(examenId);
    })[0];

    const confirmado = await PanelUI.confirmar({
      titulo: 'Eliminar examen',
      mensaje:
        'El examen "' +
        (examen ? examen.titulo : 'seleccionado') +
        '" va a dejar de mostrarse a los alumnos. Las inscripciones existentes se conservan.',
      textoOk: 'Eliminar',
      peligro: true
    });

    if (!confirmado) {
      return;
    }

    const res = await API.del('/api/examenes/' + Number(examenId));

    if (!res.ok) {
      mostrarError(res);
      return;
    }

    UI.avisar('Examen eliminado.', 'ok');
    await refrescar();
  }

  /* ---------------------------------------------------------
     Noticias
     --------------------------------------------------------- */

  function centrosParaNoticia() {
    const p = panel();
    const centros = p.centros();

    if (esAdmin()) {
      return centros;
    }

    const usuario = sesion();

    const propio = p.profesores().filter(function (profesor) {
      return Number(profesor.profesor_id) === Number(usuario.profesor_id);
    })[0];

    const ids = ((propio && propio.centros) || []).map(function (centro) {
      return Number(centro.centro_id);
    });

    return centros.filter(function (centro) {
      return ids.indexOf(Number(centro.centro_id)) !== -1;
    });
  }

  function abrirFormularioNoticia(noticiaId) {
    if (!requiereStaff()) {
      return;
    }

    const p = panel();

    const noticia = noticiaId
      ? p.noticias().filter(function (item) {
          return Number(item.id) === Number(noticiaId);
        })[0]
      : null;

    if (noticiaId && !noticia) {
      UI.avisar('No encontramos esa noticia. Actualizá el panel.', 'aviso');
      return;
    }

    const sedes = centrosParaNoticia();

    if (!sedes.length && !esAdmin()) {
      UI.avisar(
        'No tenés sedes asignadas: pedile a la administración que te asigne una para publicar novedades.',
        'aviso'
      );
      return;
    }

    const opciones = (
      esAdmin()
        ? [{ valor: '', texto: 'General (todas las sedes)' }]
        : []
    ).concat(
      sedes.map(function (centro) {
        return { valor: centro.centro_id, texto: centro.nombre };
      })
    );

    PanelUI.abrirModal({
      kicker: noticia ? 'Editar novedad' : 'Nueva novedad',
      titulo: noticia ? 'Editar noticia' : 'Publicar noticia',
      ancho: true,
      cuerpo:
        '<form id="form-noticia" class="panel-form">' +
        PanelUI.bloqueAlerta() +
        PanelUI.fila(
          PanelUI.campo({
            id: 'noticia-titulo',
            label: 'Título',
            valor: noticia ? noticia.titulo : '',
            requerido: true,
            placeholder: 'Ej.: Nuevo horario de clases'
          }),
          PanelUI.campo({
            id: 'noticia-centro',
            label: 'Sede',
            tipo: 'select',
            valor:
              noticia && noticia.centro_id
                ? noticia.centro_id
                : '',
            vacio: false,
            opciones: opciones
          })
        ) +
        PanelUI.fila(
          PanelUI.campo({
            id: 'noticia-contenido',
            label: 'Contenido',
            tipo: 'textarea',
            filas: 5,
            valor: noticia ? noticia.contenido : '',
            requerido: true,
            ancho: true,
            placeholder: 'Escribí la novedad para los alumnos…'
          }),
          PanelUI.campo({
            id: 'noticia-imagen',
            label: 'Imagen (URL)',
            tipo: 'url',
            valor: noticia && noticia.imagen_url ? noticia.imagen_url : '',
            ancho: true,
            placeholder: 'https://… (opcional)'
          })
        ) +
        '</form>',
      pie:
        PanelUI.boton({ texto: 'Cancelar', accion: 'cerrar-modal' }) +
        '<button type="submit" class="panel-btn panel-btn-primario" form="form-noticia" id="btn-noticia-guardar">' +
        (noticia ? 'Guardar cambios' : 'Publicar noticia') +
        '</button>',
      alAbrir: function () {
        const form = $('#form-noticia');

        form.addEventListener('submit', async function (evento) {
          evento.preventDefault();
          PanelUI.limpiarAviso();

          if (!form.checkValidity()) {
            form.reportValidity();
            return;
          }

          const centro = PanelUI.valor('noticia-centro');

          const datos = {
            titulo: PanelUI.valor('noticia-titulo').trim(),
            contenido: PanelUI.valor('noticia-contenido').trim(),
            centro_id: centro ? Number(centro) : null,
            imagen_url: PanelUI.valor('noticia-imagen').trim() || null
          };

          if (!datos.titulo || !datos.contenido) {
            PanelUI.aviso('Completá el título y el contenido.', 'aviso');
            return;
          }

          const boton = $('#btn-noticia-guardar');

          PanelUI.ocupado(boton, 'Guardando…');

          const res = noticia
            ? await API.put('/api/noticias/' + Number(noticia.id), datos)
            : await API.post('/api/noticias', datos);

          PanelUI.libre(boton);

          if (!res.ok) {
            mostrarError(res);
            return;
          }

          UI.avisar(
            noticia ? 'Noticia actualizada.' : 'Noticia publicada.',
            'ok'
          );
          PanelUI.cerrarModal();
          await refrescar();
        });
      }
    });
  }

  async function eliminarNoticia(noticiaId) {
    if (!requiereStaff()) {
      return;
    }

    const noticia = panel().noticias().filter(function (item) {
      return Number(item.id) === Number(noticiaId);
    })[0];

    const confirmado = await PanelUI.confirmar({
      titulo: 'Eliminar noticia',
      mensaje:
        'La noticia "' +
        (noticia ? noticia.titulo : 'seleccionada') +
        '" va a dejar de verse en el panel de los alumnos.',
      textoOk: 'Eliminar',
      peligro: true
    });

    if (!confirmado) {
      return;
    }

    const res = await API.del('/api/noticias/' + Number(noticiaId));

    if (!res.ok) {
      mostrarError(res);
      return;
    }

    UI.avisar('Noticia eliminada.', 'ok');
    await refrescar();
  }

  /* ---------------------------------------------------------
     Sedes (solo ADMIN)
     --------------------------------------------------------- */

  function buscarSede(sedeId) {
    return panel().centros().filter(function (item) {
      return Number(item.centro_id) === Number(sedeId);
    })[0] || null;
  }

  function datosSede(sede) {
    return {
      nombre: sede.nombre,
      direccion: sede.direccion || null,
      telefono: sede.telefono || null,
      captura: sede.captura || null
    };
  }

  function abrirFormularioSede(sedeId) {
    if (!requiereAdmin()) {
      return;
    }

    const sede = sedeId ? buscarSede(sedeId) : null;

    if (sedeId && !sede) {
      UI.avisar('No encontramos esa sede. Actualizá el panel.', 'aviso');
      return;
    }

    PanelUI.abrirModal({
      kicker: sede ? 'Editar sede' : 'Nueva sede',
      titulo: sede ? 'Editar sede' : 'Crear sede',
      ancho: true,
      cuerpo:
        '<form id="form-sede" class="panel-form">' +
        PanelUI.bloqueAlerta() +
        PanelUI.fila(
          PanelUI.campo({
            id: 'sede-nombre',
            label: 'Nombre',
            valor: sede ? sede.nombre : '',
            requerido: true,
            placeholder: 'Ej.: Sede Quilmes Centro'
          }),
          PanelUI.campo({
            id: 'sede-telefono',
            label: 'Teléfono',
            tipo: 'tel',
            valor: sede && sede.telefono ? sede.telefono : '',
            placeholder: '11 5555-5555 (opcional)'
          })
        ) +
        PanelUI.fila(
          PanelUI.campo({
            id: 'sede-direccion',
            label: 'Dirección',
            valor: sede && sede.direccion ? sede.direccion : '',
            ancho: true,
            placeholder: 'Calle, número y localidad (opcional)'
          })
        ) +
        PanelUI.fila(
          PanelUI.campo({
            id: 'sede-captura',
            label: 'Imagen (URL)',
            tipo: 'text',
            valor: sede && sede.captura ? sede.captura : '',
            ancho: true,
            placeholder: 'https://… (opcional)',
            pista: 'Se usa como imagen de la sede en la landing, si está cargada.'
          })
        ) +
        '</form>',
      pie:
        PanelUI.boton({ texto: 'Cancelar', accion: 'cerrar-modal' }) +
        '<button type="submit" class="panel-btn panel-btn-primario" form="form-sede" id="btn-sede-guardar">' +
        (sede ? 'Guardar cambios' : 'Crear sede') +
        '</button>',
      alAbrir: function () {
        const form = $('#form-sede');

        form.addEventListener('submit', async function (evento) {
          evento.preventDefault();
          PanelUI.limpiarAviso();

          if (!form.checkValidity()) {
            form.reportValidity();
            return;
          }

          const datos = {
            nombre: PanelUI.valor('sede-nombre').trim(),
            direccion: PanelUI.valor('sede-direccion').trim() || null,
            telefono: PanelUI.valor('sede-telefono').trim() || null,
            captura: PanelUI.valor('sede-captura').trim() || null
          };

          if (!datos.nombre) {
            PanelUI.aviso('El nombre de la sede es obligatorio.', 'aviso');
            return;
          }

          /* El PUT reemplaza todos los campos: mandamos también activo
             para no reactivar sin querer una sede dada de baja. */
          if (sede) {
            datos.activo =
              sede.activo === undefined || sede.activo === null
                ? true
                : Number(sede.activo) !== 0;
          }

          const boton = $('#btn-sede-guardar');

          PanelUI.ocupado(boton, 'Guardando…');

          const res = sede
            ? await API.put('/api/centros/' + Number(sede.centro_id), datos)
            : await API.post('/api/centros', datos);

          PanelUI.libre(boton);

          if (!res.ok) {
            mostrarError(res);
            return;
          }

          UI.avisar(sede ? 'Sede actualizada.' : 'Sede creada.', 'ok');
          PanelUI.cerrarModal();
          await refrescar();
        });
      }
    });
  }

  async function eliminarSede(sedeId) {
    if (!requiereAdmin()) {
      return;
    }

    const sede = buscarSede(sedeId);

    if (!sede) {
      UI.avisar('No encontramos esa sede. Actualizá el panel.', 'aviso');
      return;
    }

    const confirmado = await PanelUI.confirmar({
      titulo: 'Dar de baja la sede',
      mensaje:
        'La sede "' +
        sede.nombre +
        '" va a dejar de aparecer en los selectores. Los alumnos, profesores y registros existentes se conservan, y podés reactivarla después.',
      textoOk: 'Dar de baja',
      peligro: true
    });

    if (!confirmado) {
      return;
    }

    const res = await API.del('/api/centros/' + Number(sedeId));

    if (!res.ok) {
      mostrarError(res);
      return;
    }

    UI.avisar('Sede dada de baja.', 'ok');
    await refrescar();
  }

  async function reactivarSede(sedeId) {
    if (!requiereAdmin()) {
      return;
    }

    const sede = buscarSede(sedeId);

    if (!sede) {
      UI.avisar('No encontramos esa sede. Actualizá el panel.', 'aviso');
      return;
    }

    const confirmado = await PanelUI.confirmar({
      titulo: 'Reactivar sede',
      mensaje:
        'La sede "' +
        sede.nombre +
        '" va a volver a aparecer en los selectores del panel.',
      textoOk: 'Reactivar'
    });

    if (!confirmado) {
      return;
    }

    const datos = datosSede(sede);
    datos.activo = true;

    const res = await API.put('/api/centros/' + Number(sedeId), datos);

    if (!res.ok) {
      mostrarError(res);
      return;
    }

    UI.avisar('Sede reactivada.', 'ok');
    await refrescar();
  }

  /* ---------------------------------------------------------
     Lista: marcar todos
     --------------------------------------------------------- */

  function marcarTodos(modo) {
    const presente = modo !== 'ausente';

    UI.qsa('#lista-alumnos input[type="checkbox"]').forEach(function (marca) {
      marca.checked = presente;
    });
  }

  /* ---------------------------------------------------------
     Delegación de eventos
     --------------------------------------------------------- */

  const acciones = {
    perfil: function () {
      abrirPerfil();
    },

    'cerrar-modal': function () {
      PanelUI.cerrarModal();
    },

    'cerrar-drawer': function () {
      PanelUI.cerrarDrawer();
    },

    'nuevo-alumno': function () {
      abrirFormularioAlumno(null);
    },

    'editar-alumno': function (id) {
      PanelUI.cerrarDrawer();
      abrirFormularioAlumno(id);
    },

    'baja-alumno': function (id) {
      darDeBajaAlumno(id);
    },

    'ficha-alumno': function (id) {
      abrirFicha(id);
    },

    'tomar-lista': function () {
      abrirTomarLista();
    },

    'lista-todos': function (id, boton) {
      marcarTodos(boton.getAttribute('data-modo'));
    },

    'declarar-pago': function () {
      abrirDeclararPago();
    },

    'registrar-pago': function (id) {
      PanelUI.cerrarDrawer();
      abrirRegistrarPago(id);
    },

    'confirmar-pago': function (id) {
      confirmarPago(id);
    },

    'inscribir-examen': function (id) {
      inscribirExamen(id);
    },

    'cancelar-inscripcion': function (id) {
      cancelarInscripcion(id);
    },

    'nueva-sede': function () {
      abrirFormularioSede(null);
    },

    'editar-sede': function (id) {
      abrirFormularioSede(id);
    },

    'eliminar-sede': function (id) {
      eliminarSede(id);
    },

    'reactivar-sede': function (id) {
      reactivarSede(id);
    },

    'nuevo-examen': function () {
      abrirFormularioExamen(null);
    },

    'editar-examen': function (id) {
      abrirFormularioExamen(id);
    },

    'eliminar-examen': function (id) {
      eliminarExamen(id);
    },

    'nueva-noticia': function () {
      abrirFormularioNoticia(null);
    },

    'editar-noticia': function (id) {
      abrirFormularioNoticia(id);
    },

    'eliminar-noticia': function (id) {
      eliminarNoticia(id);
    }
  };

  document.addEventListener('click', function (evento) {
    const boton = evento.target.closest('[data-accion]');

    if (!boton) {
      return;
    }

    const nombre = boton.getAttribute('data-accion');
    const manejador = acciones[nombre];

    if (!manejador) {
      return;
    }

    const id = Number(boton.getAttribute('data-id')) || null;

    evento.preventDefault();
    manejador(id, boton, evento);
  });
})();
