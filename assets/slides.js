// Carrusel de pantalla completa: el scroll no desplaza la página, solo pasa a la siguiente (o anterior)
// sección. Cada cambio se hace con una letra de ZEKER dibujada enorme sobre la pantalla:
// la Z (oscura, como en el logo) o la K (terracota, como en el logo), alternándose.
//  1. el trazo grueso de la letra barre la pantalla y tapa la sección actual;
//  2. con la pantalla cubierta se cambia de sección;
//  3. el trazo se retira siguiendo su propio recorrido y deja ver la nueva sección.
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
  const fill = document.createElementNS(NS, "rect");
  fill.setAttribute("x", "0");
  fill.setAttribute("y", "0");
  layer.appendChild(fill);
  const strokes = [0, 1].map(function () {
    const p = document.createElementNS(NS, "path");
    p.setAttribute("fill", "none");
    p.setAttribute("stroke-linejoin", "miter");
    p.setAttribute("stroke-miterlimit", "8");
    p.setAttribute("stroke-linecap", "butt");
    p.setAttribute("pathLength", "1");
    p.style.strokeDasharray = "1 1";
    layer.appendChild(p);
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
    fill.setAttribute("width", String(w));
    fill.setAttribute("height", String(h));
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
      return {
        d: ["M" + x + " 0 V" + h,
            "M" + arm(w, 0) + " L" + x + " " + my + " L" + arm(w, h)],
        width: sw,
      };
    }
    const sw = m * 0.28, top = sw / 2, bot = h - sw / 2;
    return {
      d: ["M0 " + top + " H" + w + " L0 " + bot + " H" + w, ""],
      width: sw,
    };
  }

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
    fill.setAttribute("fill", color);
    fill.style.opacity = "0";
    strokes.forEach(function (p, i) {
      p.setAttribute("d", L.d[i] || "M0 0");
      p.style.display = L.d[i] ? "" : "none";
      p.setAttribute("stroke", color);
      p.setAttribute("stroke-width", String(L.width));
      p.style.strokeDashoffset = "1";
    });
    layer.style.visibility = "visible";

    const from = slides[current];
    document.dispatchEvent(new CustomEvent("slide:leave", { detail: from }));

    // 1. la letra se dibuja sobre la sección actual y el relleno la acaba de tapar
    animate(760, function (t) {
      const e = easeInOut(Math.min(1, t / 0.8));
      strokes.forEach(function (p) { p.style.strokeDashoffset = String(1 - e); });
      fill.style.opacity = String(easeInOut(Math.max(0, (t - 0.72) / 0.28)));
    }).then(function () {
      // 2. pantalla cubierta: cambio de sección
      current = next;
      show(current);
      reveal(slides[current]);
      document.dispatchEvent(new CustomEvent("slide:enter", { detail: slides[current] }));
      // 3. el relleno se va (la letra vuelve a verse) y la letra se retira por su recorrido
      return animate(760, function (t) {
        fill.style.opacity = String(1 - easeInOut(Math.min(1, t / 0.3)));
        const e = easeInOut(Math.max(0, (t - 0.18) / 0.82));
        strokes.forEach(function (p) { p.style.strokeDashoffset = String(-e); });
      });
    }).then(function () {
      layer.style.visibility = "hidden";
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
  window.addEventListener("resize", measure);
  window.scrollTo(0, 0);
  show(0);
  reveal(slides[0]);
})();
