/* ClassNext — PWA install sheet (mobile only, never on desktop) */
(function () {
  'use strict';

  var DISMISS_KEY = 'classnest_install_dismissed_at';
  var INSTALLED_KEY = 'classnest_installed';
  var DISMISS_WINDOW_MS = 7 * 24 * 60 * 60 * 1000;
  var SHOWN_KEY = 'classnest_install_sheet_shown';

  var sheet = null;
  var overlay = null;
  var deferredPrompt = null;

  function storage() {
    try {
      return window.localStorage;
    } catch (e) {
      return null;
    }
  }

  function readFlag(key) {
    var store = storage();
    return store ? store.getItem(key) : null;
  }

  function isMobile() {
    var coarse = window.matchMedia('(pointer: coarse)').matches;
    return coarse && window.innerWidth < 768;
  }

  function isIOS() {
    var ua = navigator.userAgent;
    var iPadOS = /Macintosh/.test(ua) && typeof navigator.maxTouchPoints === 'number' && navigator.maxTouchPoints > 1;
    return /iPad|iPhone|iPod/.test(ua) || iPadOS;
  }

  function isStandalone() {
    return (
      window.matchMedia('(display-mode: standalone)').matches ||
      window.matchMedia('(display-mode: fullscreen)').matches ||
      navigator.standalone === true ||
      readFlag(INSTALLED_KEY) === '1'
    );
  }

  function dismissedRecently() {
    var stamp = parseInt(readFlag(DISMISS_KEY) || '0', 10);
    if (!stamp) return false;
    return Date.now() - stamp < DISMISS_WINDOW_MS;
  }

  function markShown() {
    var store = storage();
    if (store) store.setItem(SHOWN_KEY, String(Date.now()));
  }

  function markDismissed() {
    var store = storage();
    if (store) store.setItem(DISMISS_KEY, String(Date.now()));
  }

  function markInstalled() {
    var store = storage();
    if (store) store.setItem(INSTALLED_KEY, '1');
  }

  function alreadyShownThisVisit() {
    var stamp = parseInt(readFlag(SHOWN_KEY) || '0', 10);
    // Show at most once per browser session even after closing the sheet.
    return stamp && Date.now() - stamp < 30 * 60 * 1000;
  }

  function hide() {
    [overlay, sheet].forEach(function (node) {
      if (!node) return;
      node.classList.remove('show');
      window.setTimeout(function () { node.remove(); }, 250);
    });
    overlay = null;
    sheet = null;
  }

  function dismiss() {
    markDismissed();
    hide();
  }

  function buildSheet() {
    overlay = document.createElement('div');
    overlay.className = 'cn-install-overlay';

    var actions;
    if (isIOS()) {
      actions =
        '<div class="cn-install-sheet__steps">' +
        '<p><strong>To install on iPhone or iPad:</strong></p>' +
        '<p>1. Tap the <strong>Share</strong> button.</p>' +
        '<p>2. Scroll down and tap <strong>Add to Home Screen</strong>.</p>' +
        '<p>3. Tap <strong>Add</strong>.</p>' +
        '</div>' +
        '<div class="cn-install-sheet__actions">' +
        '<button type="button" class="cn-btn cn-btn--primary cn-btn--lg" data-install-dismiss>Got it</button>' +
        '</div>';
    } else if (deferredPrompt) {
      actions =
        '<div class="cn-install-sheet__actions">' +
        '<button type="button" class="cn-btn cn-btn--primary cn-btn--lg" data-install-accept>' +
        '<i class="bi bi-download"></i> Install</button>' +
        '<button type="button" class="cn-btn cn-btn--outline cn-btn--lg" data-install-dismiss>Not now</button>' +
        '</div>';
    } else {
      actions =
        '<div class="cn-install-sheet__steps">' +
        '<p>Open the browser menu and choose <strong>&ldquo;Add to Home screen&rdquo;</strong> ' +
        'or <strong>&ldquo;Install app&rdquo;</strong>.</p>' +
        '</div>' +
        '<div class="cn-install-sheet__actions">' +
        '<button type="button" class="cn-btn cn-btn--outline cn-btn--lg" data-install-dismiss>Got it</button>' +
        '</div>';
    }

    sheet = document.createElement('div');
    sheet.className = 'cn-install-sheet';
    sheet.setAttribute('role', 'dialog');
    sheet.setAttribute('aria-modal', 'false');
    sheet.setAttribute('aria-label', 'Install the ClassNext app');
    sheet.innerHTML =
      '<button type="button" class="cn-install-sheet__close" data-install-dismiss aria-label="Close">&times;</button>' +
      '<div class="cn-install-sheet__header">' +
      '<span class="cn-install-sheet__icon"><i class="bi bi-mortarboard-fill"></i></span>' +
      '<span>' +
      '<span class="cn-install-sheet__title">ClassNext</span>' +
      '<span class="cn-install-sheet__subtitle">Install the app</span>' +
      '</span>' +
      '</div>' +
      '<p class="cn-install-sheet__benefit">Faster access &mdash; open ClassNext straight from your home screen.</p>' +
      actions;

    document.body.appendChild(overlay);
    document.body.appendChild(sheet);

    overlay.addEventListener('click', dismiss);
    sheet.querySelectorAll('[data-install-dismiss]').forEach(function (node) {
      node.addEventListener('click', dismiss);
    });

    var accept = sheet.querySelector('[data-install-accept]');
    if (accept) {
      accept.addEventListener('click', function () {
        if (!deferredPrompt) {
          dismiss();
          return;
        }
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then(function (choice) {
          if (choice && choice.outcome === 'accepted') markInstalled();
          deferredPrompt = null;
          hide();
        }).catch(function () { hide(); });
      });
    }
  }

  function show() {
    if (sheet || document.querySelector('.cn-install-sheet')) return;
    if (!isMobile() || isStandalone() || dismissedRecently() || alreadyShownThisVisit()) return;

    markShown();
    buildSheet();
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () {
        if (overlay) overlay.classList.add('show');
        if (sheet) sheet.classList.add('show');
      });
    });
  }

  if (!isMobile() || isStandalone() || dismissedRecently()) return;

  window.addEventListener('beforeinstallprompt', function (event) {
    event.preventDefault();
    deferredPrompt = event;
    show();
  });

  window.addEventListener('appinstalled', function () {
    markInstalled();
    hide();
  });

  // iOS and browsers without beforeinstallprompt: show shortly after load.
  if (isIOS() || !('onbeforeinstallprompt' in window)) {
    if (document.readyState === 'complete') {
      window.setTimeout(show, 600);
    } else {
      window.addEventListener('load', function () { window.setTimeout(show, 600); });
    }
  }
})();
