/* ClassNest — App JS */
document.addEventListener('DOMContentLoaded', () => {
  // ── Sidebar toggle (mobile) ──
  const toggle = document.querySelector('.cn-topbar__toggle');
  const sidebar = document.querySelector('.cn-sidebar');
  const overlay = document.querySelector('.cn-sidebar-overlay');

  if (toggle && sidebar) {
    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('open');
      if (overlay) overlay.classList.toggle('show');
    });
    if (overlay) {
      overlay.addEventListener('click', () => {
        sidebar.classList.remove('open');
        overlay.classList.remove('show');
      });
    }
  }

  // ── Alert auto-dismiss ──
  document.querySelectorAll('.cn-alert__close').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.closest('.cn-alert').remove();
    });
  });

  // Auto-dismiss after 5s
  document.querySelectorAll('.cn-alert').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 300);
    }, 5000);
  });

  // ── Password visibility toggle ──
  document.querySelectorAll('.cn-password-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.previousElementSibling;
      if (input.type === 'password') {
        input.type = 'text';
        btn.innerHTML = '<i class="bi bi-eye-slash"></i>';
      } else {
        input.type = 'password';
        btn.innerHTML = '<i class="bi bi-eye"></i>';
      }
    });
  });

  // ── Delete confirmation ──
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', (e) => {
      if (!confirm(el.dataset.confirm || 'Are you sure?')) {
        e.preventDefault();
      }
    });
  });

  // ── Register Service Worker ──
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js', { scope: '/' })
      .catch(() => {});
  }
});
