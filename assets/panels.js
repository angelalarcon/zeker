// Transiciones entre secciones con la Z y la K de ZEKER.
// El scroll es normal: nada se fija ni se mueve con JavaScript. Al cruzar de una sección a otra,
// una capa fija y transparente dibuja la letra (Z: un solo trazo barra–diagonal–barra;
// K: asta y flecha que nacen del mismo punto), la engrosa un poco y la desvanece mientras la
// siguiente sección sube por debajo. El avance se suaviza para que siga al dedo sin saltos.
(function () {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const nav = document.getElementById("nav-el");
  const panels = Array.from(document.querySelectorAll(".panel"));
  if (!panels.length) return;

  const NS = "http://www.w3.org/2000/svg";
  const layer = document.createElementNS(NS, "svg");
  layer.setAttribute("class", "zk-layer");
  layer.setAttribute("aria-hidden", "true");
  layer.setAttribute("preserveAspectRatio", "none");
  const paths = [0, 1].map(function () {
    const p = document.createElementNS(NS, "path");
    p.setAttribute("fill", "none");
    p.setAttribute("stroke-linecap", "round");
    p.setAttribute("stroke-linejoin", "round");
    p.setAttribute("pathLength", "1");
    layer.appendChild(p);
    return p;
  });
  document.body.appendChild(layer);

  let w = 0, h = 0, navH = 0;
  let shown = 0;       // progreso que se está dibujando (suavizado)
  let active = null;   // panel cuyo borde se está cruzando
  let target = 0;
  let running = false;

  function measure() {
    navH = nav ? nav.offsetHeight : 0;
    w = window.innerWidth;
    h = window.innerHeight - navH;
    layer.setAttribute("viewBox", "0 0 " + w + " " + h);
    layer.style.top = navH + "px";
    layer.style.height = h + "px";
    document.documentElement.style.setProperty("--nav-h", navH + "px");
  }

  function letter(shape) {
    if (shape === "k") {
      const x = w * 0.32, my = h * 0.5, x1 = w * 0.8;
      return ["M" + x + " " + h * 0.1 + " V" + h * 0.9,
              "M" + x1 + " " + h * 0.12 + " L" + (x + 4) + " " + my + " L" + x1 + " " + h * 0.88];
    }
    const x0 = w * 0.18, x1 = w * 0.82, y0 = h * 0.18, y1 = h * 0.82;
    return ["M" + x0 + " " + y0 + " H" + x1 + " L" + x0 + " " + y1 + " H" + x1, ""];
  }

  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function ease(v) { return v * v * (3 - 2 * v); }

  // Qué borde se está cruzando: la sección cuyo borde superior está entre el pie de la pantalla
  // y la barra de navegación. Progreso 0 cuando asoma, 1 cuando llega arriba.
  function pick() {
    const vh = window.innerHeight;
    let best = null, bestP = 0;
    panels.forEach(function (panel) {
      const top = panel.getBoundingClientRect().top;
      if (top > navH && top < vh) {
        const p = 1 - (top - navH) / (vh - navH);
        if (!best || p > bestP) { best = panel; bestP = p; }
      }
    });
    return { panel: best, p: bestP };
  }

  function draw() {
    if (!active || shown <= 0.001 || shown >= 0.999) {
      layer.style.opacity = "0";
      return;
    }
    const d = letter(active.dataset.shape === "k" ? "k" : "z");
    const color = active.dataset.ink || "#C24F2C";
    const draw = ease(clamp(shown / 0.45));                    // la letra se dibuja
    const grow = ease(clamp((shown - 0.3) / 0.4));             // gana grosor
    const fade = 1 - ease(clamp((shown - 0.62) / 0.33));       // y se desvanece
    const width = 3 + grow * Math.min(w, h) * 0.16;
    paths.forEach(function (p, i) {
      p.setAttribute("d", d[i] || "M0 0");
      p.setAttribute("stroke", color);
      p.setAttribute("stroke-width", width.toFixed(1));
      p.style.strokeDasharray = "1 1";
      p.style.strokeDashoffset = String(1 - draw);
      p.style.display = d[i] ? "" : "none";
    });
    layer.style.opacity = String(0.92 * fade);
  }

  function frame() {
    const diff = target - shown;
    // suavizado exponencial: sigue al scroll sin tirones
    shown = Math.abs(diff) < 0.002 ? target : shown + diff * 0.2;
    draw();
    if (shown !== target) {
      requestAnimationFrame(frame);
    } else {
      running = false;
    }
  }

  function onScroll() {
    const pk = pick();
    if (pk.panel !== active) {
      active = pk.panel;
      shown = pk.panel ? Math.min(pk.p, 0.02) : 0;
    }
    target = pk.panel ? pk.p : 0;
    if (!running) {
      running = true;
      requestAnimationFrame(frame);
    }
  }

  measure();
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", function () { measure(); onScroll(); });
})();
