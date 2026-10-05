/* ClassNext — theme bootstrap (runs before first paint to avoid a flash) */
(function () {
  'use strict';
  var KEY = 'classnest_theme';
  var stored = null;
  try {
    stored = localStorage.getItem(KEY);
  } catch (e) {
    stored = null;
  }
  var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  var theme = stored || (prefersDark ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', theme);
  window.ClassNextTheme = {
    get: function () {
      return document.documentElement.getAttribute('data-theme') || 'light';
    },
    set: function (value) {
      document.documentElement.setAttribute('data-theme', value);
      try {
        localStorage.setItem(KEY, value);
      } catch (e) {
        /* storage unavailable (private mode) — theme still applies */
      }
    },
    toggle: function () {
      var next = this.get() === 'dark' ? 'light' : 'dark';
      this.set(next);
      return next;
    },
  };
})();
