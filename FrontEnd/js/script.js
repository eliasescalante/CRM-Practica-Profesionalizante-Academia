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
