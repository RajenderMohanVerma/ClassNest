/* ClassNext — progressive enhancement for the server-rendered UI */
(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    var body = document.body;

    /* ── Sidebar drawer (mobile) ─────────────────────────── */
    var toggle = document.querySelector('.cn-topbar__toggle');
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebarOverlay');

    function setSidebar(open) {
      if (!sidebar) return;
      sidebar.classList.toggle('open', open);
      if (overlay) overlay.classList.toggle('show', open);
      body.classList.toggle('cn-sidebar-open', open);
      if (toggle) toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    }

    if (toggle && sidebar) {
      toggle.addEventListener('click', function () {
        setSidebar(!sidebar.classList.contains('open'));
      });
    }
    if (overlay) {
      overlay.addEventListener('click', function () { setSidebar(false); });
    }
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') setSidebar(false);
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 768) setSidebar(false);
    });

    /* ── Alerts ─────────────────────────────────────────── */
    document.querySelectorAll('.cn-alert__close').forEach(function (button) {
      button.addEventListener('click', function () {
        var alert = button.closest('.cn-alert');
        if (alert) alert.remove();
      });
    });
    document.querySelectorAll('.cn-alert').forEach(function (alert) {
      window.setTimeout(function () {
        alert.style.opacity = '0';
        window.setTimeout(function () { alert.remove(); }, 300);
      }, 6000);
    });

    /* ── Password visibility ────────────────────────────── */
    document.querySelectorAll('.cn-password-toggle').forEach(function (button) {
      button.addEventListener('click', function () {
        var input = button.previousElementSibling;
        if (!input) return;
        var reveal = input.type === 'password';
        input.type = reveal ? 'text' : 'password';
        button.innerHTML = reveal
          ? '<i class="bi bi-eye-slash"></i>'
          : '<i class="bi bi-eye"></i>';
        button.setAttribute('aria-label', reveal ? 'Hide password' : 'Show password');
      });
    });

    /* ── Destructive action confirmation ─────────────────── */
    document.querySelectorAll('[data-confirm]').forEach(function (element) {
      element.addEventListener('submit', function (event) {
        if (!window.confirm(element.dataset.confirm || 'Are you sure?')) {
          event.preventDefault();
        }
      });
    });

    /* ── Theme toggle ───────────────────────────────────── */
    var themeToggle = document.getElementById('themeToggle');
    if (themeToggle && window.ClassNextTheme) {
      var icon = themeToggle.querySelector('[data-theme-icon]');
      var syncIcon = function () {
        var dark = window.ClassNextTheme.get() === 'dark';
        if (icon) icon.className = dark ? 'bi bi-sun' : 'bi bi-moon-stars';
        themeToggle.setAttribute('aria-pressed', dark ? 'true' : 'false');
      };
      syncIcon();
      themeToggle.addEventListener('click', function () {
        window.ClassNextTheme.toggle();
        syncIcon();
      });
    }

    /* ── Error page "go back" ───────────────────────────── */
    document.querySelectorAll('[data-go-back]').forEach(function (link) {
      link.addEventListener('click', function (event) {
        event.preventDefault();
        if (window.history.length > 1) {
          window.history.back();
        } else {
          window.location.href = '/';
        }
      });
    });

    /* ── Filter forms: submit on select change ──────────── */
    document.querySelectorAll('.cn-filter-bar select').forEach(function (select) {
      select.addEventListener('change', function () {
        if (select.form) select.form.submit();
      });
    });

    /* ── Service worker ─────────────────────────────────── */
    if ('serviceWorker' in navigator && window.isSecureContext) {
      window.addEventListener('load', function () {
        navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(function () {});
      });
    }
  });
})();
