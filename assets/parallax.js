// Parallax de las ilustraciones por capas: cada capa [data-depth] se desplaza según el scroll
// (y, en escritorio, un poco con el ratón). 0 = fondo quieto, 1 = primer plano.
(function () {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const scenes = Array.from(document.querySelectorAll("[data-parallax]"));
  const hero = document.querySelector(".hero-svg");
  const heroLayers = hero ? Array.from(hero.querySelectorAll(".layer")) : [];
  const finePointer = window.matchMedia("(pointer: fine)").matches;
  let mouseX = 0;
  let queued = false;

  function update() {
    queued = false;
    const vh = window.innerHeight;

    scenes.forEach(function (scene) {
      const r = scene.getBoundingClientRect();
      if (r.bottom < -100 || r.top > vh + 100) return;
      // -1 cuando la escena está bajo la pantalla, 1 cuando ya ha subido
      const p = Math.max(-1, Math.min(1, (vh / 2 - (r.top + r.height / 2)) / vh));
      scene.querySelectorAll("[data-depth]").forEach(function (layer) {
        const d = parseFloat(layer.dataset.depth);
        layer.style.transform = "translate3d(" + (mouseX * d * 8).toFixed(1) + "px," + (-p * d * 28).toFixed(1) + "px,0)";
      });
    });

    if (heroLayers.length) {
      const y = Math.min(window.scrollY, vh);
      heroLayers.forEach(function (layer) {
        const d = parseFloat(layer.dataset.depth);
        // el fondo baja más despacio que el primer plano: sensación de profundidad
        layer.style.transform = "translate(" + (mouseX * d * 14).toFixed(1) + "px," + (y * (1 - d) * 0.35).toFixed(1) + "px)";
      });
    }
  }

  function queue() {
    if (!queued) {
      queued = true;
      requestAnimationFrame(update);
    }
  }

  window.addEventListener("scroll", queue, { passive: true });
  window.addEventListener("resize", queue);
  if (finePointer) {
    window.addEventListener("pointermove", function (e) {
      mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
      queue();
    }, { passive: true });
  }
  update();
})();
