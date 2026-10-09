// Carrusel de pantalla completa: el scroll no desplaza la página, solo pasa a la siguiente (o anterior)
// sección. Cada cambio se hace con una letra de ZEKER dibujada enorme sobre la pantalla:
// la Z (oscura, como en el logo) o la K (terracota, como en el logo), alternándose.
//  1. el trazo grueso de la letra se dibuja de borde a borde;
//  2. la letra crece desde su centro hasta cubrir toda la pantalla;
//  3. con la pantalla cubierta se cambia de sección;
//  4. la letra se vuelve transparente y deja ver la nueva sección.
// Una sección más alta que la pantalla se recorre primero por dentro; al llegar a su final,
// el siguiente gesto cambia de sección.
(function () {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const root = document.documentElement;
  const nav = document.getElementById("nav-el");
  const hero = document.getElementById("hero-header");
  const slides = [hero].concat(Array.from(document.querySelectorAll(".panel"))).filter(Boolean);
  if (slides.length < 2) return;

  const COLORS = { z: "#42344A", k: "#C24F2C" };
  const NAMES = slides.map(function (s, i) {
    const h = s.querySelector("h1, h2");
    return h ? h.textContent.trim().replace(/\s+/g, " ") : "Sección " + (i + 1);
  });

  root.classList.add("slides-on");

  // ---------- capa de la letra ----------
  const NS = "http://www.w3.org/2000/svg";
  const layer = document.createElementNS(NS, "svg");
  layer.setAttribute("class", "zk-cover");
  layer.setAttribute("aria-hidden", "true");
  layer.setAttribute("preserveAspectRatio", "none");
  const group = document.createElementNS(NS, "g");
  layer.appendChild(group);
  const strokes = [0, 1].map(function () {
    const p = document.createElementNS(NS, "path");
    p.setAttribute("fill", "none");
    p.setAttribute("stroke-linejoin", "miter");
    p.setAttribute("stroke-miterlimit", "8");
    p.setAttribute("stroke-linecap", "butt");
    p.setAttribute("pathLength", "1");
    p.style.strokeDasharray = "1 1";
    group.appendChild(p);
    return p;
  });
  document.body.appendChild(layer);

  // ---------- puntos de navegación ----------
  const dots = document.createElement("nav");
  dots.className = "slide-dots";
  dots.setAttribute("aria-label", "Secciones");
  const dotButtons = slides.map(function (s, i) {
    const b = document.createElement("button");
    b.type = "button";
    b.setAttribute("aria-label", NAMES[i]);
    b.addEventListener("click", function () { go(i); });
    dots.appendChild(b);
    return b;
  });
  document.body.appendChild(dots);

  let w = 0, h = 0;
  function measure() {
    const navH = nav ? nav.offsetHeight : 0;
    root.style.setProperty("--nav-h", navH + "px");
    w = window.innerWidth;
    h = window.innerHeight - navH;
    layer.setAttribute("viewBox", "0 0 " + w + " " + h);
  }

  // La letra llega a los bordes de la pantalla en cualquier tamaño:
  //  Z: barra pegada arriba de lado a lado, diagonal de la esquina superior derecha a la inferior
  //     izquierda y barra pegada abajo de lado a lado;
  //  K: asta pegada al borde izquierdo de arriba abajo y brazos que salen de su centro hasta las
  //     dos esquinas derechas.
  // Las puntas son rectas y las esquinas en ángulo, así que cada trazo termina justo en el borde.
  function letter(shape) {
    const m = Math.min(w, h);
    if (shape === "k") {
      const sw = m * 0.3, x = sw / 2, my = h / 2;
      // los brazos se alargan medio grosor más allá de la esquina para cubrirla del todo
      function arm(cx, cy) {
        const dx = cx - x, dy = cy - my, len = Math.hypot(dx, dy);
        return (cx + dx / len * sw * 0.6) + " " + (cy + dy / len * sw * 0.6);
      }
      const a1 = arm(w, 0).split(" ").map(Number), a2 = arm(w, h).split(" ").map(Number);
      return {
        d: ["M" + x + " 0 V" + h,
            "M" + a1.join(" ") + " L" + x + " " + my + " L" + a2.join(" ")],
        width: sw,
        segs: [[x, 0, x, h], [x, my, a1[0], a1[1]], [x, my, a2[0], a2[1]]],
        pivot: [x, my],
      };
    }
    const sw = m * 0.28, top = sw / 2, bot = h - sw / 2;
    return {
      d: ["M0 " + top + " H" + w + " L0 " + bot + " H" + w, ""],
      width: sw,
      segs: [[0, top, w, top], [w, top, 0, bot], [0, bot, w, bot]],
      pivot: [w / 2, h / 2],
    };
  }

  function segDist(px, py, s) {
    const dx = s[2] - s[0], dy = s[3] - s[1];
    const t = Math.max(0, Math.min(1, ((px - s[0]) * dx + (py - s[1]) * dy) / (dx * dx + dy * dy || 1)));
    return Math.hypot(px - s[0] - t * dx, py - s[1] - t * dy);
  }

  // Cuánto hay que escalar la letra (desde su pivote) para que cubra toda la pantalla:
  // búsqueda binaria comprobando una rejilla de puntos de la pantalla.
  function coverScale(L) {
    const half = L.width / 2, P = L.pivot;
    function covers(sc) {
      for (let i = 0; i <= 12; i++) {
        for (let j = 0; j <= 12; j++) {
          const qx = P[0] + (w * i / 12 - P[0]) / sc, qy = P[1] + (h * j / 12 - P[1]) / sc;
          let d = Infinity;
          L.segs.forEach(function (sg) { d = Math.min(d, segDist(qx, qy, sg)); });
          if (d > half) return false;
        }
      }
      return true;
    }
    let lo = 1, hi = 80;
    for (let k = 0; k < 24; k++) {
      const mid = (lo + hi) / 2;
      if (covers(mid)) hi = mid; else lo = mid;
    }
    return hi * 1.08;
  }

  // Si una sección no cabe en la pantalla, su contenido se reduce lo justo (como mucho al 75 %).
  function fit(slide) {
    const kids = Array.from(slide.children).filter(function (c) { return c.tagName !== "SCRIPT"; });
    kids.forEach(function (c) { c.style.zoom = ""; });
    const over = slide.scrollHeight - slide.clientHeight;
    if (over <= 1) return;
    const z = Math.max(0.75, (slide.clientHeight / slide.scrollHeight) * 0.985);
    kids.forEach(function (c) { c.style.zoom = String(z); });
  }
  function fitAll() { slides.forEach(fit); }

  // ---------- secciones ----------
  let current = 0;
  let busy = false;

  function reveal(slide) {
    const items = slide.querySelectorAll("[data-reveal]");
    items.forEach(function (el) { el.classList.remove("is-visible"); });
    slide.getBoundingClientRect();
    items.forEach(function (el, i) {
      el.style.transitionDelay = Math.min(i, 6) * 70 + "ms";
      el.classList.add("is-visible");
    });
  }

  function show(i) {
    slides.forEach(function (s, k) {
      const on = k === i;
      s.classList.toggle("is-active", on);
      s.setAttribute("aria-hidden", on ? "false" : "true");
      if (on) s.removeAttribute("inert"); else s.setAttribute("inert", "");
    });
    dotButtons.forEach(function (b, k) { b.setAttribute("aria-current", k === i ? "true" : "false"); });
    slides[i].scrollTop = 0;
  }

  function easeInOut(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }

  function animate(ms, step) {
    return new Promise(function (done) {
      const t0 = performance.now();
      function frame(now) {
        const t = Math.min(1, (now - t0) / ms);
        step(t);
        if (t < 1) requestAnimationFrame(frame); else done();
      }
      requestAnimationFrame(frame);
    });
  }

  function go(next) {
    if (busy || next === current || next < 0 || next >= slides.length) return;
    busy = true;
    // la letra de cada cambio depende del borde que se cruza: Z, K, Z, K…
    const edge = Math.max(next, current);
    const shape = edge % 2 === 1 ? "z" : "k";
    const color = COLORS[shape];
    const L = letter(shape);
    strokes.forEach(function (p, i) {
      p.setAttribute("d", L.d[i] || "M0 0");
      p.style.display = L.d[i] ? "" : "none";
      p.setAttribute("stroke", color);
      p.setAttribute("stroke-width", String(L.width));
      p.style.strokeDashoffset = "1";
    });
    const big = coverScale(L);
    const P = L.pivot;
    function scaleTo(sc) {
      group.setAttribute("transform", "translate(" + P[0] + " " + P[1] + ") scale(" + sc + ") translate(" + -P[0] + " " + -P[1] + ")");
    }
    scaleTo(1);
    layer.style.opacity = "1";
    layer.style.visibility = "visible";

    const from = slides[current];
    document.dispatchEvent(new CustomEvent("slide:leave", { detail: from }));

    // 1. la letra se dibuja sobre la sección actual
    animate(620, function (t) {
      strokes.forEach(function (p) { p.style.strokeDashoffset = String(1 - easeInOut(t)); });
    }).then(function () {
      // 2. la letra crece desde su centro hasta cubrir toda la pantalla
      return animate(520, function (t) {
        const e = t * t * t;  // empieza suave y acelera
        scaleTo(1 + (big - 1) * e);
      });
    }).then(function () {
      // 3. pantalla cubierta: cambio de sección
      current = next;
      show(current);
      reveal(slides[current]);
      document.dispatchEvent(new CustomEvent("slide:enter", { detail: slides[current] }));
      // 4. la letra se vuelve transparente y deja ver la nueva sección
      return animate(480, function (t) {
        layer.style.opacity = String(1 - easeInOut(t));
      });
    }).then(function () {
      layer.style.visibility = "hidden";
      group.removeAttribute("transform");
      // pequeña pausa para que la inercia del trackpad no encadene otro cambio
      setTimeout(function () { busy = false; }, 280);
    });
  }

  // ---------- gestos ----------
  function atEdge(dir) {
    const s = slides[current];
    if (dir > 0) return s.scrollTop + s.clientHeight >= s.scrollHeight - 2;
    return s.scrollTop <= 1;
  }

  function insideOverlay(target) {
    return target && target.closest && target.closest("#demo, #reservar-modal");
  }

  let wheelAcc = 0, wheelTimer = null;
  window.addEventListener("wheel", function (e) {
    if (insideOverlay(e.target) || root.querySelector("#demo:not([hidden])")) return;
    const dir = e.deltaY > 0 ? 1 : -1;
    if (busy) { e.preventDefault(); return; }
    if (!atEdge(dir)) { wheelAcc = 0; return; }   // primero se recorre la sección por dentro
    e.preventDefault();
    wheelAcc += e.deltaY;
    clearTimeout(wheelTimer);
    wheelTimer = setTimeout(function () { wheelAcc = 0; }, 180);
    if (Math.abs(wheelAcc) > 40) {
      wheelAcc = 0;
      go(current + dir);
    }
  }, { passive: false });

  let touchY = null, touchX = 0, touchEdgeDown = false, touchEdgeUp = false;
  window.addEventListener("touchstart", function (e) {
    if (insideOverlay(e.target)) { touchY = null; return; }
    touchY = e.touches[0].clientY;
    touchX = e.touches[0].clientX;
    touchEdgeDown = atEdge(1);
    touchEdgeUp = atEdge(-1);
  }, { passive: true });
  window.addEventListener("touchmove", function (e) {
    if (touchY === null) return;
    const dy = touchY - e.touches[0].clientY;
    const dx = touchX - e.touches[0].clientX;
    if (Math.abs(dx) > Math.abs(dy)) return;  // gesto horizontal: sliders y carruseles internos
    // en el borde de la sección, el gesto no hace rebotar la página: cambia de sección
    if (dy < 0 && current === 0) return;  // portada: tirar hacia abajo recarga, como siempre
    if ((dy > 0 && touchEdgeDown) || (dy < 0 && touchEdgeUp) || busy) e.preventDefault();
  }, { passive: false });
  window.addEventListener("touchend", function (e) {
    if (touchY === null) return;
    const dy = touchY - e.changedTouches[0].clientY;
    const dx = touchX - e.changedTouches[0].clientX;
    touchY = null;
    if (Math.abs(dy) < 50 || Math.abs(dx) > Math.abs(dy)) return;
    if (dy > 0 && touchEdgeDown) go(current + 1);
    else if (dy < 0 && touchEdgeUp) go(current - 1);
  });

  window.addEventListener("keydown", function (e) {
    if (insideOverlay(document.activeElement) || /input|textarea|select/i.test(document.activeElement.tagName)) return;
    const key = e.key;
    let dir = 0;
    if (key === "ArrowDown" || key === "PageDown" || (key === " " && !e.shiftKey)) dir = 1;
    if (key === "ArrowUp" || key === "PageUp" || (key === " " && e.shiftKey)) dir = -1;
    if (key === "Home") { e.preventDefault(); go(0); return; }
    if (key === "End") { e.preventDefault(); go(slides.length - 1); return; }
    if (!dir) return;
    if (!atEdge(dir)) {  // primero se recorre la sección por dentro
      e.preventDefault();
      const s = slides[current];
      s.scrollBy({ top: dir * s.clientHeight * 0.8, behavior: "smooth" });
      return;
    }
    e.preventDefault();
    go(current + dir);
  });

  // un enlace a una sección (#id) lleva a su diapositiva
  document.addEventListener("click", function (e) {
    const a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a || a.getAttribute("href").length < 2) return;
    const t = document.querySelector(a.getAttribute("href"));
    const i = t ? slides.findIndex(function (s) { return s.contains(t); }) : -1;
    if (i >= 0) { e.preventDefault(); go(i); }
  });

  measure();
  fitAll();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitAll);
  window.addEventListener("load", fitAll);
  window.addEventListener("resize", function () { measure(); fitAll(); });
  window.scrollTo(0, 0);
  show(0);
  reveal(slides[0]);
})();
