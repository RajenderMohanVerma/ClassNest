const CACHE_VERSION = 'classnest-v1';
const STATIC_ASSETS = [
  '/',
  '/static/css/tokens.css',
  '/static/css/components.css',
  '/static/css/pages.css',
  '/static/js/app.js',
  '/static/js/install-prompt.js',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
];

// Install — cache static shell
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// Activate — clean old caches
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch — network-first for HTML, cache-first for static assets
self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);

  // Never cache POST or auth routes
  if (e.request.method !== 'GET') return;
  if (url.pathname.startsWith('/auth/')) return;

  if (url.pathname.startsWith('/static/') || url.pathname === '/manifest.json') {
    // Cache-first for static
    e.respondWith(
      caches.match(e.request).then((cached) => cached || fetch(e.request))
    );
  } else {
    // Network-first for pages
    e.respondWith(
      fetch(e.request)
        .then((resp) => {
          const clone = resp.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(e.request, clone));
          return resp;
        })
        .catch(() => caches.match(e.request))
    );
  }
});
