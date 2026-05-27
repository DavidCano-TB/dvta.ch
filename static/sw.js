/**
 * DVDcoin Bank - Service Worker
 * Ensures fresh HTML on every load and caches static assets
 */

const CACHE_NAME = 'dvdcoin-bank-v3-20260528';
const BASE_PATH = '/bank';

// Assets to cache
const STATIC_ASSETS = [
  `${BASE_PATH}/static/css/unified-nav.css`,
  `${BASE_PATH}/static/js/unified-nav.js`,
  `${BASE_PATH}/static/js/i18n.js`,
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn('SW: Failed to cache some assets', err);
      });
    })
  );
  self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - network first for HTML, cache first for assets
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Only handle GET requests — never intercept POST/PUT/DELETE/etc (login uses POST)
  if (request.method !== 'GET') {
    return;
  }

  // Always fetch HTML fresh (no cache)
  const accept = request.headers.get('accept') || '';
  if (request.mode === 'navigate' || accept.includes('text/html')) {
    event.respondWith(
      fetch(request).catch(() => {
        return caches.match(`${BASE_PATH}/`);
      })
    );
    return;
  }

  // API calls - always network, never cache
  if (url.pathname.startsWith(`${BASE_PATH}/api/`)) {
    event.respondWith(fetch(request));
    return;
  }

  // Static assets - cache first, fallback to network
  if (url.pathname.startsWith(`${BASE_PATH}/static/`)) {
    event.respondWith(
      caches.match(request).then((cached) => {
        if (cached) {
          return cached;
        }
        return fetch(request).then((response) => {
          // Cache successful responses
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        });
      })
    );
    return;
  }

  // Default - network only
  event.respondWith(fetch(request));
});

// Handle messages from clients
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
