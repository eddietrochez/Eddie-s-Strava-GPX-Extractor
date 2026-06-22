self.addEventListener('fetch', (event) => {
    // Esto es un Service Worker básico para cumplir con el requisito de instalación
    event.respondWith(fetch(event.request));
});
