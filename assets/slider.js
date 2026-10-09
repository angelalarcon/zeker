// Slider de planes: pista con scroll-snap, flechas y puntos. Funciona también con el dedo.
(function () {
  document.querySelectorAll("[data-slider]").forEach(function (root) {
    const track = root.querySelector("[data-slider-track]");
    const slides = Array.from(track.children);
    const dots = Array.from(root.querySelectorAll("[data-slider-dot]"));
    const prev = root.querySelector("[data-slider-prev]");
    const next = root.querySelector("[data-slider-next]");
    const smooth = window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
    let current = 0;

    function go(i) {
      const slide = slides[Math.max(0, Math.min(slides.length - 1, i))];
      track.scrollTo({ left: slide.offsetLeft - track.offsetLeft - (track.clientWidth - slide.offsetWidth) / 2, behavior: smooth });
    }

    function sync() {
      const center = track.scrollLeft + track.clientWidth / 2;
      let best = 0;
      slides.forEach(function (s, i) {
        const c = s.offsetLeft - track.offsetLeft + s.offsetWidth / 2;
        if (Math.abs(c - center) < Math.abs(slides[best].offsetLeft - track.offsetLeft + slides[best].offsetWidth / 2 - center)) best = i;
      });
      current = best;
      dots.forEach(function (d, i) { d.setAttribute("aria-current", i === best ? "true" : "false"); });
      if (prev) prev.disabled = best === 0;
      if (next) next.disabled = best === slides.length - 1;
    }

    dots.forEach(function (d, i) { d.addEventListener("click", function () { go(i); }); });
    if (prev) prev.addEventListener("click", function () { go(current - 1); });
    if (next) next.addEventListener("click", function () { go(current + 1); });
    track.addEventListener("scroll", function () { window.requestAnimationFrame(sync); }, { passive: true });
    window.addEventListener("resize", sync);
    sync();
  });
})();
