// service-worker.js
// v2: red primero, caché como respaldo solo sin conexión.
// (v1 guardaba todo en caché primero, por eso el diseño no se
// actualizaba solo en los celulares con la app ya instalada)

const CACHE_NAME = "mdp-guide-v2";
const APP_SHELL = [
  "./",
  "./index.html",
  "./manifest.json",
  "./css/styles.css",
  "./js/config.js",
  "./js/api.js",
  "./js/clima.js",
  "./js/actividades.js",
  "./js/asistente.js",
  "./js/favoritos.js",
  "./js/app.js",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// Red primero para TODO (HTML, CSS, JS y /api/). Si el pedido de red
// falla (sin internet), recién ahí se usa lo guardado en caché.
// Esto prioriza que siempre se vea la última versión publicada; el
// modo offline queda como respaldo, no como comportamiento normal.
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  const esApi = url.pathname.includes("/api/");

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (!esApi && event.request.method === "GET" && response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() =>
        caches.match(event.request).then(
          (cached) =>
            cached ||
            (esApi
              ? new Response(
                  JSON.stringify({ error: "Sin conexión. Mostrando datos guardados." }),
                  { headers: { "Content-Type": "application/json" } }
                )
              : Response.error())
        )
      )
  );
});
