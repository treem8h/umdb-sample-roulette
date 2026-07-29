// UMDB Sample Roulette — service worker
const CACHE = 'umdb-sampler-v11';
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
  // audio /a/<id> → mai cache SW, passa in rete
  if (url.pathname.startsWith('/a/')) return;
  // cross-origin (thumbnail YouTube ecc.) → passa
  if (url.origin !== location.origin) return;
  // HTML/CSS/JS (tutto in index.html), manifest, videos.json, sw → NETWORK-FIRST
  // così ogni update arriva subito; la cache è solo fallback offline
  const fresh = e.request.mode === 'navigate'
    || url.pathname === '/' || url.pathname.endsWith('/')
    || url.pathname.endsWith('index.html')
    || url.pathname.endsWith('.webmanifest')
    || url.pathname.endsWith('videos.json')
    || url.pathname.endsWith('sw.js');
  if (fresh) {
    e.respondWith(
      fetch(e.request).then(r => { const cp = r.clone(); caches.open(CACHE).then(c => c.put(e.request, cp)); return r; })
                      .catch(() => caches.match(e.request))
    );
    return;
  }
  // asset statici (font, immagini) → cache-first (cambiano di rado)
  e.respondWith(caches.match(e.request).then(c => c || fetch(e.request)));
});
