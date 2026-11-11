/* =========================================================
   Tien Long Hu - Landing
   Animaciones de transicion entre secciones
   ========================================================= */

/* ---------------------------------------------------------
   Control de animaciones
   ---------------------------------------------------------
   reduceMotion apaga solo lo decorativo (glow, parallax, video).
   Las transiciones de seccion se mantienen siempre, salvo que
   pongas ACCESSIBILITY_REDUCED_MOTION = true para respetar
   estrictamente la preferencia del sistema.
   --------------------------------------------------------- */
const FORCE_ANIMATIONS = true;
const ACCESSIBILITY_REDUCED_MOTION = false;

const systemReducesMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const reduceMotion = ACCESSIBILITY_REDUCED_MOTION && systemReducesMotion;

/* Con FORCE_ANIMATIONS = true se activa esta clase y el CSS
   deja de anular las transiciones de seccion. */
if (FORCE_ANIMATIONS) {
  document.documentElement.classList.add('force-animations');
}

const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('.main-nav');
const header = document.querySelector('.site-header');
const backTop = document.querySelector('.back-top');

/* ---------------------------------------------------------
   Menu movil
   --------------------------------------------------------- */
if (menuButton && navigation) {
  const closeMenu = () => {
    navigation.classList.remove('is-open');
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.setAttribute('aria-label', 'Abrir menú');
  };

  menuButton.addEventListener('click', () => {
    const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!isOpen));
    menuButton.setAttribute('aria-label', isOpen ? 'Abrir menú' : 'Cerrar menú');
    navigation.classList.toggle('is-open', !isOpen);
  });

  navigation.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
      closeMenu();
      menuButton.focus();
    }
  });
}

/* ---------------------------------------------------------
   Transiciones por seccion
   Calculo directo en scroll (mas confiable que IntersectionObserver
   en navegadores headless/embebidos).
   --------------------------------------------------------- */
const sections = document.querySelectorAll('main > section');
const revealItems = document.querySelectorAll('.reveal');

const showEverything = () => {
  sections.forEach((section) => section.classList.add('in-view'));
  revealItems.forEach((item) => item.classList.add('is-visible'));
};

sections.forEach((section) => section.classList.add('section-anim'));

const SECTION_TRIGGER = 0.82;
/* Se resetea cuando la seccion sale del viewport por arriba o por abajo. */
const SECTION_RESET = 0.99;

const syncSections = () => {
  sections.forEach((section) => {
    const rect = section.getBoundingClientRect();
    const visibleHeight = Math.min(rect.bottom, window.innerHeight) - Math.max(rect.top, 0);
    const onScreen = visibleHeight > 0;

    // Entra cuando su borde superior llega al 82% de la pantalla
    const entering = onScreen && rect.top < window.innerHeight * SECTION_TRIGGER;
    // Se resetea cuando la seccion ya no esta en pantalla
    const exited = !onScreen || rect.top >= window.innerHeight * SECTION_RESET || rect.bottom <= 0;

    if (entering) {
      section.classList.add('in-view');
    } else if (exited) {
      section.classList.remove('in-view');
    }
  });

  revealItems.forEach((item) => {
    const rect = item.getBoundingClientRect();
    const onScreen = rect.bottom > 0 && rect.top < window.innerHeight;

    if (onScreen && rect.top < window.innerHeight * 0.9) {
      item.classList.add('is-visible');
    } else if (!onScreen || rect.top >= window.innerHeight * SECTION_RESET) {
      item.classList.remove('is-visible');
    }
  });
};

if (reduceMotion && !FORCE_ANIMATIONS) {
  // Accesibilidad: sin animaciones, mostrar todo
  showEverything();
} else {
  if ('IntersectionObserver' in window) {
    const sectionObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
        } else {
          // Vuelve a su estado inicial al salir, para animarse de nuevo
          entry.target.classList.remove('in-view');
        }
      });
    }, { threshold: 0.01, rootMargin: '0px 0px -5% 0px' });

    sections.forEach((section) => sectionObserver.observe(section));
  }

  // Refuerzo por scroll
  window.addEventListener('scroll', syncSections, { passive: true });
  window.addEventListener('resize', syncSections, { passive: true });
  window.addEventListener('load', syncSections);

  // Bucle de respaldo: algunos navegadores/entornos no disparan el evento
  // scroll al usar window.scrollTo(), ni ejecutan requestAnimationFrame
  // cuando la pestana no esta visible. Con setInterval cubrimos ambos casos.
  let lastScrollY = -1;
  const checkScroll = () => {
    const current = window.scrollY || document.documentElement.scrollTop;
    if (Math.abs(current - lastScrollY) > 0.5) {
      lastScrollY = current;
      syncSections();
    }
  };

  syncSections();
  window.setInterval(checkScroll, 120);
}
const smoothBehavior = reduceMotion ? 'auto' : 'smooth';

document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (event) => {
    const targetId = link.getAttribute('href');
    if (targetId.length < 2) return;

    const target = document.querySelector(targetId);
    if (!target) return;

    event.preventDefault();

    const headerHeight = header ? header.offsetHeight : 0;
    const top = target.getBoundingClientRect().top + window.scrollY - headerHeight + 4;

    window.scrollTo({ top, behavior: smoothBehavior });

    if (targetId === '#main-content') {
      target.focus({ preventScroll: true });
    }

    if (history.replaceState) {
      history.replaceState(null, '', targetId);
    }
  });
});

/* ---------------------------------------------------------
   Barra de progreso de lectura + header compacto + back-to-top
   --------------------------------------------------------- */
const progress = document.createElement('div');
progress.className = 'reading-progress';
progress.setAttribute('aria-hidden', 'true');
document.body.appendChild(progress);

let ticking = false;

const onScroll = () => {
  const scrollTop = window.scrollY || document.documentElement.scrollTop;
  const height = document.documentElement.scrollHeight - window.innerHeight;
  const ratio = height > 0 ? Math.min(scrollTop / height, 1) : 0;

  progress.style.transform = `scaleX(${ratio})`;

  if (header) header.classList.toggle('is-scrolled', scrollTop > 40);
  if (backTop) backTop.classList.toggle('is-visible', scrollTop > 500);

  ticking = false;
};

window.addEventListener('scroll', () => {
  if (!ticking) {
    ticking = true;
    window.requestAnimationFrame(onScroll);
  }
}, { passive: true });

onScroll();

/* ---------------------------------------------------------
   Parallax suave del hero (solo desktop)
   --------------------------------------------------------- */
const heroImage = document.querySelector('.hero-image');
const canParallax = heroImage && !reduceMotion && window.matchMedia('(min-width: 901px)').matches;

if (canParallax) {
  let heroTicking = false;

  const moveHero = () => {
    const offset = Math.min(window.scrollY * 0.18, 120);
    heroImage.style.transform = `translate3d(0, ${offset}px, 0) scale(1.06)`;
    heroTicking = false;
  };

  window.addEventListener('scroll', () => {
    if (!heroTicking) {
      heroTicking = true;
      window.requestAnimationFrame(moveHero);
    }
  }, { passive: true });
}

/* ---------------------------------------------------------
   Efecto de luz que sigue al cursor en las tarjetas
   --------------------------------------------------------- */
const cards = document.querySelectorAll('.discipline-card, .testimonial');

if (cards.length && !reduceMotion) {
  cards.forEach((card) => {
    card.classList.add('has-glow');

    card.addEventListener('pointermove', (event) => {
      const rect = card.getBoundingClientRect();
      const x = ((event.clientX - rect.left) / rect.width) * 100;
      const y = ((event.clientY - rect.top) / rect.height) * 100;
      card.style.setProperty('--x', `${x}%`);
      card.style.setProperty('--y', `${y}%`);
    });
  });
}

/* ---------------------------------------------------------
   Video de fondo (fuego): carga diferida y pausa fuera de vista
   --------------------------------------------------------- */
const fireVideos = document.querySelectorAll('.fire-video');

if (fireVideos.length) {
  // El video es decorativo: se muestra siempre en escritorio, incluso
  // si el sistema tiene "reducir movimiento" (el usuario lo pidio).
  const canPlayVideo = window.matchMedia('(min-width: 651px)').matches;

  if (!canPlayVideo) {
    fireVideos.forEach((video) => video.removeAttribute('autoplay'));
  } else {
    // La ruta real queda en data-src para no descargar 35 MB al abrir.
    fireVideos.forEach((video) => {
      const source = video.querySelector('source');
      if (source && !source.dataset.src) {
        source.dataset.src = source.getAttribute('src') || 'assets/fire.mp4';
      }
      if (source) source.removeAttribute('src');
      video.load();
      video.dataset.ready = 'false';
    });

    const startVideo = (video) => {
      const source = video.querySelector('source');

      if (source && video.dataset.ready !== 'true') {
        source.src = source.dataset.src;
        video.dataset.ready = 'true';
        video.load();
      }

      const play = video.play();
      if (play && play.catch) play.catch(() => {});
    };

    const checkVideos = () => {
      fireVideos.forEach((video) => {
        const rect = video.getBoundingClientRect();
        const onScreen = rect.bottom > 0 && rect.top < window.innerHeight;

        if (onScreen) {
          startVideo(video);
        } else if (!video.paused) {
          video.pause();
        }
      });
    };

    // IntersectionObserver (cuando funciona)
    if ('IntersectionObserver' in window) {
      const videoObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            startVideo(entry.target);
          } else if (!entry.target.paused) {
            entry.target.pause();
          }
        });
      }, { threshold: 0.15 });

      fireVideos.forEach((video) => videoObserver.observe(video));
    }

    // Respaldo por scroll e intervalo (cubre navegadores que no disparan
    // el observer ni el evento scroll).
    window.addEventListener('scroll', checkVideos, { passive: true });
    window.addEventListener('resize', checkVideos, { passive: true });
    window.setInterval(checkVideos, 300);
    checkVideos();
  }
}

/* ---------------------------------------------------------
   Año del footer
   --------------------------------------------------------- */
const yearElement = document.querySelector('#year');
if (yearElement) {
  yearElement.textContent = new Date().getFullYear();
}

/* ---------------------------------------------------------
   Chatbot de preguntas frecuentes
   ---------------------------------------------------------
   Respuestas armadas con la informacion publicada en la landing.
   La coincidencia es por palabras clave: no hay servicios externos.
   --------------------------------------------------------- */
const faqBot = document.querySelector('#faq-bot');
const faqToggle = document.querySelector('#faq-bot-toggle');
const faqPanel = document.querySelector('#faq-bot-panel');
const faqCerrar = document.querySelector('#faq-bot-cerrar');
const faqMensajes = document.querySelector('#faq-bot-mensajes');
const faqForm = document.querySelector('#faq-bot-form');
const faqInput = document.querySelector('#faq-bot-input');

const FAQ = [
  {
    id: 'disciplinas',
    prioridad: 11,
    claves: [
      'disciplina', 'disciplinas', 'wushu', 'wu shu', 'tai chi', 'taichi',
      'tai chi chuan', 'curso', 'cursos', 'clase', 'clases', 'grupo',
      'grupos', 'entrenamiento personal', 'personalizado', 'personalizados'
    ],
    respuesta:
      'La escuela trabaja Wu Shu (formas clásicas y modernas), Tai Chi Chuan, clases en grupo y entrenamientos personales. Podés ver el detalle en la sección Disciplinas de la página.'
  },
  {
    id: 'horarios',
    prioridad: 2,
    claves: [
      'horario', 'horarios', 'hora', 'horas', 'dia', 'dias', 'turno',
      'turnos', 'cuando', 'cronograma', 'que dias'
    ],
    respuesta:
      'Los horarios actuales no están publicados en la web. Escribinos a hola@unsitiogenial.es o llamá al 923 456 789 y te pasamos los días y turnos de cada disciplina.'
  },
  {
    id: 'precios',
    prioridad: 3,
    claves: [
      'precio', 'precios', 'cuota', 'cuotas', 'costo', 'costos', 'arancel',
      'aranceles', 'pago', 'pagos', 'pagar', 'mensualidad', 'valor', 'sale',
      'cuesta', 'cuanto'
    ],
    respuesta:
      'Los aranceles y planes de pago se consultan directamente con la escuela. Escribinos a hola@unsitiogenial.es o llamá al 923 456 789 para recibir la información actualizada.'
  },
  {
    id: 'ubicacion',
    prioridad: 4,
    claves: [
      'donde', 'ubicacion', 'direccion', 'llegar', 'sede', 'local', 'calle',
      'quilmes', 'ubicados', 'como llego'
    ],
    respuesta:
      'Estamos en Av. 12 de Octubre 1000, Quilmes, Buenos Aires, Argentina. En la sección Contacto de la página tenés la dirección y los datos para escribirnos.'
  },
  {
    id: 'inscripcion',
    prioridad: 5,
    claves: [
      'inscribir', 'inscripcion', 'inscribirme', 'inscribo', 'anotarme',
      'registrarme', 'empezar', 'empiezo', 'comenzar', 'comienzo', 'prueba',
      'probar', 'clase de prueba', 'como empiezo', 'como me inscribo'
    ],
    respuesta:
      'Para empezar, escribinos a hola@unsitiogenial.es o usá el botón "Quiero más información" de la sección Contacto. Si ya sos alumno o profesor, podés ingresar desde el botón Login.'
  },
  {
    id: 'edades',
    prioridad: 1,
    claves: [
      'edad', 'edades', 'nino', 'ninos', 'nina', 'ninas', 'adulto', 'adultos',
      'menor', 'menores', 'chico', 'chicos', 'familia', 'infantil'
    ],
    respuesta:
      'Hay clases en grupo y entrenamientos personalizados. No publicamos edades mínimas en la web, así que consultanos por la franja de edad y el grupo que mejor se adapte a vos o a tu familia.'
  },
  {
    id: 'contacto',
    prioridad: 6,
    claves: [
      'contacto', 'telefono', 'email', 'correo', 'whatsapp', 'comunicar',
      'hablar', 'llamar', 'escribir', 'escribinos', 'mail'
    ],
    respuesta:
      'Podés escribirnos a tienlonghu@gmail.com o llamar al 1138197145. También encontrás estos datos al final de la página, en la sección Contacto.'
  },
  {
    id: 'historia',
    prioridad: 10,
    claves: [
      'historia', 'tradicion', 'fundada', 'fundacion', 'maestro', 'ruben',
      'braun', '1991', 'escuela', 'academia', 'origen'
    ],
    respuesta:
      'Tien Long Hu es una Escuela Superior de Artes Chinas fundada en 1991 por el Maestro Rubén Braun. Preserva las enseñanzas tradicionales de las artes marciales chinas y combina formas clásicas y modernas de Wu Shu.'
  },
  {
    id: 'graduaciones',
    prioridad: 7,
    claves: [
      'graduacion', 'graduaciones', 'grado', 'grados', 'cinturon',
      'cinturones', 'examen', 'examenes', 'rendir', 'avanzar', 'certificado'
    ],
    respuesta:
      'Las graduaciones se registran en el panel privado: cada alumno puede ver su último grado y los profesores ven cuántos alumnos hay en cada graduación. Para rendir un examen, hablá con tu profesor.'
  },
  {
    id: 'login',
    prioridad: 8,
    claves: [
      'login', 'panel', 'contrasena', 'usuario', 'ingresar', 'cuenta',
      'plataforma', 'clave', 'mi perfil'
    ],
    respuesta:
      'Si ya sos alumno o profesor, entrá desde el botón Login de la esquina superior derecha. Si no recordás tu usuario o contraseña, escribinos a hola@unsitiogenial.es.'
  },
  {
    id: 'ropa',
    prioridad: 9,
    claves: [
      'ropa', 'vestimenta', 'uniforme', 'llevar', 'calzado', 'zapatillas',
      'equipo', 'que me pongo'
    ],
    respuesta:
      'Te recomendamos ropa cómoda y calzado deportivo para la primera clase. Si la disciplina necesita algún elemento específico, consultanos antes por correo o teléfono.'
  }
];

const normalizarTexto = (valor) =>
  String(valor || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

const buscarRespuesta = (consulta) => {
  const texto = ` ${normalizarTexto(consulta)} `;

  if (!texto.trim()) {
    return null;
  }

  let mejor = null;
  let mejorPuntaje = 0;

  FAQ.forEach((item) => {
    let puntaje = 0;

    item.claves.forEach((clave) => {
      const buscada = normalizarTexto(clave);

      if (!buscada) return;

      if (texto.indexOf(` ${buscada} `) !== -1) {
        puntaje += buscada.split(' ').length;
      }
    });

    if (
      puntaje > mejorPuntaje ||
      (puntaje === mejorPuntaje && puntaje > 0 && mejor && item.prioridad < mejor.prioridad)
    ) {
      mejorPuntaje = puntaje;
      mejor = item;
    }
  });

  return mejor;
};

const respuestaPorDefecto =
  'No encontré una respuesta exacta para esa pregunta. Podés consultar por horarios, precios, ubicación, disciplinas, edades, inscripción, graduaciones o el acceso al panel. Para algo puntual, escribinos a hola@unsitiogenial.es.';

if (faqBot && faqToggle && faqPanel && faqMensajes) {
  let iniciado = false;
  let abierto = false;

  const irAlFinal = () => {
    faqMensajes.scrollTop = faqMensajes.scrollHeight;
  };

  const agregarMensaje = (tipo, contenido) => {
    const burbuja = document.createElement('div');
    burbuja.className = `faq-bot-mensaje faq-bot-mensaje-${tipo}`;

    if (tipo === 'bot') {
      const autor = document.createElement('span');
      autor.className = 'faq-bot-autor';
      autor.textContent = 'Asistente';
      burbuja.appendChild(autor);
    }

    const copia = document.createElement('p');
    copia.textContent = contenido;
    burbuja.appendChild(copia);

    faqMensajes.appendChild(burbuja);
    irAlFinal();

    return burbuja;
  };

  const responder = (contenido) => {
    const indicador = document.createElement('div');
    indicador.className = 'faq-bot-mensaje faq-bot-mensaje-bot faq-bot-escribiendo';
    indicador.textContent = 'Escribiendo…';
    faqMensajes.appendChild(indicador);
    irAlFinal();

    window.setTimeout(() => {
      indicador.remove();
      agregarMensaje('bot', contenido);
    }, 320);
  };

  const preguntar = (textoCrudo) => {
    const pregunta = String(textoCrudo || '').trim();

    if (!pregunta) {
      return;
    }

    agregarMensaje('usuario', pregunta);

    const encontrada = buscarRespuesta(pregunta);

    responder(encontrada ? encontrada.respuesta : respuestaPorDefecto);
  };

  const abrirBot = () => {
    abierto = true;
    faqPanel.hidden = false;
    faqBot.classList.add('is-open');
    faqToggle.setAttribute('aria-expanded', 'true');

    if (!iniciado) {
      iniciado = true;
      agregarMensaje(
        'bot',
        '¡Hola! Soy el asistente de Tien Long Hu. Podés preguntarme por horarios, precios, ubicación, disciplinas, edades, inscripción o graduaciones.'
      );
    }

    irAlFinal();

    if (faqInput) {
      window.setTimeout(() => faqInput.focus(), 40);
    }
  };

  const cerrarBot = (devolverFoco) => {
    abierto = false;
    faqPanel.hidden = true;
    faqBot.classList.remove('is-open');
    faqToggle.setAttribute('aria-expanded', 'false');

    if (devolverFoco) {
      faqToggle.focus();
    }
  };

  faqToggle.addEventListener('click', () => {
    if (abierto) {
      cerrarBot(false);
    } else {
      abrirBot();
    }
  });

  if (faqCerrar) {
    faqCerrar.addEventListener('click', () => cerrarBot(true));
  }

  if (faqForm && faqInput) {
    faqForm.addEventListener('submit', (evento) => {
      evento.preventDefault();

      const pregunta = faqInput.value.trim();

      if (!pregunta) {
        return;
      }

      faqInput.value = '';
      preguntar(pregunta);
    });
  }

  document.addEventListener('keydown', (evento) => {
    if (evento.key === 'Escape' && abierto) {
      cerrarBot(true);
    }
  });

  document.addEventListener('click', (evento) => {
    if (abierto && !faqBot.contains(evento.target)) {
      cerrarBot(false);
    }
  });
}
