// UMDB Sample Roulette — service worker
const CACHE = 'umdb-sampler-v5';
const SHELL = [
  './', './index.html', './manifest.webmanifest',
  './assets/logo.svg', './assets/desk.png',
  './assets/SairaSemiCondensed-SemiBold.ttf', './assets/SairaSemiCondensed-Medium.ttf',
  './assets/icon-192.png', './assets/icon-512.png'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET') return;
  // audio /a/<id> → mai cache del SW (grande, gestito da browser/server), passa sempre in rete
  if (url.pathname.startsWith('/a/')) return;
  // videos.json → network-first (pool sempre fresco), fallback cache
  if (url.pathname.endsWith('videos.json')) {
    e.respondWith(fetch(e.request).then(r => { const cp = r.clone(); caches.open(CACHE).then(c => c.put(e.request, cp)); return r; }).catch(() => caches.match(e.request)));
    return;
  }
  // cross-origin (thumbnail YouTube ecc.) → passa
  if (url.origin !== location.origin) return;
  // app shell → cache-first
  e.respondWith(caches.match(e.request).then(c => c || fetch(e.request)));
});
