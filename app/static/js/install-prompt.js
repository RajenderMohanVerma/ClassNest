/* ClassNest — PWA Install Prompt (§20) */
(function () {
  'use strict';

  // Never show on desktop
  function isMobile() {
    const coarse = window.matchMedia('(pointer: coarse)').matches;
    const narrow = window.innerWidth < 768;
    return coarse && narrow;
  }

  // Already installed?
  function isInstalled() {
    return (
      window.matchMedia('(display-mode: standalone)').matches ||
      navigator.standalone === true ||
      localStorage.getItem('classnest_installed') === '1'
    );
  }

  // Dismissed recently?
  function wasDismissed() {
    const ts = localStorage.getItem('classnest_install_dismissed_at');
    if (!ts) return false;
    const elapsed = Date.now() - parseInt(ts, 10);
    return elapsed < 7 * 24 * 60 * 60 * 1000; // 7 days
  }

  if (!isMobile() || isInstalled() || wasDismissed()) return;

  // Detect iOS
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;

  // Store beforeinstallprompt event
  let deferredPrompt = null;
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    showSheet();
  });

  // Listen for successful install
  window.addEventListener('appinstalled', () => {
    localStorage.setItem('classnest_installed', '1');
    hideSheet();
  });

  // Build the sheet
  function buildSheet() {
    const overlay = document.createElement('div');
    overlay.className = 'cn-install-overlay';
    overlay.id = 'installOverlay';

    let actionsHTML;
    if (isIOS) {
      actionsHTML = `
        <div class="cn-install-sheet__steps">
          <p><strong>To install:</strong></p>
          <p>1. Tap the <strong>Share</strong> button <i class="bi bi-box-arrow-up"></i></p>
          <p>2. Scroll down and tap <strong>Add to Home Screen</strong></p>
          <p>3. Tap <strong>Add</strong></p>
        </div>`;
    } else if (deferredPrompt) {
      actionsHTML = `
        <div class="cn-install-sheet__actions">
          <button class="cn-btn cn-btn--primary cn-btn--lg" id="installBtn">
            <i class="bi bi-download"></i> Install
          </button>
          <button class="cn-btn cn-btn--outline cn-btn--lg" id="installDismiss">
            Not now
          </button>
        </div>`;
    } else {
      actionsHTML = `
        <div class="cn-install-sheet__steps">
          <p><strong>To install:</strong></p>
          <p>Open the browser menu (⋮) and tap <strong>"Add to Home Screen"</strong> or <strong>"Install App"</strong>.</p>
        </div>
        <div class="cn-install-sheet__actions" style="margin-top: var(--cn-space-4);">
          <button class="cn-btn cn-btn--outline cn-btn--lg" id="installDismiss" style="flex:1;">
            Got it
          </button>
        </div>`;
    }

    const sheet = document.createElement('div');
    sheet.className = 'cn-install-sheet';
    sheet.id = 'installSheet';
    sheet.innerHTML = `
      <button class="cn-install-sheet__close" id="installClose" aria-label="Close">&times;</button>
      <div class="cn-install-sheet__header">
        <div class="cn-install-sheet__icon"><i class="bi bi-mortarboard-fill"></i></div>
        <div>
          <div class="cn-install-sheet__title">ClassNest</div>
          <div class="cn-install-sheet__subtitle">Install the app</div>
        </div>
      </div>
      <div class="cn-install-sheet__benefit">
        Faster access — open ClassNest straight from your home screen.
      </div>
      ${actionsHTML}
    `;

    document.body.appendChild(overlay);
    document.body.appendChild(sheet);

    // Events
    overlay.addEventListener('click', dismiss);
    sheet.querySelector('#installClose').addEventListener('click', dismiss);

    const installBtn = sheet.querySelector('#installBtn');
    if (installBtn) {
      installBtn.addEventListener('click', async () => {
        if (deferredPrompt) {
          deferredPrompt.prompt();
          const result = await deferredPrompt.userChoice;
          if (result.outcome === 'accepted') {
            localStorage.setItem('classnest_installed', '1');
          }
          deferredPrompt = null;
          hideSheet();
        }
      });
    }

    const dismissBtn = sheet.querySelector('#installDismiss');
    if (dismissBtn) {
      dismissBtn.addEventListener('click', dismiss);
    }
  }

  function showSheet() {
    if (document.getElementById('installSheet')) return;
    buildSheet();
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        const o = document.getElementById('installOverlay');
        const s = document.getElementById('installSheet');
        if (o) o.classList.add('show');
        if (s) s.classList.add('show');
      });
    });
  }

  function hideSheet() {
    const o = document.getElementById('installOverlay');
    const s = document.getElementById('installSheet');
    if (o) { o.classList.remove('show'); setTimeout(() => o.remove(), 250); }
    if (s) { s.classList.remove('show'); setTimeout(() => s.remove(), 250); }
  }

  function dismiss() {
    localStorage.setItem('classnest_install_dismissed_at', Date.now().toString());
    hideSheet();
  }

  // For iOS or fallback (no beforeinstallprompt), show after page load
  if (isIOS || !('BeforeInstallPromptEvent' in window)) {
    if (document.readyState === 'complete') {
      setTimeout(showSheet, 500);
    } else {
      window.addEventListener('load', () => setTimeout(showSheet, 500));
    }
  }
})();
