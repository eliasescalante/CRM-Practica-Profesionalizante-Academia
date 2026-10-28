/* =========================================================
   Tien Long Hu - Utilidades de interfaz
   ---------------------------------------------------------
   Helpers chicos y sin dependencias que comparten el login
   y el panel: buscar nodos, escapar texto que viene de la API,
   formatear fechas, iniciales, avisos y estados vacíos.
   ========================================================= */

const UI = (function () {
  'use strict';

  function qs(selector, raiz) {
    return (raiz || document).querySelector(selector);
  }

  function qsa(selector, raiz) {
    return Array.prototype.slice.call(
      (raiz || document).querySelectorAll(selector)
    );
  }

  /* Escapa texto antes de meterlo con innerHTML.
     Los datos vienen de la base: nombres con acentos, comillas, etc. */
  function escapar(valor) {
    if (valor === null || valor === undefined) {
      return '';
    }

    return String(valor)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function texto(valor, reemplazo) {
    if (valor === null || valor === undefined || valor === '') {
      return reemplazo === undefined ? '—' : reemplazo;
    }

    return String(valor);
  }

  /* Acepta "2026-10-07", "Wed, 07 Oct 2026 00:00:00 GMT" o ISO completo.
     Para las fechas sin hora usa UTC para no correrse un día por zona. */
  function formatearFecha(valor) {
    if (!valor) {
      return '—';
    }

    if (typeof valor === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(valor)) {
      const partes = valor.split('-');
      return partes[2] + '/' + partes[1] + '/' + partes[0];
    }

    const fecha = new Date(valor);

    if (isNaN(fecha.getTime())) {
      return String(valor);
    }

    const dia = String(fecha.getUTCDate()).padStart(2, '0');
    const mes = String(fecha.getUTCMonth() + 1).padStart(2, '0');

    return dia + '/' + mes + '/' + fecha.getUTCFullYear();
  }

  function iniciales(nombre, apellido) {
    const a = (nombre || '').trim().charAt(0);
    const b = (apellido || '').trim().charAt(0);
    const resultado = (a + b).toUpperCase();

    return resultado || '?';
  }

  function moneda(valor) {
    if (valor === null || valor === undefined || valor === '') {
      return '—';
    }

    const numero = Number(valor);

    if (isNaN(numero)) {
      return String(valor);
    }

    try {
      return new Intl.NumberFormat('es-AR', {
        style: 'currency',
        currency: 'ARS',
        maximumFractionDigits: 0
      }).format(numero);
    } catch (error) {
      return '$ ' + numero;
    }
  }

  /* ---------------------------------------------------------
     Avisos flotantes (toast)
     --------------------------------------------------------- */

  function contenedorAvisos() {
    let contenedor = qs('.toast-stack');

    if (!contenedor) {
      contenedor = document.createElement('div');
      contenedor.className = 'toast-stack';
      contenedor.setAttribute('aria-live', 'polite');
      contenedor.setAttribute('aria-atomic', 'true');
      document.body.appendChild(contenedor);
    }

    return contenedor;
  }

  function avisar(mensaje, tipo) {
    if (!mensaje) {
      return;
    }

    const contenedor = contenedorAvisos();
    const aviso = document.createElement('div');

    aviso.className = 'toast toast-' + (tipo || 'info');
    aviso.setAttribute('role', 'status');
    aviso.textContent = mensaje;

    contenedor.appendChild(aviso);

    window.setTimeout(function () {
      aviso.classList.add('se-va');

      window.setTimeout(function () {
        if (aviso.parentNode) {
          aviso.parentNode.removeChild(aviso);
        }
      }, 320);
    }, 5200);
  }

  /* ---------------------------------------------------------
     Cajas de mensaje dentro de un formulario
     --------------------------------------------------------- */

  function mostrarMensaje(nodo, mensaje, tipo) {
    if (!nodo) {
      return;
    }

    nodo.textContent = mensaje;
    nodo.className = 'alerta alerta-' + (tipo || 'error');
    nodo.hidden = false;
  }

  function ocultarMensaje(nodo) {
    if (!nodo) {
      return;
    }

    nodo.textContent = '';
    nodo.hidden = true;
    nodo.className = 'alerta';
  }

  /* ---------------------------------------------------------
     Bloques de estado
     --------------------------------------------------------- */

  function vacio(titulo, detalle) {
    return (
      '<div class="vacio">' +
      '<span class="vacio-marca" aria-hidden="true">◇</span>' +
      '<p class="vacio-titulo">' +
      escapar(titulo) +
      '</p>' +
      '<p class="vacio-detalle">' +
      escapar(detalle || '') +
      '</p>' +
      '</div>'
    );
  }

  function cargando(filas) {
    const cantidad = filas || 3;
    let salida = '<div class="cargando-filas" aria-hidden="true">';

    for (let i = 0; i < cantidad; i += 1) {
      salida += '<span class="cargando-fila"></span>';
    }

    salida += '</div>';

    return salida;
  }

  /* ---------------------------------------------------------
     Insignias de estado
     --------------------------------------------------------- */

  function insignia(textoEstado) {
    const valor = String(textoEstado || '').toUpperCase();

    const mapa = {
      ACTIVO: 'ok',
      CONFIRMADO: 'ok',
      PAGADA: 'ok',
      INSCRIPTO: 'ok',
      PENDIENTE: 'warn',
      PAUSADO: 'warn',
      VENCIDA: 'bad',
      RECHAZADO: 'bad',
      INACTIVO: 'bad',
      SUSPENDIDO: 'bad',
      PRESENTE: 'ok',
      AUSENTE: 'bad'
    };

    const tono = mapa[valor] || 'neutro';

    return (
      '<span class="insignia insignia-' +
      tono +
      '">' +
      escapar(valor || '—') +
      '</span>'
    );
  }

  return {
    qs: qs,
    qsa: qsa,
    escapar: escapar,
    texto: texto,
    formatearFecha: formatearFecha,
    iniciales: iniciales,
    moneda: moneda,
    avisar: avisar,
    mostrarMensaje: mostrarMensaje,
    ocultarMensaje: ocultarMensaje,
    vacio: vacio,
    cargando: cargando,
    insignia: insignia
  };
})();

window.UI = UI;
