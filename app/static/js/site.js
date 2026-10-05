/* ClassNext public site interactions.
   Kept in a separate file because the Content-Security-Policy allows
   'self' scripts only — inline handlers are blocked. */
(function () {
  'use strict';

  var toggle = document.querySelector('[data-nav-toggle]');
  var panel = document.querySelector('[data-nav-panel]');
  var overlay = document.querySelector('[data-nav-overlay]');

  function setNav(open, restoreFocus) {
    if (!panel || !toggle) return;
    panel.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    var toggleIcon = toggle.querySelector('i');
    if (toggleIcon) toggleIcon.className = open ? 'bi bi-x-lg' : 'bi bi-list';
    if (overlay) overlay.hidden = !open;
    document.body.style.overflow = open ? 'hidden' : '';
    if (open) {
      var firstLink = panel.querySelector('.cn-site-nav__link, .cn-site-search input');
      if (firstLink) firstLink.focus();
    } else if (restoreFocus) {
      toggle.focus();
    }
  }

  if (toggle && panel) {
    toggle.addEventListener('click', function () {
      setNav(!panel.classList.contains('is-open'), true);
    });
  }

  if (overlay) {
    overlay.addEventListener('click', function () { setNav(false, true); });
  }

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Tab' && panel && panel.classList.contains('is-open')) {
      var focusable = Array.prototype.slice.call(panel.querySelectorAll(
        'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), summary'
      )).filter(function (element) { return element.getClientRects().length; });
      if (focusable.length) {
        var first = focusable[0];
        var last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
      return;
    }
    if (event.key !== 'Escape') return;
    var openDisclosure = panel && panel.querySelector('.cn-site-nav__disclosure[open]');
    if (openDisclosure) {
      openDisclosure.removeAttribute('open');
      var summary = openDisclosure.querySelector('summary');
      if (summary) summary.focus();
    } else if (panel && panel.classList.contains('is-open')) {
      setNav(false, true);
    }
  });

  document.addEventListener('click', function (event) {
    if (!panel || event.target.closest('.cn-site-nav__disclosure')) return;
    panel.querySelectorAll('.cn-site-nav__disclosure[open]').forEach(function (disclosure) {
      disclosure.removeAttribute('open');
    });
  });

  // Collapse the drawer when the viewport grows past the tablet breakpoint.
  window.addEventListener('resize', function () {
    if (window.innerWidth > 1160) setNav(false);
  });

  // Close the drawer after following an in-page link (same-document nav).
  if (panel) {
    panel.addEventListener('click', function (event) {
      if (event.target.closest('a') && window.innerWidth <= 1160) setNav(false);
    });
  }
}());
