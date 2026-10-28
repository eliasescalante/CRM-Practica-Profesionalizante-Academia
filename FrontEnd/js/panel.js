/* =========================================================
   Tien Long Hu - Panel privado
   ---------------------------------------------------------
   Una sola página con dos vistas:
     - ALUMNO        -> sus asistencias, cuotas, pagos,
                        graduaciones y novedades
     - PROFESOR/ADMIN -> alumnos, sedes, cobros y agenda

   La sesión se valida contra /api/auth/me antes de pintar nada.
   Si el token ya no sirve, se limpia y se vuelve al login.
   ========================================================= */

(function () {
  'use strict';

  const $ = UI.qs;

  const MESES = [
    'ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN',
    'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'
  ];

  const ESTADOS_ABIERTOS = ['PENDIENTE', 'VENCIDA'];

  /* ---------------------------------------------------------
     Nodos del header
     --------------------------------------------------------- */

  const panelNombre = $('#panel-nombre');
  const panelRol = $('#panel-rol');
  const panelAvatar = $('#panel-avatar');
  const btnSalir = $('#btn-salir');
  const btnRecargar = $('#btn-recargar');

  const esqueleto = $('#panel-esqueleto');
  const alerta = $('#panel-alerta');

  const vistaAlumno = $('#vista-alumno');
  const vistaStaff = $('#vista-staff');

  /* ---------------------------------------------------------
     Estado
     --------------------------------------------------------- */

  let usuario = null;
  let alumnosCache = [];
  let cuotasCache = [];
  let pagosCache = [];
  let examenesCache = [];
  let inscripcionesCache = [];
  let centrosCache = [];
  let profesoresCache = [];
  let noticiasCache = [];
  let chatCentroId = null;
  let perfilCache = {};
  let sesionCaida = false;

  /* ---------------------------------------------------------
     Helpers de datos
     --------------------------------------------------------- */

  /* Devuelve el cuerpo de una respuesta o null.
     Si el backend dijo 401/403, marca la sesión como caída. */
  function cuerpo(resultado) {
    if (!resultado) {
      return null;
    }

    if (API.sesionInvalida(resultado)) {
      sesionCaida = true;
      return null;
    }

    return resultado.ok ? resultado.data : null;
  }

  function lista(datos, clave) {
    if (!datos) {
      return [];
    }

    if (Array.isArray(datos)) {
      return datos;
    }

    return Array.isArray(datos[clave]) ? datos[clave] : [];
  }

  function sumar(items, campo) {
    return items.reduce(function (total, item) {
      const valor = Number(item[campo]);
      return total + (isNaN(valor) ? 0 : valor);
    }, 0);
  }

  function esAbierta(cuota) {
    return ESTADOS_ABIERTOS.indexOf(String(cuota.estado || '').toUpperCase()) !== -1;
  }

  function estadoPago(pago) {
    return String(pago.estado || '').toUpperCase();
  }

  function etiquetaRol(rol) {
    if (rol === 'ADMIN') {
      return 'Administrador';
    }

    if (rol === 'PROFESOR') {
      return 'Profesor';
    }

    if (rol === 'ALUMNO') {
      return 'Alumno';
    }

    return rol || '—';
  }

  function esStaff(rol) {
    return rol === 'ADMIN' || rol === 'PROFESOR';
  }

  /* ---------------------------------------------------------
     Helpers de formato
     --------------------------------------------------------- */

  function partesFecha(valor) {
    if (!valor) {
      return null;
    }

    const fecha = new Date(valor);

    if (isNaN(fecha.getTime())) {
      return null;
    }

    return {
      dia: String(fecha.getUTCDate()).padStart(2, '0'),
      mes: MESES[fecha.getUTCMonth()],
      anio: fecha.getUTCFullYear()
    };
  }

  /* Los endpoints devuelven RFC 1123; las fechas sin hora se leen en UTC
     para no mostrarlas corridas un día. */
  function fecha(valor) {
    return UI.formatearFecha(valor);
  }

  /* Para el chat mostramos día y hora local en formato corto. */
  function fechaHora(valor) {
    if (!valor) {
      return '';
    }

    const momento = new Date(valor);

    if (isNaN(momento.getTime())) {
      return '';
    }

    return (
      String(momento.getDate()).padStart(2, '0') +
      '/' +
      String(momento.getMonth() + 1).padStart(2, '0') +
      ' · ' +
      String(momento.getHours()).padStart(2, '0') +
      ':' +
      String(momento.getMinutes()).padStart(2, '0')
    );
  }

  function fechaHoy() {
    const hoy = new Date();

    return (
      String(hoy.getDate()).padStart(2, '0') +
      '/' +
      String(hoy.getMonth() + 1).padStart(2, '0') +
      '/' +
      hoy.getFullYear()
    );
  }

  function periodo(cuota) {
    const mes = Number(cuota.periodo_mes);
    const anio = cuota.periodo_anio;

    if (!mes || !anio) {
      return '—';
    }

    return MESES[mes - 1] + ' ' + anio;
  }

  function fechaBloque(valor) {
    const partes = partesFecha(valor);

    if (!partes) {
      return '';
    }

    return (
      '<span class="panel-fecha" aria-hidden="true">' +
      '<b>' + partes.dia + '</b>' +
      '<span>' + partes.mes + '</span>' +
      '</span>'
    );
  }

  function texto(valor) {
    return UI.escapar(UI.texto(valor));
  }

  /* ---------------------------------------------------------
     Constructores de tablas
     --------------------------------------------------------- */

  /* columnas: [{ titulo, clase }]
     filas:    [[{ html, clase }]]  (el html ya viene escapado) */
  function tabla(columnas, filas) {
    const cabecera = columnas
      .map(function (col) {
        return (
          '<th' + (col.clase ? ' class="' + col.clase + '"' : '') + '>' +
          UI.escapar(col.titulo) +
          '</th>'
        );
      })
      .join('');

    const cuerpoTabla = filas
      .map(function (celdas) {
        return (
          '<tr>' +
          celdas
            .map(function (celda) {
              return (
                '<td' + (celda.clase ? ' class="' + celda.clase + '"' : '') + '>' +
                celda.html +
                '</td>'
              );
            })
            .join('') +
          '</tr>'
        );
      })
      .join('');

    return (
      '<table class="panel-tabla">' +
      '<thead><tr>' + cabecera + '</tr></thead>' +
      '<tbody>' + cuerpoTabla + '</tbody>' +
      '</table>'
    );
  }

  function celda(textoCrudo, clase) {
    return { html: texto(textoCrudo), clase: clase || '' };
  }

  function celdaVacia(clase) {
    return { html: '<span class="sin-dato">—</span>', clase: clase || '' };
  }

  /* ---------------------------------------------------------
     Render de bloques compartidos
     --------------------------------------------------------- */

  function pintarExamenes(nodo, examenes, opciones) {
    const config = opciones || {};
    const inscripciones = Array.isArray(config.inscripciones)
      ? config.inscripciones
      : null;
    const esStaff = Boolean(config.staff);
    const admin = Boolean(usuario) && usuario.rol === 'ADMIN';

    /* El PROFESOR gestiona solo los exámenes de sus sedes asignados a él;
       el backend aplica la misma regla al crear, editar y eliminar. */
    const propias = esStaff
      ? sedesDelStaff().map(function (centro) {
          return Number(centro.centro_id);
        })
      : [];

    const visibles =
      esStaff && !admin
        ? examenes.filter(function (examen) {
            return propias.indexOf(Number(examen.centro_id)) !== -1;
          })
        : examenes;

    if (!visibles.length) {
      nodo.innerHTML = UI.vacio(
        'Sin exámenes programados',
        esStaff
          ? 'Agendá la primera fecha con el botón «Nuevo examen».'
          : 'Cuando la escuela publique nuevas fechas, van a aparecer acá.'
      );
      return;
    }

    nodo.innerHTML = visibles
      .map(function (examen) {
        const profesor = [examen.profesor_nombre, examen.profesor_apellido]
          .filter(Boolean)
          .join(' ');

        const detalles = [
          examen.centro_nombre || 'Sede a confirmar',
          profesor ? 'Prof. ' + profesor : '',
          examen.cantidad_inscriptos
            ? examen.cantidad_inscriptos + ' inscriptos'
            : ''
        ].filter(Boolean);

        const monto = Number(examen.monto);
        const activo =
          examen.activo === undefined || examen.activo === null
            ? true
            : Number(examen.activo) !== 0;

        const gestionable =
          esStaff &&
          activo &&
          (admin ||
            (propias.indexOf(Number(examen.centro_id)) !== -1 &&
              Number(examen.profesor_id) === Number(usuario.profesor_id)));

        let acciones = '';

        if (gestionable) {
          acciones =
            '<div class="panel-acciones-fila">' +
            '<button type="button" class="panel-btn panel-btn-mini" ' +
            'data-accion="editar-examen" data-id="' +
            Number(examen.examen_id) +
            '">Editar</button>' +
            '<button type="button" class="panel-btn panel-btn-mini panel-btn-peligro" ' +
            'data-accion="eliminar-examen" data-id="' +
            Number(examen.examen_id) +
            '">Eliminar</button>' +
            '</div>';
        } else if (esStaff && !activo) {
          acciones =
            '<div class="panel-acciones-fila">' +
            UI.insignia('INACTIVO') +
            '</div>';
        } else if (inscripciones) {
          const inscripcion = inscripciones.filter(function (item) {
            return Number(item.examen_id) === Number(examen.examen_id);
          })[0];

          if (inscripcion) {
            acciones =
              UI.insignia('INSCRIPTO') +
              '<button type="button" class="panel-btn panel-btn-mini" ' +
              'data-accion="cancelar-inscripcion" data-id="' +
              Number(inscripcion.inscripcion_id) +
              '">Cancelar</button>';
          } else {
            acciones =
              '<button type="button" class="panel-btn panel-btn-mini panel-btn-primario" ' +
              'data-accion="inscribir-examen" data-id="' +
              Number(examen.examen_id) +
              '">Inscribirme</button>';
          }
        }

        return (
          '<article class="panel-fila">' +
          fechaBloque(examen.fecha_examen) +
          '<div class="panel-fila-copy">' +
          '<h3>' + texto(examen.titulo || 'Examen') + '</h3>' +
          '<p>' + texto(detalles.join(' · ')) + '</p>' +
          '</div>' +
          '<div class="panel-fila-lado">' +
          (monto > 0 ? '<b>' + UI.moneda(monto) + '</b>' : '') +
          (acciones || UI.insignia('PROGRAMADO')) +
          '</div>' +
          '</article>'
        );
      })
      .join('');
  }

  function pintarNoticias(nodo, noticias, opciones) {
    const config = opciones || {};
    const esStaff = Boolean(config.staff);
    const admin = Boolean(usuario) && usuario.rol === 'ADMIN';

    /* El PROFESOR ve las generales y las de sus sedes; las de otras sedes
       no le corresponden y el backend también las rechaza. */
    const propias = esStaff
      ? sedesDelStaff().map(function (centro) {
          return Number(centro.centro_id);
        })
      : [];

    const visibles =
      esStaff && !admin
        ? noticias.filter(function (noticia) {
            return (
              !noticia.centro_id ||
              propias.indexOf(Number(noticia.centro_id)) !== -1
            );
          })
        : noticias;

    if (!visibles.length) {
      nodo.innerHTML = UI.vacio(
        'Todavía no hay novedades',
        config.staff
          ? 'Publicá la primera noticia para que la vean los alumnos.'
          : 'Las noticias que publique la escuela se van a ver en este bloque.'
      );
      return;
    }

    nodo.innerHTML = visibles
      .map(function (noticia) {
        const activa =
          noticia.activa === undefined || noticia.activa === null
            ? true
            : Number(noticia.activa) !== 0;

        const gestionable =
          esStaff &&
          (admin ||
            (noticia.centro_id &&
              propias.indexOf(Number(noticia.centro_id)) !== -1));

        const detalles = [
          noticia.autor ? 'Por ' + noticia.autor : '',
          noticia.centro || 'General'
        ].filter(Boolean);

        const imagen = noticia.imagen_url
          ? '<img class="panel-noticia-img" src="' +
            UI.escapar(noticia.imagen_url) +
            '" alt="" loading="lazy" />'
          : '';

        let lado = '';

        if (gestionable && activa) {
          lado =
            '<div class="panel-acciones-fila">' +
            '<button type="button" class="panel-btn panel-btn-mini" ' +
            'data-accion="editar-noticia" data-id="' +
            Number(noticia.id) +
            '">Editar</button>' +
            '<button type="button" class="panel-btn panel-btn-mini panel-btn-peligro" ' +
            'data-accion="eliminar-noticia" data-id="' +
            Number(noticia.id) +
            '">Eliminar</button>' +
            '</div>';
        } else if (esStaff && !activa) {
          lado =
            '<div class="panel-acciones-fila">' +
            UI.insignia('INACTIVA') +
            '</div>';
        }

        return (
          '<article class="panel-fila panel-fila-noticia">' +
          fechaBloque(noticia.fecha_publicacion) +
          '<div class="panel-fila-copy">' +
          '<h3>' + texto(noticia.titulo || 'Novedad') + '</h3>' +
          '<p class="panel-noticia-texto">' +
          texto(noticia.contenido || '') +
          '</p>' +
          '<p>' + texto(detalles.join(' · ')) + '</p>' +
          imagen +
          '</div>' +
          (lado
            ? '<div class="panel-fila-lado">' + lado + '</div>'
            : '') +
          '</article>'
        );
      })
      .join('');
  }

  /* ---------------------------------------------------------
     Sedes (solo ADMIN)
     --------------------------------------------------------- */

  function pintarSedes(nodo, centros) {
    if (!centros.length) {
      nodo.innerHTML = UI.vacio(
        'Todavía no hay sedes',
        'Creá la primera con el botón «Nueva sede».'
      );
      return;
    }

    /* Activas primero y, dentro de cada grupo, por nombre. */
    const ordenadas = centros.slice().sort(function (a, b) {
      const bajaA = Number(a.activo) === 0 ? 1 : 0;
      const bajaB = Number(b.activo) === 0 ? 1 : 0;

      if (bajaA !== bajaB) {
        return bajaA - bajaB;
      }

      return String(a.nombre || '').localeCompare(String(b.nombre || ''), 'es');
    });

    nodo.innerHTML = ordenadas
      .map(function (centro) {
        const activa =
          centro.activo === undefined || centro.activo === null
            ? true
            : Number(centro.activo) !== 0;

        const detalles = [centro.direccion, centro.telefono]
          .filter(Boolean)
          .join(' · ');

        const inicial = String(centro.nombre || 'S')
          .trim()
          .charAt(0)
          .toUpperCase();

        const acciones = activa
          ? '<button type="button" class="panel-btn panel-btn-mini" ' +
            'data-accion="editar-sede" data-id="' +
            Number(centro.centro_id) +
            '">Editar</button>' +
            '<button type="button" class="panel-btn panel-btn-mini panel-btn-peligro" ' +
            'data-accion="eliminar-sede" data-id="' +
            Number(centro.centro_id) +
            '">Dar de baja</button>'
          : UI.insignia('INACTIVA') +
            '<button type="button" class="panel-btn panel-btn-mini" ' +
            'data-accion="reactivar-sede" data-id="' +
            Number(centro.centro_id) +
            '">Reactivar</button>';

        return (
          '<article class="panel-fila">' +
          '<span class="panel-sede-marca" aria-hidden="true">' +
          texto(inicial) +
          '</span>' +
          '<div class="panel-fila-copy">' +
          '<h3>' + texto(centro.nombre || 'Sede') + '</h3>' +
          '<p>' +
          texto(detalles || 'Sin dirección ni teléfono cargados') +
          '</p>' +
          '</div>' +
          '<div class="panel-fila-lado">' +
          '<div class="panel-acciones-fila">' +
          acciones +
          '</div>' +
          '</div>' +
          '</article>'
        );
      })
      .join('');
  }

  /* ---------------------------------------------------------
     Chat por sede
     --------------------------------------------------------- */

  function sedesDelStaff() {
    if (!usuario) {
      return [];
    }

    if (usuario.rol === 'ADMIN') {
      return centrosCache;
    }

    const propio = profesoresCache.filter(function (profesor) {
      return Number(profesor.profesor_id) === Number(usuario.profesor_id);
    })[0];

    const ids = ((propio && propio.centros) || []).map(function (centro) {
      return Number(centro.centro_id);
    });

    return centrosCache.filter(function (centro) {
      return ids.indexOf(Number(centro.centro_id)) !== -1;
    });
  }

  function pintarChat(nodo, mensajes) {
    if (!mensajes.length) {
      nodo.innerHTML = UI.vacio(
        'Sin mensajes todavía',
        'Escribí el primero para empezar la conversación con la escuela.'
      );
      return;
    }

    const personaId = Number(usuario && usuario.persona_id);

    nodo.innerHTML = mensajes
      .map(function (mensaje) {
        const propio =
          Boolean(personaId) &&
          Number(mensaje.emisor_persona_id) === personaId;

        const nombre = [mensaje.emisor_nombre, mensaje.emisor_apellido]
          .filter(Boolean)
          .join(' ');

        const rol = mensaje.rol
          ? etiquetaRol(String(mensaje.rol).toUpperCase())
          : '';

        const avatar = mensaje.emisor_avatar
          ? '<img src="' + UI.escapar(mensaje.emisor_avatar) + '" alt="" />'
          : UI.escapar(
              UI.iniciales(mensaje.emisor_nombre, mensaje.emisor_apellido)
            );

        return (
          '<article class="chat-mensaje' +
          (propio ? ' chat-mensaje-propio' : '') +
          '">' +
          '<span class="chat-avatar" aria-hidden="true">' +
          avatar +
          '</span>' +
          '<div class="chat-burbuja">' +
          '<header class="chat-cabeza">' +
          '<strong>' + texto(nombre || 'Usuario') + '</strong>' +
          (propio
            ? '<span class="chat-etiqueta">Vos</span>'
            : rol
              ? '<span class="chat-etiqueta">' + texto(rol) + '</span>'
              : '') +
          '<time datetime="' + UI.escapar(mensaje.fecha_hora || '') + '">' +
          texto(fechaHora(mensaje.fecha_hora)) +
          '</time>' +
          '</header>' +
          '<p>' + texto(mensaje.mensaje || '') + '</p>' +
          '</div>' +
          '</article>'
        );
      })
      .join('');

    nodo.scrollTop = nodo.scrollHeight;
  }

  function cargandoChat() {
    return (
      '<div class="cargando-filas" aria-hidden="true">' +
      '<span class="cargando-fila"></span>' +
      '<span class="cargando-fila"></span>' +
      '</div>'
    );
  }

  async function cargarChatAlumno() {
    const nodo = $('#al-chat');
    const nota = $('#al-chat-nota');
    const form = $('#form-chat-alumno');

    if (!nodo) {
      return;
    }

    const centroId = perfilCache.centro_id;

    if (nota) {
      nota.textContent = perfilCache.centro_nombre || 'Canal de tu sede';
    }

    if (!centroId) {
      if (form) {
        form.hidden = true;
      }

      nodo.innerHTML = UI.vacio(
        'Sin sede asignada',
        'Cuando la escuela te asigne una sede vas a poder escribir acá.'
      );
      return;
    }

    if (form) {
      form.hidden = false;
    }

    nodo.innerHTML = cargandoChat();

    const res = await API.get('/api/chat/centro/' + Number(centroId));

    if (API.sesionInvalida(res)) {
      sesionCaida = true;
      return;
    }

    if (!res.ok) {
      nodo.innerHTML = UI.vacio(
        'No pudimos cargar los mensajes',
        API.mensaje(res)
      );
      return;
    }

    pintarChat(nodo, lista(res.data, 'mensajes'));
  }

  async function cargarChatStaff() {
    const select = $('#chat-centro');
    const nodo = $('#st-chat');
    const form = $('#form-chat-staff');

    if (!select || !nodo) {
      return;
    }

    const sedes = sedesDelStaff();

    if (!sedes.length) {
      select.innerHTML = '<option value="">Sin sedes</option>';
      select.disabled = true;

      if (form) {
        form.hidden = true;
      }

      nodo.innerHTML = UI.vacio(
        'Sin sedes asignadas',
        'Cuando tengas una sede asignada vas a poder ver y enviar mensajes.'
      );
      return;
    }

    const anterior = Number(chatCentroId || select.value);

    select.disabled = false;

    if (form) {
      form.hidden = false;
    }

    select.innerHTML = sedes
      .map(function (centro) {
        return (
          '<option value="' +
          Number(centro.centro_id) +
          '">' +
          texto(centro.nombre) +
          '</option>'
        );
      })
      .join('');

    const elegida =
      sedes.filter(function (centro) {
        return Number(centro.centro_id) === anterior;
      })[0] || sedes[0];

    select.value = String(elegida.centro_id);
    chatCentroId = Number(elegida.centro_id);

    await cargarMensajesStaff();
  }

  async function cargarMensajesStaff() {
    const nodo = $('#st-chat');
    const select = $('#chat-centro');

    if (!nodo || !select) {
      return;
    }

    const centroId = Number(select.value);

    if (!centroId) {
      return;
    }

    chatCentroId = centroId;
    nodo.innerHTML = cargandoChat();

    const res = await API.get('/api/chat/centro/' + centroId);

    if (API.sesionInvalida(res)) {
      sesionCaida = true;
      return;
    }

    if (!res.ok) {
      nodo.innerHTML = UI.vacio(
        'No pudimos cargar los mensajes',
        API.mensaje(res)
      );
      return;
    }

    pintarChat(nodo, lista(res.data, 'mensajes'));
  }

  async function enviarMensajeChat(form, campo, centroId) {
    if (!form || !campo) {
      return;
    }

    const mensaje = campo.value.trim();

    if (!centroId) {
      UI.avisar('No hay una sede asignada para enviar el mensaje.', 'aviso');
      return;
    }

    if (!mensaje) {
      campo.focus();
      return;
    }

    const boton = form.querySelector('button[type="submit"]');

    if (boton) {
      boton.disabled = true;
    }

    const res = await API.post('/api/chat', {
      centro_id: Number(centroId),
      mensaje: mensaje
    });

    if (boton) {
      boton.disabled = false;
    }

    if (API.sesionInvalida(res)) {
      sesionCaida = true;
      API.limpiarSesion();
      API.irALogin('expirado');
      return;
    }

    if (!res.ok) {
      UI.avisar(API.mensaje(res), 'error');
      return;
    }

    campo.value = '';
    campo.focus();

    if (usuario && esStaff(usuario.rol)) {
      await cargarMensajesStaff();
    } else {
      await cargarChatAlumno();
    }
  }

  function pintarTablaCuotas(nodo, cuotas) {
    if (!cuotas.length) {
      nodo.innerHTML = UI.vacio(
        'Sin cuotas registradas',
        'Cuando la administración genere tus cuotas, vas a verlas acá.'
      );
      return;
    }

    const filas = cuotas.map(function (cuota) {
      return [
        celda(periodo(cuota), 'fuerte'),
        celda(fecha(cuota.fecha_vencimiento)),
        celda(UI.moneda(cuota.monto), 'num'),
        { html: UI.insignia(cuota.estado), clase: 'num' }
      ];
    });

    nodo.innerHTML = tabla(
      [
        { titulo: 'Período' },
        { titulo: 'Vencimiento' },
        { titulo: 'Monto', clase: 'num' },
        { titulo: 'Estado', clase: 'num' }
      ],
      filas
    );
  }

  function pintarTablaAsistencias(nodo, asistencias) {
    if (!asistencias.length) {
      nodo.innerHTML = UI.vacio(
        'Sin asistencias registradas',
        'Cuando tu profesor tome lista, las clases van a aparecer acá.'
      );
      return;
    }

    const filas = asistencias.map(function (asistencia) {
      const presente = Boolean(asistencia.presente);

      return [
        celda(fecha(asistencia.fecha), 'fuerte'),
        {
          html: UI.insignia(presente ? 'PRESENTE' : 'AUSENTE'),
          clase: 'num'
        },
        asistencia.observacion
          ? celda(asistencia.observacion, 'tenue')
          : celdaVacia('tenue')
      ];
    });

    nodo.innerHTML = tabla(
      [
        { titulo: 'Fecha' },
        { titulo: 'Estado', clase: 'num' },
        { titulo: 'Observación' }
      ],
      filas
    );
  }

  function pintarTablaPagos(nodo, pagos) {
    if (!pagos.length) {
      nodo.innerHTML = UI.vacio(
        'Sin pagos registrados',
        'Los pagos que registre la escuela aparecen en este listado.'
      );
      return;
    }

    const filas = pagos.map(function (pago) {
      const concepto =
        '<span class="fuerte">' +
        texto(pago.tipo_concepto || 'Pago') +
        '</span>' +
        (pago.descripcion
          ? '<br /><span class="tenue">' + texto(pago.descripcion) + '</span>'
          : '');

      return [
        celda(fecha(pago.fecha_registro)),
        { html: concepto },
        celda(pago.metodo_pago || '—', 'tenue'),
        celda(UI.moneda(pago.monto), 'num'),
        { html: UI.insignia(pago.estado), clase: 'num' }
      ];
    });

    nodo.innerHTML = tabla(
      [
        { titulo: 'Registrado' },
        { titulo: 'Concepto' },
        { titulo: 'Método' },
        { titulo: 'Monto', clase: 'num' },
        { titulo: 'Estado', clase: 'num' }
      ],
      filas
    );
  }

  /* ---------------------------------------------------------
     Cabecera
     --------------------------------------------------------- */

  function pintarAvatar(url) {
    if (!panelAvatar) {
      return;
    }

    if (url) {
      panelAvatar.classList.add('con-foto');
      panelAvatar.innerHTML =
        '<img src="' + UI.escapar(url) + '" alt="" loading="lazy" />';
    } else {
      panelAvatar.classList.remove('con-foto');
      panelAvatar.textContent = UI.iniciales(usuario.nombre, usuario.apellido);
    }
  }

  function pintarUsuario() {
    const nombreCompleto = [usuario.nombre, usuario.apellido]
      .filter(Boolean)
      .join(' ');

    panelNombre.textContent = nombreCompleto || usuario.usuario || 'Usuario';
    panelRol.textContent = etiquetaRol(usuario.rol);
    pintarAvatar(usuario.avatar);
  }

  /* Refresca el header cuando el perfil se edita sin recargar la página. */
  function sincronizarPerfil(perfil) {
    if (!perfil) {
      return;
    }

    usuario = Object.assign({}, usuario, {
      nombre: perfil.nombre || usuario.nombre,
      apellido: perfil.apellido || usuario.apellido,
      email: perfil.email || usuario.email,
      avatar: perfil.avatar || null
    });

    const nombreCompleto = [usuario.nombre, usuario.apellido]
      .filter(Boolean)
      .join(' ');

    panelNombre.textContent = nombreCompleto || usuario.usuario || 'Usuario';
    pintarAvatar(perfil.avatar);

    API.actualizarUsuario({
      nombre: usuario.nombre,
      apellido: usuario.apellido,
      email: usuario.email,
      avatar: usuario.avatar
    });
  }

  function mostrarAlerta(mensaje, tipo) {
    UI.mostrarMensaje(alerta, mensaje, tipo || 'error');
  }

  /* ---------------------------------------------------------
     VISTA ALUMNO
     --------------------------------------------------------- */

  function kpi(alumno, pie) {
    return { valor: alumno, pie: pie };
  }

  function pintarKpiAlumno(id, datos) {
    document.getElementById(id).textContent = datos.valor;
    document.getElementById(id + '-pie').textContent = datos.pie;
  }

  async function cargarAlumno() {
    const alumnoId = usuario.alumno_id;

    const pedidos = {
      perfil: API.get('/api/perfil'),
      examenes: API.get('/api/examenes/proximos')
    };

    /* Sin ficha de alumno no tiene sentido pedir "mis" listados:
       esos endpoints necesitan el alumno_id. */
    if (alumnoId) {
      pedidos.asistencias = API.get('/api/asistencias/alumno/' + alumnoId);
      pedidos.cuotas = API.get('/api/cuotas/alumno/' + alumnoId);
      pedidos.pagos = API.get('/api/pagos/alumno/' + alumnoId);
      pedidos.graduaciones = API.get('/api/graduaciones/alumno/' + alumnoId);
      pedidos.inscripciones = API.get('/api/examenes/mis-inscripciones');
    }

    const claves = Object.keys(pedidos);

    const respuestas = await Promise.allSettled(
      claves.map(function (clave) {
        return pedidos[clave];
      })
    );

    const datos = {};

    respuestas.forEach(function (respuesta, indice) {
      datos[claves[indice]] =
        respuesta.status === 'fulfilled' ? cuerpo(respuesta.value) : null;
    });

    if (sesionCaida) {
      return;
    }

    if (!datos.perfil) {
      mostrarAlerta(
        'No pudimos cargar tu ficha desde el servidor (' +
          API.base +
          '). Probá con "Actualizar" en un momento.',
        'error'
      );
    }

    const perfil =
      (datos.perfil && datos.perfil.perfil) || {};

    perfilCache = perfil;
    sincronizarPerfil(perfil);

    /* Las novedades se piden después del perfil: el alumno solo ve las
       generales y las de su sede. */
    const respuestaNoticias = perfil.centro_id
      ? await API.get('/api/noticias/centro/' + Number(perfil.centro_id))
      : await API.get('/api/noticias');

    if (sesionCaida) {
      return;
    }

    const asistencias = lista(datos.asistencias, 'asistencias');
    const cuotas = lista(datos.cuotas, 'cuotas');
    const pagos = lista(datos.pagos, 'pagos');
    const graduaciones = lista(datos.graduaciones, 'graduaciones');
    const examenes = lista(datos.examenes, 'examenes');
    const noticias = lista(cuerpo(respuestaNoticias), 'noticias');
    const inscripciones = lista(datos.inscripciones, 'inscripciones');

    cuotasCache = cuotas;
    pagosCache = pagos;
    examenesCache = examenes;
    inscripcionesCache = inscripciones;
    noticiasCache = noticias;

    /* --- Hero --- */

    $('#alumno-nombre').textContent =
      perfil.nombre || usuario.nombre || 'alumno';

    $('#alumno-sede').textContent = perfil.centro_nombre || 'Sin sede asignada';

    const profe = [perfil.profesor_nombre, perfil.profesor_apellido]
      .filter(Boolean)
      .join(' ');

    $('#alumno-profesor').textContent = profe || 'Sin profesor asignado';
    $('#alumno-desde').textContent = fecha(perfil.fecha_de_inicio);

    if (!alumnoId) {
      mostrarAlerta(
        'Tu usuario todavía no está vinculado a una ficha de alumno. ' +
          'Pedile a la administración que lo asocie para ver tus cuotas y asistencias.',
        'aviso'
      );
    }

    /* --- KPIs --- */

    const presentes = asistencias.filter(function (asistencia) {
      return Boolean(asistencia.presente);
    }).length;

    pintarKpiAlumno(
      'kpi-asistencias',
      kpi(
        asistencias.length
          ? Math.round((presentes / asistencias.length) * 100) + '%'
          : '—',
        asistencias.length
          ? presentes + ' de ' + asistencias.length + ' clases registradas'
          : 'Sin asistencias registradas'
      )
    );

    const abiertas = cuotas.filter(esAbierta);
    const montoAbierto = sumar(abiertas, 'monto');

    pintarKpiAlumno(
      'kpi-cuotas',
      kpi(
        String(abiertas.length),
        cuotas.length
          ? abiertas.length
            ? UI.moneda(montoAbierto) + ' por regularizar'
            : 'Estás al día con tus cuotas'
          : 'Sin cuotas generadas'
      )
    );

    const confirmados = pagos.filter(function (pago) {
      return estadoPago(pago) === 'CONFIRMADO';
    });
    const montoPagado = sumar(confirmados, 'monto');

    pintarKpiAlumno(
      'kpi-pagos',
      kpi(
        String(confirmados.length),
        confirmados.length
          ? UI.moneda(montoPagado) + ' abonados'
          : 'Sin pagos confirmados'
      )
    );

    pintarKpiAlumno(
      'kpi-graduaciones',
      kpi(
        String(graduaciones.length),
        graduaciones.length
          ? 'Último grado: ' + (graduaciones[0].grado || '—')
          : 'Todavía sin graduaciones'
      )
    );

    /* --- Listados --- */

    pintarExamenes($('#al-examenes'), examenes, {
      inscripciones: inscripciones
    });
    pintarNoticias($('#al-noticias'), noticias);
    pintarTablaAsistencias($('#al-asistencias'), asistencias);
    pintarTablaCuotas($('#al-cuotas'), cuotas);
    pintarTablaPagos($('#al-pagos'), pagos);

    const presentesClases = asistencias.filter(function (asistencia) {
      return Boolean(asistencia.presente);
    }).length;

    $('#al-asistencias-nota').textContent = asistencias.length
      ? presentesClases +
        ' de ' +
        asistencias.length +
        ' clases · ' +
        Math.round((presentesClases / asistencias.length) * 100) +
        '%'
      : '';

    $('#al-cuotas-nota').textContent = cuotas.length
      ? cuotas.length + (cuotas.length === 1 ? ' cuota' : ' cuotas')
      : '';

    $('#al-pagos-nota').textContent = pagos.length
      ? pagos.length + (pagos.length === 1 ? ' pago' : ' pagos')
      : '';

    await cargarChatAlumno();

    /* --- Graduaciones --- */

    const nodoGraduaciones = $('#al-graduaciones');

    if (!graduaciones.length) {
      nodoGraduaciones.innerHTML = UI.vacio(
        'Todavía sin graduaciones',
        'Cada grado alcanzado va a quedar registrado en esta lista.'
      );
    } else {
      nodoGraduaciones.innerHTML = graduaciones
        .map(function (graduacion) {
          return (
            '<article class="panel-fila">' +
            fechaBloque(graduacion.fecha) +
            '<div class="panel-fila-copy">' +
            '<h3>' + texto(graduacion.grado || 'Grado') + '</h3>' +
            '<p>' + texto(graduacion.centro_nombre || 'Sede') + '</p>' +
            '</div>' +
            '<div class="panel-fila-lado">' +
            (partesFecha(graduacion.fecha)
              ? '<b>' + partesFecha(graduacion.fecha).anio + '</b>'
              : '') +
            '</div>' +
            '</article>'
          );
        })
        .join('');
    }

    /* --- Datos personales --- */

    const datosPersonales = [
      ['Documento', perfil.dni],
      ['Email', perfil.email],
      ['Usuario', perfil.usuario || usuario.usuario],
      ['Teléfono', perfil.telefono],
      ['Nacimiento', fecha(perfil.fecha_nacimiento)],
      ['Emergencia', perfil.contacto_emergencia]
    ];

    $('#al-datos').innerHTML =
      datosPersonales
        .map(function (fila) {
          return (
            '<div>' +
            '<dt>' + UI.escapar(fila[0]) + '</dt>' +
            '<dd>' + texto(fila[1]) + '</dd>' +
            '</div>'
          );
        })
        .join('') +
      '<div><dt>Estado</dt><dd>' +
      UI.insignia(perfil.alumno_estado || (perfil.persona_activa ? 'ACTIVO' : 'INACTIVO')) +
      '</dd></div>';
  }

  /* ---------------------------------------------------------
     VISTA PROFESOR / ADMIN
     --------------------------------------------------------- */

  function pintarKpiStaff(id, valor, pie) {
    document.getElementById(id).textContent = valor;
    document.getElementById(id + '-pie').textContent = pie;
  }

  function pintarTablaAlumnos(alumnos, busqueda) {
    const nodo = $('#st-alumnos');
    const termino = (busqueda || '').trim().toLowerCase();

    const filtrados = alumnos.filter(function (alumno) {
      if (!termino) {
        return true;
      }

      const textoBuscable = [
        alumno.nombre,
        alumno.apellido,
        alumno.dni,
        alumno.email,
        alumno.usuario,
        alumno.centro_nombre,
        alumno.profesor_nombre,
        alumno.profesor_apellido
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();

      return textoBuscable.indexOf(termino) !== -1;
    });

    $('#st-alumnos-nota').textContent = termino
      ? filtrados.length + ' de ' + alumnos.length + ' alumnos'
      : alumnos.length +
        (alumnos.length === 1 ? ' alumno registrado' : ' alumnos registrados');

    if (!filtrados.length) {
      nodo.innerHTML = UI.vacio(
        termino ? 'Sin resultados' : 'Todavía no hay alumnos',
        termino
          ? 'Probá con otro nombre, DNI, sede o profesor.'
          : 'Cuando se registren alumnos van a aparecer en este listado.'
      );
      return;
    }

    const filas = filtrados.map(function (alumno) {
      const profe = [alumno.profesor_nombre, alumno.profesor_apellido]
        .filter(Boolean)
        .join(' ');

      const persona =
        '<div class="panel-persona">' +
        '<span class="panel-persona-avatar" aria-hidden="true">' +
        UI.escapar(UI.iniciales(alumno.nombre, alumno.apellido)) +
        '</span>' +
        '<span class="panel-persona-copy">' +
        '<strong>' +
        texto([alumno.nombre, alumno.apellido].filter(Boolean).join(' ')) +
        '</strong>' +
        (alumno.email
          ? '<small>' + texto(alumno.email) + '</small>'
          : '') +
        '</span>' +
        '</div>';

      const acciones =
        '<div class="panel-acciones-fila">' +
        '<button type="button" class="panel-btn panel-btn-mini" ' +
        'data-accion="ficha-alumno" data-id="' +
        Number(alumno.alumno_id) +
        '">Ficha</button>' +
        '<button type="button" class="panel-btn panel-btn-mini" ' +
        'data-accion="editar-alumno" data-id="' +
        Number(alumno.alumno_id) +
        '">Editar</button>' +
        '</div>';

      return [
        { html: persona },
        alumno.dni ? celda(alumno.dni) : celdaVacia(),
        alumno.centro_nombre ? celda(alumno.centro_nombre) : celdaVacia(),
        profe ? celda(profe) : celdaVacia(),
        { html: UI.insignia(alumno.estado), clase: 'num' },
        celda(fecha(alumno.fecha_de_inicio || alumno.fecha_alta), 'tenue'),
        { html: acciones, clase: 'num' }
      ];
    });

    nodo.innerHTML = tabla(
      [
        { titulo: 'Alumno' },
        { titulo: 'DNI' },
        { titulo: 'Sede' },
        { titulo: 'Profesor' },
        { titulo: 'Estado', clase: 'num' },
        { titulo: 'Desde', clase: 'num' },
        { titulo: 'Acciones', clase: 'num' }
      ],
      filas
    );
  }

  function pintarTablaPendientes(pagos) {
    const nodo = $('#st-pagos');
    const pendientes = pagos.filter(function (pago) {
      return estadoPago(pago) !== 'CONFIRMADO';
    });

    $('#st-pagos-nota').textContent = pendientes.length
      ? UI.moneda(sumar(pendientes, 'monto')) + ' a cobrar'
      : '';

    if (!pendientes.length) {
      nodo.innerHTML = UI.vacio(
        'Sin pagos pendientes',
        'Todos los pagos registrados están confirmados.'
      );
      return;
    }

    const filas = pendientes.map(function (pago) {
      const alumno = [pago.alumno_nombre, pago.alumno_apellido]
        .filter(Boolean)
        .join(' ');

      const acciones =
        '<div class="panel-acciones-fila">' +
        (pago.alumno_id
          ? '<button type="button" class="panel-btn panel-btn-mini" ' +
            'data-accion="ficha-alumno" data-id="' +
            Number(pago.alumno_id) +
            '">Ficha</button>'
          : '') +
        (usuario.rol === 'ADMIN' && pago.pago_id
          ? '<button type="button" class="panel-btn panel-btn-mini panel-btn-primario" ' +
            'data-accion="confirmar-pago" data-id="' +
            Number(pago.pago_id) +
            '">Confirmar</button>'
          : '') +
        '</div>';

      return [
        alumno ? celda(alumno, 'fuerte') : celdaVacia('fuerte'),
        celda(pago.tipo_concepto || 'Pago'),
        celda(UI.moneda(pago.monto), 'num'),
        celda(fecha(pago.fecha_registro), 'tenue'),
        { html: UI.insignia(pago.estado), clase: 'num' },
        { html: acciones, clase: 'num' }
      ];
    });

    nodo.innerHTML = tabla(
      [
        { titulo: 'Alumno' },
        { titulo: 'Concepto' },
        { titulo: 'Monto', clase: 'num' },
        { titulo: 'Registrado', clase: 'num' },
        { titulo: 'Estado', clase: 'num' },
        { titulo: 'Acciones', clase: 'num' }
      ],
      filas
    );
  }

  async function cargarStaff() {
    const pedidos = {
      perfil: API.get('/api/perfil'),
      alumnos: API.get('/api/alumnos'),
      profesores: API.get('/api/profesores?todos=true'),
      centros: API.get('/api/centros?todos=true'),
      pagos: API.get('/api/pagos/pendientes'),
      examenes: API.get('/api/examenes/?todos=true'),
      noticias: API.get('/api/noticias?todos=true')
    };

    const claves = Object.keys(pedidos);

    const respuestas = await Promise.allSettled(
      claves.map(function (clave) {
        return pedidos[clave];
      })
    );

    const datos = {};

    respuestas.forEach(function (respuesta, indice) {
      datos[claves[indice]] =
        respuesta.status === 'fulfilled' ? cuerpo(respuesta.value) : null;
    });

    if (sesionCaida) {
      return;
    }

    if (!datos.alumnos) {
      mostrarAlerta(
        'No pudimos cargar el listado de alumnos desde ' +
          API.base +
          '. Probá con "Actualizar" en un momento.',
        'error'
      );
    }

    const perfil = (datos.perfil && datos.perfil.perfil) || {};
    perfilCache = perfil;
    sincronizarPerfil(perfil);

    alumnosCache = lista(datos.alumnos, 'alumnos');

    const profesores = lista(datos.profesores, 'profesores');
    const centros = lista(datos.centros, 'centros');
    const pagos = lista(datos.pagos, 'pagos');
    const examenes = lista(datos.examenes, 'examenes');
    const noticias = lista(datos.noticias, 'noticias');

    profesoresCache = profesores;
    centrosCache = centros;
    pagosCache = pagos;
    examenesCache = examenes;
    noticiasCache = noticias;

    const esAdmin = usuario.rol === 'ADMIN';

    /* --- Hero --- */

    $('#staff-kicker').textContent = esAdmin
      ? 'Administración'
      : 'Portal del profesor';

    $('#staff-nombre').textContent =
      perfil.nombre || usuario.nombre || 'equipo';

    $('#staff-bajada').textContent = esAdmin
      ? 'El estado de la escuela de un vistazo: alumnos, sedes, cobros y las novedades que estás publicando.'
      : 'Tus alumnos, la agenda de exámenes y los cobros pendientes de la escuela.';

    $('#staff-rol').textContent = etiquetaRol(usuario.rol);
    $('#staff-usuario').textContent = usuario.usuario
      ? '@' + usuario.usuario
      : '—';
    $('#staff-hoy').textContent = fechaHoy();

    /* --- KPIs --- */

    const alumnosActivos = alumnosCache.filter(function (alumno) {
      return String(alumno.estado || '').toUpperCase() === 'ACTIVO';
    }).length;

    pintarKpiStaff(
      'kpi-alumnos',
      String(alumnosCache.length),
      alumnosActivos + (alumnosActivos === 1 ? ' activo' : ' activos')
    );

    const profesoresActivos = profesores.filter(function (profesor) {
      return Boolean(profesor.profesor_activo);
    }).length;

    pintarKpiStaff(
      'kpi-profesores',
      String(profesores.length),
      profesoresActivos + (profesoresActivos === 1 ? ' activo' : ' activos')
    );

    const sedesActivas = centros.filter(function (centro) {
      return Boolean(centro.activo);
    }).length;

    pintarKpiStaff(
      'kpi-sedes',
      String(centros.length),
      sedesActivas + (sedesActivas === 1 ? ' activa' : ' activas')
    );

    const pendientes = pagos.filter(function (pago) {
      return estadoPago(pago) !== 'CONFIRMADO';
    });

    pintarKpiStaff(
      'kpi-pendientes',
      String(pendientes.length),
      pendientes.length
        ? UI.moneda(sumar(pendientes, 'monto')) + ' a cobrar'
        : 'Sin cobros pendientes'
    );

    /* --- Sedes (solo ADMIN) --- */

    const tarjetaSedes = $('#st-sedes-card');

    if (tarjetaSedes) {
      tarjetaSedes.hidden = !esAdmin;
    }

    if (esAdmin) {
      pintarSedes($('#st-sedes'), centros);

      const notaSedes = $('#st-sedes-nota');

      if (notaSedes) {
        notaSedes.textContent =
          centros.length + (centros.length === 1 ? ' sede' : ' sedes');
      }
    }

    /* --- Listados --- */

    pintarTablaAlumnos(alumnosCache, $('#buscar-alumnos').value);
    pintarTablaPendientes(pagos);
    pintarExamenes($('#st-examenes'), examenes, { staff: true });
    pintarNoticias($('#st-noticias'), noticias, { staff: true });

    await cargarChatStaff();
  }

  /* ---------------------------------------------------------
     Arranque
     --------------------------------------------------------- */

  function mostrarVista(rol) {
    if (esStaff(rol)) {
      vistaStaff.hidden = false;
      vistaAlumno.hidden = true;
    } else {
      vistaAlumno.hidden = false;
      vistaStaff.hidden = true;
    }
  }

  function terminarCarga() {
    esqueleto.hidden = true;
    btnRecargar.disabled = false;
  }

  async function cargarVista() {
    if (!usuario) {
      return;
    }

    if (esStaff(usuario.rol)) {
      await cargarStaff();
    } else {
      await cargarAlumno();
    }
  }

  /* Vuelve a pedir los datos de la vista actual. La usan las acciones
     después de guardar, para que las tablas queden al día. */
  async function recargar(silencioso) {
    if (!usuario) {
      return false;
    }

    UI.ocultarMensaje(alerta);
    await cargarVista();

    if (sesionCaida) {
      API.limpiarSesion();
      API.irALogin('expirado');
      return false;
    }

    if (!silencioso) {
      UI.avisar('Datos actualizados.', 'ok');
    }

    return true;
  }

  async function iniciar() {
    if (!API.requerirSesion()) {
      return;
    }

    const sesion = await API.auth.me();

    if (!sesion.ok) {
      const tokenViejo = API.sesionInvalida(sesion);

      API.limpiarSesion();
      API.irALogin(tokenViejo ? 'expirado' : 'sin-sesion');
      return;
    }

    usuario = sesion.data.usuario;

    pintarUsuario();
    mostrarVista(usuario.rol);
    terminarCarga();

    await cargarVista();

    if (sesionCaida) {
      API.limpiarSesion();
      API.irALogin('expirado');
    }
  }

  /* ---------------------------------------------------------
     Eventos
     --------------------------------------------------------- */

  btnSalir.addEventListener('click', function () {
    API.cerrarSesion();
  });

  btnRecargar.addEventListener('click', async function () {
    if (!usuario || btnRecargar.disabled) {
      return;
    }

    btnRecargar.disabled = true;

    await recargar(false);

    btnRecargar.disabled = false;
  });

  $('#buscar-alumnos').addEventListener('input', function (evento) {
    if (!alumnosCache.length) {
      return;
    }

    pintarTablaAlumnos(alumnosCache, evento.target.value);
  });

  const formChatAlumno = $('#form-chat-alumno');
  const formChatStaff = $('#form-chat-staff');
  const selectChatCentro = $('#chat-centro');

  if (formChatAlumno) {
    formChatAlumno.addEventListener('submit', function (evento) {
      evento.preventDefault();
      enviarMensajeChat(
        formChatAlumno,
        $('#chat-alumno-mensaje'),
        perfilCache.centro_id
      );
    });
  }

  if (formChatStaff) {
    formChatStaff.addEventListener('submit', function (evento) {
      evento.preventDefault();
      enviarMensajeChat(
        formChatStaff,
        $('#chat-staff-mensaje'),
        chatCentroId
      );
    });
  }

  if (selectChatCentro) {
    selectChatCentro.addEventListener('change', function () {
      chatCentroId = Number(selectChatCentro.value);
      cargarMensajesStaff();
    });
  }

  /* Las acciones del panel (js/panel-acciones.js) leen los datos ya
     cargados y piden un refresco después de cada escritura. */
  window.Panel = {
    usuario: function () {
      return usuario;
    },
    perfil: function () {
      return perfilCache;
    },
    alumnos: function () {
      return alumnosCache;
    },
    cuotas: function () {
      return cuotasCache;
    },
    pagos: function () {
      return pagosCache;
    },
    examenes: function () {
      return examenesCache;
    },
    inscripciones: function () {
      return inscripcionesCache;
    },
    centros: function () {
      return centrosCache;
    },
    profesores: function () {
      return profesoresCache;
    },
    noticias: function () {
      return noticiasCache;
    },
    fijarCatalogos: function (centros, profesores) {
      if (Array.isArray(centros)) {
        centrosCache = centros;
      }

      if (Array.isArray(profesores)) {
        profesoresCache = profesores;
      }
    },
    recargar: recargar,
    mostrarAlerta: mostrarAlerta
  };

  iniciar();
})();
