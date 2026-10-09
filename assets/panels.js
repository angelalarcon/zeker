// Transiciones entre secciones con la Z y la K de ZEKER.
// Cada .panel queda fijo (sticky) al llegar arriba. El siguiente panel no sube deslizándose:
// se queda en su sitio y se descubre a través de la forma de una letra (Z: barra, diagonal, barra;
// K: barra vertical y flecha) dibujada primero como un trazo de color fino que se ensancha
// hasta llenar la pantalla y luego se desvanece dejando ver el contenido.
(function () {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (!window.CSS || !CSS.supports("clip-path", "path('M0 0')")) return;

  const root = document.documentElement;
  const nav = document.getElementById("nav-el");
  const panels = Array.from(document.querySelectorAll(".panel"));
  if (!panels.length) return;

  root.classList.add("panels-on");

  const items = panels.map(function (panel, i) {
    const marker = document.createElement("div");
    marker.className = "panel-marker";
    panel.parentNode.insertBefore(marker, panel);
    const ink = document.createElement("div");
    ink.className = "panel-ink";
    ink.style.background = panel.dataset.ink || "#C24F2C";
    panel.appendChild(ink);
    panel.style.zIndex = String(i + 1);
    if (i < panels.length - 1) {
      const dwell = document.createElement("div");
      dwell.className = "panel-dwell";
      panel.parentNode.insertBefore(dwell, panel.nextSibling);
    }
    return { panel: panel, marker: marker, ink: ink, shape: panel.dataset.shape === "k" ? "k" : "z", state: "" };
  });

  let navH = 0;
  let vh = 0;

  function measure() {
    navH = nav ? nav.offsetHeight : 0;
    vh = window.innerHeight;
    root.style.setProperty("--nav-h", navH + "px");
    items.forEach(function (it) {
      // un panel más alto que la pantalla se queda fijo cuando su final llega abajo
      it.panel.style.top = navH + Math.min(0, vh - navH - it.panel.offsetHeight) + "px";
    });
  }

  // Cuadrilátero alrededor del segmento a→b con medio grosor t (siempre en el mismo sentido de giro
  // para que la unión de trazos con la regla nonzero no deje huecos).
  function stroke(ax, ay, bx, by, t, ext) {
    const dx = bx - ax, dy = by - ay;
    const len = Math.hypot(dx, dy) || 1;
    const ux = dx / len, uy = dy / len;
    const nx = -uy * t, ny = ux * t;
    ax -= ux * ext; ay -= uy * ext; bx += ux * ext; by += uy * ext;
    let pts = [[ax + nx, ay + ny], [bx + nx, by + ny], [bx - nx, by - ny], [ax - nx, ay - ny]];
    let area = 0;
    for (let i = 0; i < 4; i++) {
      const p = pts[i], q = pts[(i + 1) % 4];
      area += p[0] * q[1] - q[0] * p[1];
    }
    if (area < 0) pts = pts.reverse();
    return "M" + pts.map(function (p) { return p[0].toFixed(1) + " " + p[1].toFixed(1); }).join(" L") + " Z";
  }

  // Segmentos de cada letra, en el orden en que se dibujan.
  function segments(shape, w, h) {
    if (shape === "k") {
      const x = w * 0.3, my = h * 0.52;
      return [[x, -h, x, 2 * h], [x, my, w * 0.92, h * 0.08], [x, my, w * 0.92, h * 0.96]];
    }
    const x0 = w * 0.1, x1 = w * 0.9, y0 = h * 0.14, y1 = h * 0.86;
    return [[x0, y0, x1, y0], [x1, y0, x0, y1], [x0, y1, x1, y1]];
  }

  // d: cuánto de la letra está dibujado (0–1, trazo a trazo); t: medio grosor del trazo.
  function shapePath(shape, w, h, t, d) {
    const segs = segments(shape, w, h);
    let path = "";
    segs.forEach(function (sg, i) {
      const f = clamp(d * segs.length - i);
      if (f <= 0) return;
      path += stroke(sg[0], sg[1], sg[0] + (sg[2] - sg[0]) * f, sg[1] + (sg[3] - sg[1]) * f, t, f >= 1 ? t : 0);
    });
    return path || "M0 0 Z";
  }

  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function ease(p) { return p * p * (3 - 2 * p); }

  function update() {
    queued = false;
    const span = (vh - navH) * 0.85;
    items.forEach(function (it) {
      const top = it.marker.getBoundingClientRect().top;
      const p = clamp((vh - top) / span);
      const panel = it.panel;
      if (p <= 0) {
        if (it.state !== "hidden") { panel.style.visibility = "hidden"; it.state = "hidden"; }
        return;
      }
      if (p >= 1 || top <= navH) {
        if (it.state !== "done") {
          panel.style.visibility = "";
          panel.style.clipPath = "";
          panel.style.transform = "";
          it.ink.style.opacity = "0";
          it.state = "done";
        }
        return;
      }
      // entrando: el panel se queda arriba y se descubre con la letra
      it.state = "entering";
      const w = panel.offsetWidth;
      const h = vh - navH;
      // 0–35 %: la letra se dibuja con un trazo fino; 35–85 %: el trazo se ensancha hasta llenar
      // la pantalla; 60–95 %: el color se desvanece y queda el contenido.
      const d = clamp(p / 0.35);
      const grow = ease(clamp((p - 0.35) / 0.5));
      const t = 3 + Math.pow(grow, 2) * Math.max(w, h) * 1.1;
      panel.style.visibility = "";
      panel.style.transform = "translateY(" + (navH - top).toFixed(1) + "px)";
      panel.style.clipPath = "path('" + shapePath(it.shape, w, h, t, d) + "')";
      it.ink.style.opacity = String(1 - clamp((p - 0.6) / 0.35));
    });
  }

  let queued = false;
  function queue() {
    if (!queued) {
      queued = true;
      requestAnimationFrame(update);
    }
  }

  measure();
  update();
  window.addEventListener("scroll", queue, { passive: true });
  window.addEventListener("resize", function () { measure(); queue(); });
  if ("ResizeObserver" in window) {
    const ro = new ResizeObserver(function () { measure(); queue(); });
    items.forEach(function (it) { ro.observe(it.panel); });
  }
})();
