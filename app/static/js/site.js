/* ClassNext public site interactions.
   Kept in a separate file because the Content-Security-Policy allows
   'self' scripts only — inline handlers are blocked. */
(function () {
  'use strict';

  var toggle = document.querySelector('[data-nav-toggle]');
  var panel = document.querySelector('[data-nav-panel]');
  var overlay = document.querySelector('[data-nav-overlay]');

  function setNav(open) {
    if (!panel || !toggle) return;
    panel.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
    if (overlay) overlay.hidden = !open;
    document.body.style.overflow = open ? 'hidden' : '';
  }

  if (toggle && panel) {
    toggle.addEventListener('click', function () {
      setNav(!panel.classList.contains('is-open'));
    });
  }

  if (overlay) {
    overlay.addEventListener('click', function () { setNav(false); });
  }

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') setNav(false);
  });

  // Collapse the drawer when the viewport grows past the mobile breakpoint,
  // otherwise the panel stays hidden behind the desktop nav.
  window.addEventListener('resize', function () {
    if (window.innerWidth > 900) setNav(false);
  });

  // Close the drawer after following an in-page link (same-document nav).
  if (panel) {
    panel.addEventListener('click', function (event) {
      if (event.target.closest('a') && window.innerWidth <= 900) setNav(false);
    });
  }
}());