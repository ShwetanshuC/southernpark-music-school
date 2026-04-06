// Custom JavaScript for Southern Park Music School website

// Toggle flip for faculty cards
function toggleFlip(card) {
  var inner = card.querySelector('.flip-card-inner');
  if (!inner) return;

  var goingToBack = !card.classList.contains('rotate');

  card.classList.toggle('rotate');
  card.setAttribute('aria-expanded', String(goingToBack));

  var onTransitionEnd = function (e) {
    if (e.propertyName !== 'transform') return;
    inner.removeEventListener('transitionend', onTransitionEnd);
    if (card.classList.contains('rotate')) {
      var backFace = card.querySelector('.flip-card-back');
      if (backFace) {
        requestAnimationFrame(function () {
          backFace.scrollTo({ top: backFace.scrollHeight, behavior: 'smooth' });
        });
      }
    }
  };

  if (goingToBack) {
    inner.addEventListener('transitionend', onTransitionEnd);
  }
}

// Open gallery image in our custom modal
function openModal(imgElement) {
  var src = imgElement.getAttribute('src');
  var modalImgEl = document.getElementById('modalImage');
  var modalContainer = document.getElementById('imageModal');
  if (modalImgEl && modalContainer) {
    modalImgEl.setAttribute('src', src);
    modalContainer.classList.add('show');
  }
}

// Close the modal
function closeModal() {
  var modalContainer = document.getElementById('imageModal');
  if (modalContainer) modalContainer.classList.remove('show');
}

// Initialize custom hero carousel (simple slideshow)
function initHeroCarousel() {
  var hero = document.getElementById('heroCarousel');
  if (!hero) return;
  var slides = hero.querySelectorAll('.carousel-item');
  if (!slides || slides.length === 0) return;
  var current = 0;
  slides.forEach(function (slide, index) {
    if (index === 0) slide.classList.add('active');
    else slide.classList.remove('active');
  });
  setInterval(function () {
    slides[current].classList.remove('active');
    current = (current + 1) % slides.length;
    slides[current].classList.add('active');
  }, 5000);
}

// INIT ASAP (don’t wait for images)
document.addEventListener('DOMContentLoaded', function () {
  // Handle contact form submission
  var contactForms = document.querySelectorAll('.contact-form');
  contactForms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      alert('Thank you for reaching out! We will get back to you soon.');
      form.reset();
    });
  });

  // Set up gallery image click events (modal)
  var galleryImages = document.querySelectorAll('.gallery-grid img');
  galleryImages.forEach(function (img) {
    img.addEventListener('click', function () { openModal(img); });
  });

  // Close modal when clicking outside the content or on close button
  (function wireModalClose() {
    var modalContainer = document.getElementById('imageModal');
    if (!modalContainer) return;
    modalContainer.addEventListener('click', function (e) {
      if (e.target === modalContainer) closeModal();
    });
    var closeBtn = document.getElementById('modalCloseBtn');
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
  })();

  // ======================
  // Navbar (mobile toggle)
  // ======================
  var navbarToggler = document.querySelector('.navbar-toggler');
  var navbarCollapse = document.querySelector('.navbar-collapse');

  function setTogglerState(isOpen) {
    if (!navbarToggler) return;
    navbarToggler.classList.toggle('collapsed', !isOpen);
    navbarToggler.setAttribute('aria-expanded', String(isOpen));
  }

  function toggleCollapse() {
    if (!navbarCollapse) return;
    var isOpen = navbarCollapse.classList.toggle('show');
    setTogglerState(isOpen);
  }

  if (navbarToggler) {
    navbarToggler.addEventListener('click', toggleCollapse);
    // Initial state
    setTogglerState(false);
  }

  function handleResize() {
    if (!navbarCollapse || !navbarToggler) return;
    if (window.innerWidth >= 992) {
      // Desktop: ensure panel is closed and toggler reflects closed state
      navbarCollapse.classList.remove('show');
      setTogglerState(false);
    }
  }
  window.addEventListener('resize', handleResize);

  // Responsive vertical menu class on small screens
  function updateNavbarCollapseVertical() {
    // Re-query in case this script runs on pages without a navbar
    var collapseEl = document.querySelector('.navbar-collapse');
    if (!collapseEl) return;
    if (window.innerWidth < 992) collapseEl.classList.add('mobile-vertical');
    else collapseEl.classList.remove('mobile-vertical');
  }
  updateNavbarCollapseVertical();
  window.addEventListener('resize', updateNavbarCollapseVertical);

  // Initialize hero slideshow (if present)
  initHeroCarousel();

  // ===== Alert banner — hide if already dismissed this session =====
  var banner = document.getElementById('alertBanner');
  if (banner) {
    if (sessionStorage.getItem('weatherDismissed')) {
      banner.remove();
    } else {
      var dismissBtn = document.getElementById('dismissBanner');
      if (dismissBtn) {
        dismissBtn.addEventListener('click', function () {
          sessionStorage.setItem('weatherDismissed', '1');
          banner.classList.add('dismissed');
          setTimeout(function () { banner.remove(); }, 350);
        });
      }
    }
  }

  // ===== Smooth scroll with navbar offset for hero anchor links =====
  document.querySelectorAll('a[href="#about"], a[href="#why-us"], a[href="#history"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var target = document.querySelector(link.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      var nav = document.querySelector('nav');
      var navH = nav ? nav.offsetHeight : 0;
      var top = target.getBoundingClientRect().top + window.scrollY - navH - 8;
      window.scrollTo({ top: top, behavior: 'smooth' });
    });
  });

  // ===== Navbar shadow on scroll + hero parallax =====
  var mainNav = document.querySelector('nav');
  var heroSlides = document.querySelectorAll('#heroCarousel .carousel-item');
  var heroEl = document.getElementById('heroCarousel');
  window.addEventListener('scroll', function () {
    var sy = window.scrollY;
    if (mainNav) mainNav.classList.toggle('scrolled', sy > 10);
    if (heroSlides.length && heroEl && sy < heroEl.offsetHeight * 1.2) {
      var offset = sy * 0.18;
      for (var i = 0; i < heroSlides.length; i++) {
        heroSlides[i].style.transform = 'translateY(' + offset + 'px)';
      }
    }
  }, { passive: true });

  // ===== Scroll reveal =====
  var revealEls = document.querySelectorAll('.reveal');
  if (revealEls.length && 'IntersectionObserver' in window) {
    var revealObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('visible');
          revealObs.unobserve(e.target);
        }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(function (el) { revealObs.observe(el); });
  }

  // ===== Stat counter =====
  document.querySelectorAll('.stat-num').forEach(function (el) {
    var raw = el.dataset.count || el.textContent.trim();
    var target = parseInt(raw, 10);
    var suffix = el.dataset.suffix || '';
    
    // If no explicit suffix but string has one (e.g. "60+"), extract it
    if (!suffix && /[^\d]/.test(raw)) {
      suffix = raw.replace(/[\d]/g, '');
    }

    if (isNaN(target)) {
      el.textContent = raw;
      return;
    }

    var duration = 1400;
    var started = false;
    var statObs = new IntersectionObserver(function (entries) {
      if (!entries[0].isIntersecting || started) return;
      started = true;
      var startTime = null;
      function step(ts) {
        if (!startTime) startTime = ts;
        var prog = Math.min((ts - startTime) / duration, 1);
        var eased = 1 - Math.pow(1 - prog, 3);
        el.textContent = Math.floor(eased * target) + suffix;
        if (prog < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
      statObs.disconnect();
    }, { threshold: 0.5 });
    statObs.observe(el);
  });

  // =============================
  // Faculty toolbar interactions
  // =============================
  var searchInput = document.getElementById('faculty-search');
  if (searchInput) {
    // Map cards and set aria-controls
    var allCards = Array.prototype.slice.call(document.querySelectorAll('.faculty-section .flip-card'));
    allCards.forEach(function (card) {
      var grid = card.closest ? card.closest('.faculty-grid') : null;
      if (grid) {
        var children = Array.prototype.slice.call(grid.children);
        card.dataset.origIndex = String(children.indexOf(card));
      }
      var back = card.querySelector('.flip-card-back');
      if (back && back.id) card.setAttribute('aria-controls', back.id);
    });

    // Cross-browser diacritic strip (no Unicode property escapes)
    function normalizeStr(s) {
      return (s || '')
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, ''); // combining marks
    }

    function textOrEmpty(el) { return el && el.textContent ? el.textContent : ''; }

    // Token-based partial matching: all tokens must appear somewhere in the haystack
    function cardMatches(card, rawTerm) {
      var term = normalizeStr(rawTerm).trim();
      if (!term) return true;

      var front = card.querySelector('.flip-card-front .p-3');
      var nameEl = front ? front.querySelector('h5') : null;
      var roleEl = front ? front.querySelector('p') : null;

      var name = textOrEmpty(nameEl);
      var role = textOrEmpty(roleEl);
      var tags = card.getAttribute('data-tags') || '';

      var hay = normalizeStr(name + ' ' + role + ' ' + tags).replace(/\s+/g, ' ').trim();

      // Split on whitespace; require every token to be present (substring match)
      var tokens = term.split(/\s+/);
      for (var i = 0; i < tokens.length; i++) {
        if (hay.indexOf(tokens[i]) === -1) return false;
      }
      return true;
    }

    function applySearch() {
      var term = (searchInput.value || '').trim();
      allCards.forEach(function (card) {
        card.style.display = cardMatches(card, term) ? '' : 'none';
      });
      // Hide section headings when all cards in that section are hidden
      document.querySelectorAll('.faculty-section').forEach(function (section) {
        var visible = section.querySelectorAll('.flip-card:not([style*="display: none"]):not([style*="display:none"])');
        section.style.display = visible.length ? '' : 'none';
      });
    }

    // Lightweight debounce
    function debounce(fn, ms) {
      var t;
      return function () {
        var ctx = this, args = arguments;
        clearTimeout(t);
        t = setTimeout(function () { fn.apply(ctx, args); }, ms);
      };
    }
    var applySearchDebounced = debounce(applySearch, 120);

    // Listen broadly so partials update while typing on all browsers
    searchInput.addEventListener('input', applySearchDebounced);
    searchInput.addEventListener('keyup', applySearchDebounced);
    searchInput.addEventListener('search', applySearch); // Enter/clear on type=search

    // Make mobile keyboards less “helpful”
    try {
      searchInput.setAttribute('autocomplete', 'off');
      searchInput.setAttribute('autocorrect', 'off');
      searchInput.setAttribute('autocapitalize', 'none');
      searchInput.setAttribute('spellcheck', 'false');
    } catch (e) {}

    // Initial render
    applySearch();

    // Keyboard access: flip on Enter/Space
    document.querySelectorAll('.flip-card[role="button"]').forEach(function (el) {
      el.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          toggleFlip(el);
        }
      });
    });
  }
});