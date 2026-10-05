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
    document.querySelectorAll('#themeToggle, [data-theme-toggle]').forEach(function (themeToggle) {
      if (!window.ClassNextTheme) return;
      var icon = themeToggle.querySelector('[data-theme-icon]');
      var syncIcon = function () {
        var dark = window.ClassNextTheme.get() === 'dark';
        if (icon) icon.className = dark ? 'bi bi-sun' : 'bi bi-moon-stars';
        themeToggle.setAttribute('aria-pressed', dark ? 'true' : 'false');
        themeToggle.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
      };
      syncIcon();
      themeToggle.addEventListener('click', function () {
        window.ClassNextTheme.toggle();
        syncIcon();
      });
    });

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

    /* ── Class -> subject -> chapter selectors ──────────── */
    document.querySelectorAll('.cn-catalog-form').forEach(function (form) {
      var classSelect = form.querySelector('[data-catalog-class]');
      var subjectSelect = form.querySelector('[data-catalog-subject]');
      var chapterSelect = form.querySelector('[data-catalog-chapter]');
      if (!classSelect || !subjectSelect) return;

      var filterOptions = function (select, predicate, emptyLabel) {
        var selected = select.value;
        var visibleCount = 0;
        Array.prototype.forEach.call(select.options, function (option) {
          if (!option.value) {
            option.hidden = false;
            option.disabled = false;
            return;
          }
          var visible = predicate(option);
          option.hidden = !visible;
          option.disabled = !visible;
          if (visible) visibleCount += 1;
        });
        if (selected && select.selectedOptions.length && select.selectedOptions[0].disabled) {
          select.value = '';
        }
        if (select.options[0]) select.options[0].textContent = emptyLabel;
        select.disabled = visibleCount === 0;
      };

      var updateCatalogOptions = function () {
        var classId = classSelect.value;
        filterOptions(subjectSelect, function (option) {
          return Boolean(classId) && option.dataset.classId === classId;
        }, classId ? 'Choose a subject' : 'Choose the class first');

        if (!chapterSelect) return;
        var subjectId = subjectSelect.value;
        filterOptions(chapterSelect, function (option) {
          return Boolean(classId && subjectId)
            && option.dataset.classId === classId
            && option.dataset.subjectId === subjectId;
        }, subjectId ? 'Choose a chapter' : 'Choose a subject first');
      };

      classSelect.addEventListener('change', updateCatalogOptions);
      subjectSelect.addEventListener('change', updateCatalogOptions);
      updateCatalogOptions();
    });

    /* ── Service worker ─────────────────────────────────── */
    if ('serviceWorker' in navigator && window.isSecureContext) {
      window.addEventListener('load', function () {
        navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(function () {});
      });
    }
  });
})();
