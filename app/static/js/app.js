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

    /* ── Live class catalog search ───────────────────────── */
    var classSearch = document.querySelector('[data-class-search]');
    var classItems = Array.prototype.slice.call(document.querySelectorAll('[data-class-item]'));
    if (classSearch && classItems.length) {
      var classCount = document.querySelector('[data-class-count]');
      var classEmpty = document.querySelector('[data-class-no-results]');
      var filterClasses = function () {
        var query = classSearch.value.trim().toLocaleLowerCase();
        var shown = 0;
        classItems.forEach(function (item) {
          var matches = !query || (item.dataset.search || '').indexOf(query) !== -1;
          item.hidden = !matches;
          if (matches) shown += 1;
        });
        if (classCount) {
          classCount.textContent = shown + ' class' + (shown === 1 ? '' : 'es') + ' shown';
        }
        if (classEmpty) classEmpty.hidden = shown !== 0;
      };
      classSearch.addEventListener('input', filterClasses);
      classSearch.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
          classSearch.value = '';
          filterClasses();
          classSearch.blur();
        }
      });
      document.addEventListener('keydown', function (event) {
        var target = event.target;
        var isTyping = target && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName));
        if (event.key === '/' && !isTyping && !event.ctrlKey && !event.metaKey && !event.altKey) {
          event.preventDefault();
          classSearch.focus();
        }
      });
    }

    /* ── Searchable notices and premium courses ────────── */
    [
      { input: '[data-notice-search]', items: '[data-notice-item]', count: '[data-notice-count]', empty: '[data-notice-no-results]', noun: 'notice' },
      { input: '[data-premium-search]', items: '[data-premium-card]', count: '[data-premium-count]', empty: '[data-premium-no-results]', noun: 'course' }
    ].forEach(function (config) {
      var input = document.querySelector(config.input);
      var items = Array.prototype.slice.call(document.querySelectorAll(config.items));
      if (!input || !items.length) return;

      var filter = function () {
        var term = input.value.trim().toLocaleLowerCase();
        var shown = 0;
        items.forEach(function (item) {
          var visible = !term || (item.dataset.search || '').indexOf(term) !== -1;
          item.hidden = !visible;
          if (visible) shown += 1;
        });
        var count = document.querySelector(config.count);
        var empty = document.querySelector(config.empty);
        if (count) count.textContent = shown + ' ' + config.noun + (shown === 1 ? '' : 's') + ' shown';
        if (empty) empty.hidden = shown > 0;
      };
      input.addEventListener('input', filter);
      input.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
          input.value = '';
          filter();
          input.blur();
        }
      });
      document.addEventListener('keydown', function (event) {
        var target = event.target;
        var isTyping = target && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName));
        if (event.key === '/' && !isTyping && !event.ctrlKey && !event.metaKey && !event.altKey) {
          event.preventDefault();
          input.focus();
        }
      });
    });

    /* ── FAQ topic/search filters and disclosure controls ── */
    var faqSearch = document.querySelector('[data-faq-search]');
    var faqItems = Array.prototype.slice.call(document.querySelectorAll('[data-faq-entry]'));
    if (faqSearch && faqItems.length) {
      var activeTopic = 'all';
      var filterFaqs = function () {
        var term = faqSearch.value.trim().toLocaleLowerCase();
        var shown = 0;
        faqItems.forEach(function (item) {
          var topicMatches = activeTopic === 'all' || item.dataset.category === activeTopic;
          var textMatches = !term || (item.dataset.search || '').indexOf(term) !== -1;
          var visible = topicMatches && textMatches;
          item.hidden = !visible;
          if (visible) shown += 1;
        });
        document.querySelectorAll('[data-faq-group]').forEach(function (group) {
          group.hidden = !group.querySelector('[data-faq-entry]:not([hidden])');
        });
        var count = document.querySelector('[data-faq-count]');
        var empty = document.querySelector('[data-faq-no-results]');
        if (count) count.textContent = shown + ' question' + (shown === 1 ? '' : 's');
        if (empty) empty.hidden = shown > 0;
      };

      faqSearch.addEventListener('input', filterFaqs);
      faqSearch.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
          faqSearch.value = '';
          filterFaqs();
          faqSearch.blur();
        }
      });
      document.addEventListener('keydown', function (event) {
        var target = event.target;
        var isTyping = target && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName));
        if (event.key === '/' && !isTyping && !event.ctrlKey && !event.metaKey && !event.altKey) {
          event.preventDefault();
          faqSearch.focus();
        }
      });
      document.querySelectorAll('[data-faq-topic]').forEach(function (button) {
        button.addEventListener('click', function () {
          activeTopic = button.dataset.faqTopic;
          document.querySelectorAll('[data-faq-topic]').forEach(function (topic) {
            var selected = topic === button;
            topic.classList.toggle('is-active', selected);
            topic.setAttribute('aria-pressed', selected ? 'true' : 'false');
          });
          filterFaqs();
        });
      });

      var expand = document.querySelector('[data-faq-expand]');
      var collapse = document.querySelector('[data-faq-collapse]');
      if (expand) expand.addEventListener('click', function () {
        faqItems.forEach(function (item) { if (!item.hidden) item.open = true; });
        expand.setAttribute('aria-expanded', 'true');
      });
      if (collapse) collapse.addEventListener('click', function () {
        faqItems.forEach(function (item) { item.open = false; });
        if (expand) expand.setAttribute('aria-expanded', 'false');
      });
      faqItems.forEach(function (item) {
        item.addEventListener('toggle', function () {
          if (expand && !faqItems.some(function (entry) { return !entry.open; })) {
            expand.setAttribute('aria-expanded', 'true');
          } else if (expand) {
            expand.setAttribute('aria-expanded', 'false');
          }
        });
      });
      var resetFaqSearch = document.querySelector('[data-faq-reset]');
      if (resetFaqSearch) resetFaqSearch.addEventListener('click', function () {
        faqSearch.value = '';
        activeTopic = 'all';
        document.querySelectorAll('[data-faq-topic]').forEach(function (topic) {
          var selected = topic.dataset.faqTopic === 'all';
          topic.classList.toggle('is-active', selected);
          topic.setAttribute('aria-pressed', selected ? 'true' : 'false');
        });
        filterFaqs();
        faqSearch.focus();
      });
    }

    /* ── Contact form topic shortcuts and character count ── */
    var contactSubject = document.querySelector('[data-contact-subject]');
    var contactMessage = document.querySelector('[data-contact-message]');
    var contactCount = document.querySelector('[data-contact-count]');
    document.querySelectorAll('[data-contact-topic]').forEach(function (button) {
      button.addEventListener('click', function () {
        if (contactSubject) contactSubject.value = button.dataset.contactTopic;
        if (contactMessage) contactMessage.focus();
      });
    });
    if (contactMessage && contactCount) {
      var updateMessageCount = function () {
        contactCount.textContent = contactMessage.value.length + ' / 4000';
      };
      contactMessage.addEventListener('input', updateMessageCount);
      updateMessageCount();
    }

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
