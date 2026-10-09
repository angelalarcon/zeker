// Momento 2: los objetos del negocio flotan sueltos y, con el scroll, vuelan a su sitio en la web.
// Cada objeto se convierte en el icono de su pieza; al llegar, la pieza se "construye".
(function () {
  const section = document.getElementById("build");
  if (!section) return;

  const stage = document.getElementById("build-stage");
  const frame = document.getElementById("build-frame");
  const clock = document.getElementById("build-clock");
  const bar = document.getElementById("build-bar");
  const statusEl = document.getElementById("build-status");
  const urlEl = document.getElementById("build-url");
  const URL_TEXT = "latabernademaria.es";
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Duración (en progreso 0–1) del vuelo de cada objeto; los inicios se reparten en escalera.
  const FLIGHT = 0.4;
  const objs = Array.from(stage.querySelectorAll("[data-obj]"));
  const items = objs.map(function (el, i) {
    const target = stage.querySelector('[data-target="' + el.dataset.obj + '"]');
    return {
      el: el,
      bg: el.querySelector(".obj-bg"),
      icon: el.querySelector(".obj-icon"),
      target: target,
      slot: target.closest(".slot"),
      from: el.dataset.from.split(",").map(Number),
      rot: Number(el.dataset.rot || 0),
      start: (i * (1 - FLIGHT)) / Math.max(1, objs.length - 1),
      phase: i * 1.7,
    };
  });

  function clamp(v, a, b) { return Math.min(b, Math.max(a, v)); }
  function ease(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }

  // Progreso del scroll dentro de la sección: la construcción ocurre entre el 8% y el 85%.
  function buildProgress() {
    if (reduceMotion) return 1;
    const r = section.getBoundingClientRect();
    const total = r.height - window.innerHeight;
    const p = total > 0 ? clamp(-r.top / total, 0, 1) : 1;
    return clamp((p - 0.08) / 0.77, 0, 1);
  }

  let lastStatus = "";
  function setStatus(text) {
    if (text === lastStatus) return;
    lastStatus = text;
    statusEl.textContent = text;
  }

  function render(time) {
    const q = buildProgress();
    const s = stage.getBoundingClientRect();
    const seconds = time / 1000;

    items.forEach(function (it) {
      const size = it.el.offsetWidth;
      const iconPx = parseFloat(getComputedStyle(it.icon).fontSize);
      const r = it.target.getBoundingClientRect();
      const toX = r.left - s.left + r.width / 2;
      const toY = r.top - s.top + r.height / 2;
      const fromX = it.from[0] * s.width;
      const fromY = it.from[1] * s.height;

      const t = clamp((q - it.start) / FLIGHT, 0, 1);
      const e = ease(t);
      const drift = reduceMotion ? 0 : 1 - e;
      const x = fromX + (toX - fromX) * e + Math.sin(seconds * 0.9 + it.phase) * 8 * drift;
      const y = fromY + (toY - fromY) * e + Math.cos(seconds * 0.7 + it.phase) * 10 * drift;
      const scale = 1 + (r.width / iconPx - 1) * e;
      const rot = (it.rot + Math.sin(seconds * 0.6 + it.phase) * 4) * drift;

      it.el.style.transform =
        "translate(" + (x - size / 2) + "px," + (y - size / 2) + "px) rotate(" + rot + "deg) scale(" + scale + ")";
      it.el.style.visibility = "visible";
      it.bg.style.opacity = String(1 - clamp((e - 0.4) / 0.6, 0, 1));
      it.slot.classList.toggle("is-built", t >= 1);
    });

    clock.textContent = String(Math.round(q * 30));
    bar.style.transform = "scaleX(" + q + ")";

    // La URL se escribe sola al final, cuando la web ya está montada.
    const typed = Math.round(clamp((q - 0.86) / 0.14, 0, 1) * URL_TEXT.length);
    urlEl.textContent = URL_TEXT.slice(0, typed);
    frame.classList.toggle("is-live", q >= 1);

    if (q <= 0) setStatus("Nos cuentas tu negocio…");
    else if (q < 1) setStatus("Construyendo tu web…");
    else setStatus("Lista ✓");
  }

  // Solo animamos mientras la sección está a la vista.
  let running = false;
  function loop(time) {
    if (!running) return;
    render(time);
    requestAnimationFrame(loop);
  }

  if (reduceMotion) {
    const once = function () { render(0); };
    window.addEventListener("resize", once);
    window.addEventListener("load", once);
    once();
    return;
  }

  new IntersectionObserver(function (entries) {
    const visible = entries[0].isIntersecting;
    if (visible && !running) {
      running = true;
      requestAnimationFrame(loop);
    } else if (!visible) {
      running = false;
    }
  }).observe(section);
})();
