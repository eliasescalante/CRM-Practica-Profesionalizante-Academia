/* =========================================================
   Tien Long Hu - Panel: piezas de interfaz
   ---------------------------------------------------------
   Modal, drawer, confirmación y helpers para armar los
   formularios de las acciones del panel. No conoce la API:
   solo abre, cierra, enfoca y devuelve los nodos.
   ========================================================= */

const PanelUI = (function () {
  'use strict';

  const $ = UI.qs;

  const modalFondo = $('#modal-fondo');
  const modalCaja = $('.modal-caja', modalFondo);
  const modalKicker = $('#modal-kicker');
  const modalTitulo = $('#modal-titulo');
  const modalCuerpo = $('#modal-cuerpo');
  const modalPie = $('#modal-pie');
  const modalCerrar = $('#modal-cerrar');

  const drawerFondo = $('#drawer-fondo');
  const drawerCaja = $('.panel-drawer', drawerFondo);
  const drawerKicker = $('#drawer-kicker');
  const drawerTitulo = $('#drawer-titulo');
  const drawerCuerpo = $('#drawer-cuerpo');
  const drawerCerrar = $('#drawer-cerrar');

  const confirmarFondo = $('#confirmar-fondo');
  const confirmarTitulo = $('#confirmar-titulo');
  const confirmarTexto = $('#confirmar-texto');
  const confirmarOk = $('#confirmar-ok');
  const confirmarCancelar = $('#confirmar-cancelar');

  const FOCALIZABLES = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled]):not([type="hidden"])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])'
  ].join(',');

  let ultimoFoco = null;
  let resolverConfirmacion = null;

  /* ---------------------------------------------------------
     Bloqueo del scroll de la página
     --------------------------------------------------------- */

  function actualizarBloqueo() {
    const abierto =
      !modalFondo.hidden || !drawerFondo.hidden || !confirmarFondo.hidden;

    document.body.classList.toggle('panel-bloqueado', abierto);
  }

  function capaActiva() {
    if (!confirmarFondo.hidden) {
      return $('.modal-caja', confirmarFondo);
    }

    if (!drawerFondo.hidden) {
      return drawerCaja;
    }

    if (!modalFondo.hidden) {
      return modalCaja;
    }

    return null;
  }

  function enfocar(raiz) {
    if (!raiz) {
      return;
    }

    const candidatos = UI.qsa(FOCALIZABLES, raiz).filter(function (nodo) {
      return nodo.offsetParent !== null || nodo === document.activeElement;
    });

    const primero =
      candidatos.filter(function (nodo) {
        return nodo.matches('input, select, textarea');
      })[0] || candidatos[0];

    if (primero) {
      primero.focus();
    } else if (raiz.setAttribute) {
      raiz.setAttribute('tabindex', '-1');
      raiz.focus();
    }
  }

  function recordarFoco() {
    ultimoFoco = document.activeElement;
  }

  function devolverFoco() {
    if (ultimoFoco && document.contains(ultimoFoco)) {
      ultimoFoco.focus();
    }

    ultimoFoco = null;
  }

  /* ---------------------------------------------------------
     Modal
     --------------------------------------------------------- */

  function abrirModal(opciones) {
    const config = opciones || {};

    if (modalFondo.hidden) {
      recordarFoco();
    }

    modalKicker.textContent = config.kicker || 'Panel';
    modalTitulo.textContent = config.titulo || '';
    modalCuerpo.innerHTML = config.cuerpo || '';

    if (config.pie) {
      modalPie.innerHTML = config.pie;
      modalPie.hidden = false;
    } else {
      modalPie.innerHTML = '';
      modalPie.hidden = true;
    }

    modalCaja.classList.toggle('modal-caja-ancho', config.ancho === true);
    modalFondo.hidden = false;
    actualizarBloqueo();

    const api = {
      cuerpo: modalCuerpo,
      pie: modalPie,
      cerrar: cerrarModal
    };

    if (typeof config.alAbrir === 'function') {
      config.alAbrir(api);
    }

    enfocar(modalCaja);

    return api;
  }

  function cerrarModal() {
    if (modalFondo.hidden) {
      return;
    }

    modalFondo.hidden = true;
    modalCuerpo.innerHTML = '';
    modalPie.innerHTML = '';
    modalCaja.classList.remove('modal-caja-ancho');
    actualizarBloqueo();

    if (drawerFondo.hidden && confirmarFondo.hidden) {
      devolverFoco();
    }
  }

  function modalAbierto() {
    return !modalFondo.hidden;
  }

  /* ---------------------------------------------------------
     Drawer
     --------------------------------------------------------- */

  function abrirDrawer(opciones) {
    const config = opciones || {};

    if (drawerFondo.hidden) {
      recordarFoco();
    }

    drawerKicker.textContent = config.kicker || 'Ficha';
    drawerTitulo.textContent = config.titulo || '';
    drawerCuerpo.innerHTML = config.cuerpo || '';
    drawerFondo.hidden = false;
    actualizarBloqueo();

    const api = {
      cuerpo: drawerCuerpo,
      cerrar: cerrarDrawer
    };

    if (typeof config.alAbrir === 'function') {
      config.alAbrir(api);
    }

    enfocar(drawerCaja);

    return api;
  }

  function cerrarDrawer() {
    if (drawerFondo.hidden) {
      return;
    }

    drawerFondo.hidden = true;
    drawerCuerpo.innerHTML = '';
    actualizarBloqueo();

    if (modalFondo.hidden && confirmarFondo.hidden) {
      devolverFoco();
    }
  }

  function drawerAbierto() {
    return !drawerFondo.hidden;
  }

  /* ---------------------------------------------------------
     Confirmación
     --------------------------------------------------------- */

  function confirmar(opciones) {
    const config = opciones || {};

    if (resolverConfirmacion) {
      resolverConfirmacion(false);
    }

    confirmarTitulo.textContent = config.titulo || '¿Continuar?';
    confirmarTexto.textContent = config.mensaje || '';
    confirmarOk.textContent = config.textoOk || 'Confirmar';
    confirmarOk.className =
      'panel-btn ' +
      (config.peligro === false ? 'panel-btn-primario' : 'panel-btn-peligro');

    confirmarFondo.hidden = false;
    actualizarBloqueo();
    confirmarCancelar.focus();

    return new Promise(function (resolver) {
      resolverConfirmacion = resolver;
    });
  }

  function cerrarConfirmacion(valor) {
    if (confirmarFondo.hidden) {
      return;
    }

    confirmarFondo.hidden = true;
    actualizarBloqueo();

    const resolver = resolverConfirmacion;
    resolverConfirmacion = null;

    if (resolver) {
      resolver(Boolean(valor));
    }

    const capa = capaActiva();

    if (capa) {
      enfocar(capa);
    }
  }

  /* ---------------------------------------------------------
     Teclado
     --------------------------------------------------------- */

  document.addEventListener('keydown', function (evento) {
    if (!capaActiva()) {
      return;
    }

    if (evento.key === 'Escape') {
      evento.preventDefault();

      if (!confirmarFondo.hidden) {
        cerrarConfirmacion(false);
      } else if (!drawerFondo.hidden) {
        cerrarDrawer();
      } else {
        cerrarModal();
      }

      return;
    }

    if (evento.key !== 'Tab') {
      return;
    }

    const capa = capaActiva();
    const nodos = UI.qsa(FOCALIZABLES, capa).filter(function (nodo) {
      return nodo.offsetParent !== null;
    });

    if (!nodos.length) {
      evento.preventDefault();
      return;
    }

    const primero = nodos[0];
    const ultimo = nodos[nodos.length - 1];

    if (evento.shiftKey && document.activeElement === primero) {
      evento.preventDefault();
      ultimo.focus();
    } else if (!evento.shiftKey && document.activeElement === ultimo) {
      evento.preventDefault();
      primero.focus();
    }
  });

  modalCerrar.addEventListener('click', cerrarModal);

  modalFondo.addEventListener('click', function (evento) {
    if (evento.target === modalFondo) {
      cerrarModal();
    }
  });

  drawerCerrar.addEventListener('click', cerrarDrawer);

  drawerFondo.addEventListener('click', function (evento) {
    if (evento.target === drawerFondo) {
      cerrarDrawer();
    }
  });

  confirmarOk.addEventListener('click', function () {
    cerrarConfirmacion(true);
  });

  confirmarCancelar.addEventListener('click', function () {
    cerrarConfirmacion(false);
  });

  confirmarFondo.addEventListener('click', function (evento) {
    if (evento.target === confirmarFondo) {
      cerrarConfirmacion(false);
    }
  });

  /* ---------------------------------------------------------
     Constructores de formulario
     --------------------------------------------------------- */

  function esc(valor) {
    return UI.escapar(valor);
  }

  function opcional(etiqueta) {
    return etiqueta === false
      ? ''
      : ' <span class="opcional">(opcional)</span>';
  }

  function atributos(extra) {
    const partes = [];

    Object.keys(extra || {}).forEach(function (clave) {
      const valor = extra[clave];

      if (valor === undefined || valor === null || valor === false) {
        return;
      }

      if (valor === true) {
        partes.push(clave);
        return;
      }

      partes.push(clave + '="' + esc(valor) + '"');
    });

    return partes.length ? ' ' + partes.join(' ') : '';
  }

  function campo(config) {
    const id = config.id;
    const tipo = config.tipo || 'text';
    const clases = ['campo'];

    if (config.ancho) {
      clases.push('campo-ancho');
    }

    if (config.clave) {
      clases.push('campo-clave');
    }

    const label =
      '<label for="' + esc(id) + '">' +
      esc(config.label || id) +
      (config.requerido ? '' : opcional(config.opcional)) +
      '</label>';

    const comunes = {
      id: id,
      name: config.name || id,
      required: Boolean(config.requerido),
      disabled: Boolean(config.deshabilitado),
      placeholder: config.placeholder,
      autocomplete: config.autocomplete,
      min: config.min,
      max: config.max,
      step: config.step,
      inputmode: config.inputmode
    };

    let control;

    if (tipo === 'textarea') {
      control =
        '<textarea' +
        atributos(comunes) +
        (config.filas ? ' rows="' + Number(config.filas) + '"' : '') +
        '>' +
        esc(config.valor) +
        '</textarea>';
    } else if (tipo === 'select') {
      const opciones = (config.opciones || [])
        .map(function (opcion) {
          const item =
            typeof opcion === 'object'
              ? opcion
              : { valor: opcion, texto: opcion };
          const valor = item.valor === undefined ? '' : item.valor;
          const seleccionada = String(valor) === String(config.valor || '');

          return (
            '<option value="' +
            esc(valor) +
            '"' +
            (seleccionada ? ' selected' : '') +
            '>' +
            esc(item.texto === undefined ? valor : item.texto) +
            '</option>'
          );
        })
        .join('');

      control =
        '<select' + atributos(comunes) + '>' +
        (config.vacio === false
          ? ''
          : '<option value="">' + esc(config.vacio || 'Seleccioná…') + '</option>') +
        opciones +
        '</select>';
    } else {
      control =
        '<input type="' +
        esc(tipo) +
        '"' +
        atributos(comunes) +
        ' value="' +
        esc(config.valor) +
        '" />';
    }

    return (
      '<div class="' + clases.join(' ') + '">' +
      label +
      control +
      (config.pista
        ? '<span class="pista">' + esc(config.pista) + '</span>'
        : '') +
      '</div>'
    );
  }

  function fila() {
    const bloques = Array.prototype.slice.call(arguments).filter(Boolean);

    return '<div class="form-grid">' + bloques.join('') + '</div>';
  }

  function bloqueAlerta(id) {
    return (
      '<div class="alerta" id="' +
      esc(id || 'modal-alerta') +
      '" role="alert" hidden></div>'
    );
  }

  function seccion(titulo, contenido, nota) {
    return (
      '<section class="form-seccion">' +
      '<header class="form-seccion-cabeza">' +
      '<h3>' + esc(titulo) + '</h3>' +
      (nota ? '<span>' + esc(nota) + '</span>' : '') +
      '</header>' +
      contenido +
      '</section>'
    );
  }

  function boton(config) {
    const clases = ['panel-btn'];

    if (config.chico) {
      clases.push('panel-btn-chico');
    }

    clases.push('panel-btn-' + (config.tipo || 'secundario'));

    return (
      '<button' +
      atributos({
        type: config.submit ? 'submit' : 'button',
        class: clases.join(' '),
        id: config.id,
        form: config.form,
        'data-accion': config.accion,
        'data-id': config.idDato
      }) +
      '>' +
      esc(config.texto || 'Aceptar') +
      '</button>'
    );
  }

  /* ---------------------------------------------------------
     Formularios
     --------------------------------------------------------- */

  function valor(id, raiz) {
    const nodo = (raiz || document).querySelector('#' + id);

    if (!nodo) {
      return '';
    }

    return String(nodo.value || '').trim();
  }

  function numero(id, raiz) {
    const crudo = valor(id, raiz);
    const numeroValor = Number(crudo);

    return crudo === '' || isNaN(numeroValor) ? null : numeroValor;
  }

  /* <input type="date"> solo acepta YYYY-MM-DD. */
  function fechaInput(valorCrudo) {
    if (!valorCrudo) {
      return '';
    }

    const texto = String(valorCrudo);

    if (/^\d{4}-\d{2}-\d{2}/.test(texto)) {
      return texto.slice(0, 10);
    }

    const fecha = new Date(texto);

    if (isNaN(fecha.getTime())) {
      return '';
    }

    return (
      String(fecha.getUTCFullYear()) +
      '-' +
      String(fecha.getUTCMonth() + 1).padStart(2, '0') +
      '-' +
      String(fecha.getUTCDate()).padStart(2, '0')
    );
  }

  function hoyInput() {
    const ahora = new Date();

    return (
      String(ahora.getFullYear()) +
      '-' +
      String(ahora.getMonth() + 1).padStart(2, '0') +
      '-' +
      String(ahora.getDate()).padStart(2, '0')
    );
  }

  function ocupado(botonNodo, texto) {
    if (!botonNodo) {
      return;
    }

    if (!botonNodo.dataset.textoOriginal) {
      botonNodo.dataset.textoOriginal = botonNodo.textContent;
    }

    botonNodo.disabled = true;
    botonNodo.textContent = texto || 'Guardando…';
  }

  function libre(botonNodo) {
    if (!botonNodo) {
      return;
    }

    botonNodo.disabled = false;

    if (botonNodo.dataset.textoOriginal) {
      botonNodo.textContent = botonNodo.dataset.textoOriginal;
    }
  }

  function aviso(mensaje, tipo) {
    UI.mostrarMensaje(
      $('#modal-alerta'),
      mensaje,
      tipo || 'error'
    );
  }

  function limpiarAviso() {
    UI.ocultarMensaje($('#modal-alerta'));
  }

  return {
    abrirModal: abrirModal,
    cerrarModal: cerrarModal,
    modalAbierto: modalAbierto,
    abrirDrawer: abrirDrawer,
    cerrarDrawer: cerrarDrawer,
    drawerAbierto: drawerAbierto,
    confirmar: confirmar,
    esc: esc,
    campo: campo,
    fila: fila,
    bloqueAlerta: bloqueAlerta,
    seccion: seccion,
    boton: boton,
    valor: valor,
    numero: numero,
    fechaInput: fechaInput,
    hoyInput: hoyInput,
    ocupado: ocupado,
    libre: libre,
    aviso: aviso,
    limpiarAviso: limpiarAviso
  };
})();

window.PanelUI = PanelUI;
