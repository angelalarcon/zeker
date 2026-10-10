(function () {
  const TIMEZONE = "Atlantic/Canary";
  const SIMPLE_ICONS_BASE = "https://cdn.jsdelivr.net/npm/simple-icons@11.14.0/icons";
  const MASK_SIZE = 1000;
  let particlesContainer = null;
  let booking = { company: "", slots: [], day: null, start: null };

  const modalHtml = `
    <div id="reservar-modal" class="fixed inset-0 z-50 hidden" role="dialog" aria-modal="true" aria-labelledby="reservar-title">
      <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" data-reservar-close></div>
      <div class="relative flex min-h-full items-center justify-center p-4">
        <div id="reservar-form-panel" class="relative p-8 sm:p-10 max-w-2xl w-full mx-auto bg-paper rounded-[1.75rem] shadow-[0_0_0_2px_#42344A,8px_8px_0_#42344A]">
          <button type="button" class="absolute right-4 top-4 rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600" data-reservar-close aria-label="Cerrar">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
          <p class="eyebrow">Reserva gratuita · 30 min</p>
          <h2 id="reservar-title" class="poster-title mt-3 text-3xl">¿Cómo se llama tu negocio?</h2>
          <p class="mt-2 text-slate-600">Buscamos tu marca en internet para personalizar la experiencia.</p>
          <form id="reservar-form" class="mt-6">
            <label for="reservar-company" class="sr-only">Nombre de la empresa o negocio</label>
            <input
              id="reservar-company"
              name="company"
              type="text"
              required
              autocomplete="organization"
              placeholder="Ej. Panadería La Esquina"
              class="w-full rounded-2xl border border-slate-200 px-4 py-3.5 text-base text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
            />
            <p id="reservar-error" class="mt-2 hidden text-sm text-red-600"></p>
            <button
              type="submit"
              class="mt-4 w-full rounded-full bg-indigo-600 px-6 py-3.5 text-base font-semibold text-white shadow-sm transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Continuar
            </button>
          </form>
        </div>
      </div>
    </div>

    <div id="reservar-booking" class="fixed inset-0 z-50 hidden" role="dialog" aria-modal="true" aria-labelledby="reservar-booking-title">
      <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" data-booking-close></div>
      <div class="relative flex min-h-full items-center justify-center p-4">
        <div class="relative p-6 sm:p-10 max-w-2xl w-full mx-auto bg-paper rounded-[1.75rem] shadow-[0_0_0_2px_#42344A,8px_8px_0_#42344A]">
          <button type="button" class="absolute right-4 top-4 rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600" data-booking-close aria-label="Cerrar">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>
          <div id="booking-step-pick">
            <p class="eyebrow">Reserva gratuita · 30 min</p>
            <h2 id="reservar-booking-title" class="poster-title mt-3 text-3xl">Elige día y hora</h2>
            <p class="mt-2 text-slate-600">Horario de Canarias. Te confirmamos la reunión por email.</p>
            <p id="booking-loading" class="mt-6 text-slate-600">Buscando huecos libres<span class="reservar-dots">...</span></p>
            <div id="booking-days" class="mt-6 flex gap-2 overflow-x-auto pb-2" role="listbox" aria-label="Día"></div>
            <div id="booking-times" class="mt-4 grid grid-cols-3 gap-2 sm:grid-cols-4" role="listbox" aria-label="Hora"></div>
            <form id="booking-form" class="mt-6 hidden space-y-3">
              <p id="booking-chosen" class="font-display text-sm font-bold uppercase tracking-[0.12em] text-indigo-600"></p>
              <input name="name" type="text" required autocomplete="name" placeholder="Tu nombre" aria-label="Tu nombre"
                class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-base text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20" />
              <input name="email" type="email" required autocomplete="email" placeholder="Tu email" aria-label="Tu email"
                class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-base text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20" />
              <textarea name="message" rows="2" placeholder="¿Algo que debamos saber? (opcional)" aria-label="Mensaje"
                class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-base text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"></textarea>
              <input name="website" type="text" tabindex="-1" autocomplete="off" class="hidden" aria-hidden="true" />
              <button type="submit" class="w-full rounded-full bg-indigo-600 px-6 py-3.5 text-base font-semibold text-white shadow-sm transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60">
                Solicitar reunión
              </button>
            </form>
            <p id="booking-error" class="mt-3 hidden text-sm text-red-600"></p>
          </div>
          <div id="booking-step-done" class="hidden text-center">
            <p class="eyebrow">Solicitud enviada</p>
            <h2 class="poster-title mt-3 text-3xl">¡Gracias!</h2>
            <p id="booking-done-text" class="mt-3 text-slate-700"></p>
            <button type="button" class="btn btn-primary mt-7" data-booking-close>Cerrar</button>
          </div>
        </div>
      </div>
    </div>
  `;

  function injectModal() {
    if (document.getElementById("reservar-modal")) return;
    document.body.insertAdjacentHTML("beforeend", modalHtml);

    const style = document.createElement("style");
    style.textContent = `
      @keyframes reservar-dots { 0%, 20% { opacity: 0; } 50% { opacity: 1; } 100% { opacity: 0; } }
      .reservar-dots { animation: reservar-dots 1.4s infinite; }
      #hero-logo-particles canvas { display: block; }
      .booking-chip { flex-shrink: 0; border-radius: 1rem; padding: .6rem .9rem; text-align: center; box-shadow: inset 0 0 0 2px #E5D8C6; background: #fff; color: #42344A; transition: background-color .2s, box-shadow .2s; }
      .booking-chip:hover { box-shadow: inset 0 0 0 2px #C24F2C; }
      .booking-chip[aria-selected="true"] { background: #C24F2C; color: #FBF4E4; box-shadow: none; }
    `;
    document.head.appendChild(style);
  }

  function getModal() {
    return document.getElementById("reservar-modal");
  }

  function openModal() {
    const modal = getModal();
    const error = document.getElementById("reservar-error");
    document.getElementById("reservar-form").reset();
    error.classList.add("hidden");
    error.textContent = "";
    modal.classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
    document.getElementById("reservar-company").focus();
  }

  function closeModal() {
    const modal = getModal();
    modal.classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
  }

  function destroyParticles() {
    if (typeof tsParticles === "undefined") return;
    const existing = tsParticles.dom().find((c) => c.id === "hero-logo-particles");
    if (existing) existing.destroy();
    particlesContainer = null;
  }

  function animateHeroOpen() {
    window.scrollTo(0, 0);

    const navEl      = document.getElementById("nav-el");
    const navLogo    = document.getElementById("nav-logo");
    const navItems   = document.getElementById("nav-items");
    const heroAbove  = document.getElementById("hero-above");
    const lineTop    = document.getElementById("hero-line-top");
    const slot       = document.getElementById("hero-logo-slot");
    const lineBottom = document.getElementById("hero-line-bottom");
    const heroBelow  = document.getElementById("hero-below");
    const headerEl   = document.getElementById("hero-header");
    const mainEl     = document.getElementById("main-content");
    const fieldCanvas = document.getElementById("field");
    const bgOverlay  = document.getElementById("bg-overlay");

    if (!lineTop || !lineBottom || !slot) return;


    // Reset text opacity from previous animation
    const logoText = document.getElementById("hero-logo-text");
    if (logoText) logoText.style.opacity = "";

    const navHeight = navEl ? navEl.offsetHeight : 64;
    const ease = "0.8s cubic-bezier(0.4,0,0.2,1)";

    document.body.style.overflow = "hidden";
    document.body.style.transition = `background-color ${ease}`;
    document.body.style.backgroundColor = "#33283B";

    if (fieldCanvas) { fieldCanvas.style.transition = `opacity ${ease}`; fieldCanvas.style.opacity = "0"; }
    if (bgOverlay)   { bgOverlay.style.transition   = `opacity ${ease}`; bgOverlay.style.opacity   = "0"; }

    if (navEl)    { navEl.style.transition = `background-color ${ease}, border-color ${ease}`; navEl.style.backgroundColor = "transparent"; navEl.style.borderColor = "transparent"; }
    if (navLogo)  { navLogo.style.transition = `color ${ease}`;       navLogo.style.color = "white"; }
    if (navItems) { navItems.style.transition = "opacity 0.4s ease";  navItems.style.opacity = "0"; navItems.style.pointerEvents = "none"; }

    if (headerEl) { headerEl.style.transition = `padding-top ${ease}, padding-bottom ${ease}`; headerEl.style.paddingTop = "0"; headerEl.style.paddingBottom = "0"; }

    if (heroAbove) heroAbove.style.transform = "translateY(-100vh)";
    lineTop.style.transform = "translateY(-100vh)";

    // Fix slot to viewport so it's always centered regardless of document flow
    slot.style.backgroundColor = "#33283B";
    slot.style.position   = "fixed";
    slot.style.top        = `${navHeight}px`;
    slot.style.left       = "0";
    slot.style.right      = "0";
    slot.style.zIndex     = "20";
    slot.style.borderRadius = "0";
    slot.style.height     = "0";
    // Let the position change settle before expanding
    requestAnimationFrame(() => {
      slot.style.height = `calc(100vh - ${navHeight}px)`;
    });

    lineBottom.style.transform = "translateY(100vh)";
    if (heroBelow) heroBelow.style.transform = "translateY(100vh)";
    if (mainEl)    mainEl.style.transform    = "translateY(100vh)";
  }

  function animateHeroClose() {
    const navEl      = document.getElementById("nav-el");
    const navLogo    = document.getElementById("nav-logo");
    const navItems   = document.getElementById("nav-items");
    const heroAbove  = document.getElementById("hero-above");
    const lineTop    = document.getElementById("hero-line-top");
    const slot       = document.getElementById("hero-logo-slot");
    const lineBottom = document.getElementById("hero-line-bottom");
    const heroBelow  = document.getElementById("hero-below");
    const headerEl   = document.getElementById("hero-header");
    const mainEl     = document.getElementById("main-content");
    const fieldCanvas = document.getElementById("field");
    const bgOverlay  = document.getElementById("bg-overlay");

    // Hide text and clear overflow immediately
    const logoText = document.getElementById("hero-logo-text");
    if (logoText) logoText.style.opacity = "0";
    document.body.style.overflow = "";
    document.body.classList.remove("overflow-hidden");

    document.body.style.backgroundColor = "";

    if (fieldCanvas) fieldCanvas.style.opacity = "";
    if (bgOverlay)   bgOverlay.style.opacity   = "";

    if (navEl)    { navEl.style.backgroundColor = ""; navEl.style.borderColor = ""; }
    if (navLogo)  navLogo.style.color = "";
    if (navItems) { navItems.style.opacity = ""; navItems.style.pointerEvents = ""; }

    if (headerEl) { headerEl.style.paddingTop = ""; headerEl.style.paddingBottom = ""; }

    if (heroAbove) heroAbove.style.transform = "";
    lineTop.style.transform    = "";
    lineBottom.style.transform = "";
    if (heroBelow) heroBelow.style.transform = "";
    if (mainEl)    mainEl.style.transform    = "";

    // Collapse slot then restore in-flow positioning
    slot.style.height = "0";
    setTimeout(() => {
      slot.style.position        = "relative";
      slot.style.backgroundColor = "";
      slot.style.top          = "";
      slot.style.left         = "";
      slot.style.right        = "";
      slot.style.zIndex       = "";
      slot.style.borderRadius = "";
      if (logoText) logoText.style.opacity = "0"; // keep hidden while slot is collapsed
    }, 850);
  }

  async function searchClearbit(query) {
    const url = `https://autocomplete.clearbit.com/v1/companies/suggest?query=${encodeURIComponent(query)}`;
    const res = await fetch(url);
    if (!res.ok) return [];
    return res.json();
  }

  function matchClearbitResult(companyName, suggestions) {
    const normalized = companyName.toLowerCase().trim();
    const firstWord = normalized.split(/\s+/)[0];
    return (
      suggestions.find((item) => item.name.toLowerCase() === normalized) ||
      suggestions.find((item) => item.name.toLowerCase().includes(firstWord) || firstWord.includes(item.name.toLowerCase().split(/\s+/)[0])) ||
      null
    );
  }

  function slugCandidates(name, domain) {
    const slugs = new Set();

    const plain = name
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .trim();

    // First word of the name is the most likely Simple Icons slug (e.g. "Santander" from "Santander Bank")
    const firstWord = plain.split(/\s+/)[0].replace(/[^a-z0-9]/g, "");
    if (firstWord.length > 1) slugs.add(firstWord);

    slugs.add(plain.replace(/[^a-z0-9]+/g, ""));
    slugs.add(plain.replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""));

    if (domain) {
      const host = domain.replace(/^www\./, "").split(".");
      slugs.add(host[0]);
      if (host.length > 2) slugs.add(host[host.length - 2]);
    }

    return [...slugs].filter((slug) => slug && slug.length > 1);
  }

  function pathsFromSvgText(svgText) {
    const doc = new DOMParser().parseFromString(svgText, "image/svg+xml");
    const paths = [...doc.querySelectorAll("path")]
      .map((pathEl) => pathEl.getAttribute("d"))
      .filter(Boolean);

    if (!paths.length) return null;

    const svg = doc.querySelector("svg");
    const viewBox = svg?.getAttribute("viewBox")?.split(/\s+/).map(Number);
    let width = parseFloat(svg?.getAttribute("width")) || 24;
    let height = parseFloat(svg?.getAttribute("height")) || 24;

    if (viewBox?.length === 4) {
      width = viewBox[2];
      height = viewBox[3];
    }

    return { path: paths.join(" "), width, height };
  }

  async function fetchSimpleIconsPath(slugs) {
    for (const slug of slugs) {
      try {
        const res = await fetch(`${SIMPLE_ICONS_BASE}/${slug}.svg`);
        if (!res.ok) continue;
        const pathData = pathsFromSvgText(await res.text());
        if (pathData) return pathData;
      } catch {
        /* siguiente slug */
      }
    }
    return null;
  }

  async function fetchImageAsBlob(url) {
    try {
      const res = await fetch(url);
      if (res.ok) return await res.blob();
    } catch { /* ignore */ }
    return null;
  }

  async function loadImage(url) {
    const blob = await fetchImageAsBlob(url);
    if (blob) {
      const objectUrl = URL.createObjectURL(blob);
      return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => { URL.revokeObjectURL(objectUrl); resolve(img); };
        img.onerror = () => { URL.revokeObjectURL(objectUrl); reject(new Error("img load failed")); };
        img.src = objectUrl;
      });
    }
    throw new Error("No se pudo cargar la imagen");
  }

  function toSilhouette(imageData) {
    const { data, width, height } = imageData;
    const out = new ImageData(width, height);

    for (let i = 0; i < data.length; i += 4) {
      const r = data[i];
      const g = data[i + 1];
      const b = data[i + 2];
      const a = data[i + 3];
      const max = Math.max(r, g, b);
      const min = Math.min(r, g, b);
      const isBackground = a < 50 || (max > 232 && max - min < 40);
      const value = isBackground ? 255 : 0;
      out.data[i] = value;
      out.data[i + 1] = value;
      out.data[i + 2] = value;
      out.data[i + 3] = 255;
    }

    return out;
  }

  function traceSilhouette(imageData) {
    const svgString = ImageTracer.imagedataToSVG(imageData, {
      ltres: 0.5,
      qtres: 0.5,
      pathomit: 6,
      colorsampling: 0,
      numberofcolors: 2,
      mincolorratio: 0,
      colorquantcycles: 1,
      blurradius: 0,
      blurdelta: 20,
      scale: 1,
      simplifytolerance: 0.35,
      roundcoords: 1,
      viewbox: true,
      linefilter: true,
    });

    // Keep only dark-colored paths (the logo) — discard light/white paths (the background rectangle)
    const doc = new DOMParser().parseFromString(svgString, "image/svg+xml");
    const svg = doc.querySelector("svg");
    const viewBox = svg?.getAttribute("viewBox")?.split(/\s+/).map(Number);
    const width = viewBox?.[2] || MASK_SIZE;
    const height = viewBox?.[3] || MASK_SIZE;

    const darkPaths = [...doc.querySelectorAll("path")].filter((p) => {
      const style = p.getAttribute("style") || "";
      const fill = p.getAttribute("fill") || "";
      const colorStr = (style.match(/fill\s*:\s*([^;]+)/)?.[1] || fill).trim();
      if (!colorStr) return true;
      // rgb(r,g,b) format
      const rgb = colorStr.match(/rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)/i);
      if (rgb) return (Number(rgb[1]) + Number(rgb[2]) + Number(rgb[3])) / 3 < 128;
      // #rrggbb format
      const hex = colorStr.replace("#", "");
      if (hex.length === 6) {
        const r = parseInt(hex.slice(0, 2), 16);
        const g = parseInt(hex.slice(2, 4), 16);
        const b = parseInt(hex.slice(4, 6), 16);
        return (r + g + b) / 3 < 128;
      }
      return true;
    }).map((p) => p.getAttribute("d")).filter(Boolean);

    if (!darkPaths.length) return pickMainPath(svgString);
    return { path: darkPaths.join(" "), width, height };
  }

  function drawInitials(ctx, companyName) {
    const words = companyName.trim().split(/\s+/);
    const initials = words.map((w) => w[0]).join("").toUpperCase().slice(0, 2);
    const fontSize = initials.length === 1 ? MASK_SIZE * 0.54 : MASK_SIZE * 0.42;
    ctx.font = `bold ${fontSize}px Arial, sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(initials, MASK_SIZE / 2, MASK_SIZE / 2);
  }

  async function buildParticleMask({ pathData, imageUrl, companyName }) {
    const canvas = document.createElement("canvas");
    canvas.width = MASK_SIZE;
    canvas.height = MASK_SIZE;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, MASK_SIZE, MASK_SIZE);
    ctx.fillStyle = "#000000";

    if (pathData?.path) {
      const scale = (MASK_SIZE * 0.52) / Math.max(pathData.width, pathData.height);
      const w = pathData.width * scale;
      const h = pathData.height * scale;
      ctx.translate((MASK_SIZE - w) / 2, (MASK_SIZE - h) / 2);
      ctx.scale(scale, scale);
      try {
        ctx.fill(new Path2D(pathData.path));
      } catch {
        return null;
      }
    } else if (imageUrl) {
      try {
        const img = await loadImage(imageUrl);
        const scale = Math.min((MASK_SIZE * 0.52) / img.width, (MASK_SIZE * 0.52) / img.height);
        const w = img.width * scale;
        const h = img.height * scale;
        ctx.drawImage(img, (MASK_SIZE - w) / 2, (MASK_SIZE - h) / 2, w, h);
      } catch {
        // Image failed (e.g. CORS on file://) — fall through to initials
        ctx.fillRect(0, 0, MASK_SIZE, MASK_SIZE); // reset
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, MASK_SIZE, MASK_SIZE);
        ctx.fillStyle = "#000000";
        if (companyName) drawInitials(ctx, companyName);
        else return null;
      }
    } else if (companyName) {
      drawInitials(ctx, companyName);
    } else {
      return null;
    }

    const silhouette = toSilhouette(ctx.getImageData(0, 0, MASK_SIZE, MASK_SIZE));
    const traced = traceSilhouette(silhouette);
    if (!traced?.path) return null;

    return {
      path: traced.path,
      width: MASK_SIZE,
      height: MASK_SIZE,
    };
  }

  function waitForLayout() {
    return new Promise((resolve) => {
      requestAnimationFrame(() => requestAnimationFrame(resolve));
    });
  }

  function pickMainPath(svgText) {
    const doc = new DOMParser().parseFromString(svgText, "image/svg+xml");
    const paths = [...doc.querySelectorAll("path")].filter((p) => p.getAttribute("d"));
    if (!paths.length) return null;

    const ranked = paths
      .map((pathEl) => {
        const d = pathEl.getAttribute("d");
        const moveCount = (d.match(/M/gi) || []).length;
        return { d, score: d.length / Math.max(moveCount, 1) };
      })
      .sort((a, b) => b.score - a.score);

    const svg = doc.querySelector("svg");
    const viewBox = svg?.getAttribute("viewBox")?.split(/\s+/).map(Number);
    let width = parseFloat(svg?.getAttribute("width")) || MASK_SIZE;
    let height = parseFloat(svg?.getAttribute("height")) || MASK_SIZE;

    if (viewBox?.length === 4) {
      width = viewBox[2];
      height = viewBox[3];
    }

    return { path: ranked[0].d, width, height };
  }

  function extractDomainFromInput(name) {
    const trimmed = name.trim().toLowerCase().replace(/^https?:\/\//, "").replace(/^www\./, "");
    if (/^[a-z0-9][a-z0-9.-]*\.[a-z]{2,}$/i.test(trimmed)) {
      return trimmed.split("/")[0];
    }
    return null;
  }

  async function resolveBestLogoUrl(domain) {
    if (!domain) return null;
    // DuckDuckGo sends Access-Control-Allow-Origin: * — works from file:// without a proxy
    return `https://icons.duckduckgo.com/ip3/${domain}.ico`;
  }

  async function resolveLogoPath(companyName) {
    const suggestions = await searchClearbit(companyName);
    const match = matchClearbitResult(companyName, suggestions);
    const searchName = match?.name || companyName.replace(/\.(com|es|net|org|io)$/i, "").trim() || companyName;
    const inputDomain = extractDomainFromInput(companyName);
    const domain = inputDomain || match?.domain || null;

    const [svgPath, imageUrl] = await Promise.all([
      fetchSimpleIconsPath(slugCandidates(searchName, domain)),
      resolveBestLogoUrl(domain),
    ]);

    return { companyName: searchName, svgPath, imageUrl };
  }

  function buildParticleConfig(pathData, useMask) {
    const config = {
      detectRetina: false,
      fpsLimit: 60,
      // No background fill — the body/slot background provides the dark color
      // so the canvas stays transparent and crossfades work correctly
      interactivity: {
        detectsOn: "canvas",
        events: {
          onHover: { enable: true, mode: "bubble" },
          resize: true,
        },
        modes: {
          bubble: {
            color: "#818cf8",
            distance: 100,
            duration: 2,
            opacity: 1,
            size: 10,
            speed: 3,
          },
        },
      },
      particles: {
        color: { value: "#ffffff" },
        links: {
          blink: false,
          color: "#ffffff",
          consent: false,
          distance: 20,
          enable: true,
          opacity: 0.8,
          width: 1,
        },
        move: {
          attract: { enable: false, rotate: { x: 600, y: 1200 } },
          bounce: false,
          direction: "none",
          enable: true,
          outMode: "bounce",
          random: false,
          speed: 1,
          straight: false,
        },
        number: {
          density: { enable: false, area: 2000 },
          limit: 0,
          value: useMask ? 300 : 180,
        },
        opacity: {
          animation: { enable: true, minimumValue: 0.05, speed: 3, sync: false },
          random: false,
          value: 1,
        },
        shape: { type: "circle" },
        size: {
          animation: { enable: false, minimumValue: 0.1, speed: 40, sync: false },
          random: true,
          value: useMask ? 3 : 2.5,
        },
      },
    };

    if (useMask && pathData?.path) {
      config.polygon = {
        draw: { enable: true, lineColor: "#818cf8", lineWidth: 1 },
        move: { radius: 10 },
        inlineArrangement: "equidistant",
        scale: window.innerWidth < 640 ? 0.5 : 1.0,
        type: "inline",
        data: {
          path: pathData.path,
          size: { width: pathData.width, height: pathData.height },
        },
      };
    }

    return config;
  }

  async function crossfadeToMask(pathData) {
    const heroEl = document.getElementById("hero-logo-particles");
    const oldCanvas = heroEl ? heroEl.querySelector("canvas") : null;

    // Step 1: fade out the floating particles canvas
    if (oldCanvas) {
      oldCanvas.style.transition = "opacity 0.6s ease";
      oldCanvas.style.opacity = "0";
      await new Promise((r) => setTimeout(r, 600));
    }

    // Step 2: destroy old instance, launch logo particles
    destroyParticles();
    const config = buildParticleConfig(pathData, true);
    const container = await tsParticles.load("hero-logo-particles", config);
    particlesContainer = container;

    // Step 3: fade the new canvas in
    const newCanvas = heroEl ? heroEl.querySelector("canvas") : null;
    if (newCanvas) {
      newCanvas.style.opacity = "0";
      newCanvas.style.transition = "opacity 1.2s ease";
      requestAnimationFrame(() => requestAnimationFrame(() => {
        newCanvas.style.opacity = "1";
      }));
    }
  }

  function startParticles(pathData, useMask) {
    // When switching to the logo mask, use a smooth crossfade instead of a hard cut
    if (useMask && pathData && particlesContainer) {
      return crossfadeToMask(pathData);
    }

    destroyParticles();
    const config = buildParticleConfig(pathData, useMask);
    return tsParticles.load("hero-logo-particles", config).then((container) => {
      particlesContainer = container;
    });
  }

  const dayFormat = new Intl.DateTimeFormat("es-ES", { timeZone: TIMEZONE, weekday: "short", day: "numeric", month: "short" });
  const dayKeyFormat = new Intl.DateTimeFormat("en-CA", { timeZone: TIMEZONE, year: "numeric", month: "2-digit", day: "2-digit" });
  const timeFormat = new Intl.DateTimeFormat("es-ES", { timeZone: TIMEZONE, hour: "2-digit", minute: "2-digit" });
  const longFormat = new Intl.DateTimeFormat("es-ES", { timeZone: TIMEZONE, weekday: "long", day: "numeric", month: "long", hour: "2-digit", minute: "2-digit" });

  async function fetchSlots() {
    const res = await fetch("/api/slots", { headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error("slots " + res.status);
    return (await res.json()).slots || [];
  }

  function showBookingError(message) {
    const el = document.getElementById("booking-error");
    el.textContent = message;
    el.classList.toggle("hidden", !message);
  }

  function renderDays() {
    const days = document.getElementById("booking-days");
    const keys = [...new Set(booking.slots.map((iso) => dayKeyFormat.format(new Date(iso))))];
    days.innerHTML = "";
    keys.forEach((key) => {
      const first = booking.slots.find((iso) => dayKeyFormat.format(new Date(iso)) === key);
      const [weekday, ...rest] = dayFormat.format(new Date(first)).replace(",", "").split(" ");
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "booking-chip";
      chip.setAttribute("role", "option");
      chip.setAttribute("aria-selected", String(key === booking.day));
      chip.innerHTML = `<span class="block text-xs uppercase tracking-[0.12em]"></span><span class="block font-semibold"></span>`;
      chip.children[0].textContent = weekday;
      chip.children[1].textContent = rest.join(" ");
      chip.addEventListener("click", () => { booking.day = key; booking.start = null; renderDays(); renderTimes(); });
      days.appendChild(chip);
    });
  }

  function renderTimes() {
    const times = document.getElementById("booking-times");
    const form = document.getElementById("booking-form");
    times.innerHTML = "";
    booking.slots
      .filter((iso) => dayKeyFormat.format(new Date(iso)) === booking.day)
      .forEach((iso) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "booking-chip font-semibold";
        btn.setAttribute("role", "option");
        btn.setAttribute("aria-selected", String(iso === booking.start));
        btn.textContent = timeFormat.format(new Date(iso));
        btn.addEventListener("click", () => {
          booking.start = iso;
          renderTimes();
          form.querySelector('[name="name"]').focus();
        });
        times.appendChild(btn);
      });
    form.classList.toggle("hidden", !booking.start);
    if (booking.start) document.getElementById("booking-chosen").textContent = longFormat.format(new Date(booking.start)) + " · hora canaria";
  }

  async function openBooking(company, slotsPromise) {
    booking = { company, slots: [], day: null, start: null };
    const modal = document.getElementById("reservar-booking");
    document.getElementById("booking-step-pick").classList.remove("hidden");
    document.getElementById("booking-step-done").classList.add("hidden");
    document.getElementById("booking-form").reset();
    document.getElementById("booking-form").classList.add("hidden");
    document.getElementById("booking-days").innerHTML = "";
    document.getElementById("booking-times").innerHTML = "";
    document.getElementById("booking-loading").classList.remove("hidden");
    showBookingError("");
    modal.classList.remove("hidden");
    document.body.classList.add("overflow-hidden");

    try {
      booking.slots = await slotsPromise;
    } catch (e) {
      console.error("Error loading slots:", e);
      booking.slots = [];
    }
    document.getElementById("booking-loading").classList.add("hidden");
    if (!booking.slots.length) {
      showBookingError("Ahora mismo no hay huecos disponibles. Escríbenos por WhatsApp y lo cuadramos.");
      return;
    }
    booking.day = dayKeyFormat.format(new Date(booking.slots[0]));
    renderDays();
    renderTimes();
  }

  function closeBooking() {
    document.getElementById("reservar-booking").classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
    document.body.style.overflow = "";
  }

  async function handleBookingSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const data = Object.fromEntries(new FormData(form));
    showBookingError("");
    submitBtn.disabled = true;

    try {
      const res = await fetch("/api/request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...data, company: booking.company, start: booking.start }),
      });
      const result = await res.json().catch(() => ({}));
      if (!res.ok) {
        showBookingError(result.error || "No hemos podido enviar la solicitud. Inténtalo de nuevo.");
        if (res.status === 409) {
          booking.slots = booking.slots.filter((iso) => iso !== booking.start);
          booking.start = null;
          renderTimes();
        }
        return;
      }
      document.getElementById("booking-done-text").textContent =
        `Hemos recibido tu solicitud para el ${longFormat.format(new Date(booking.start))} (hora canaria). ` +
        `Te llegará un email a ${data.email} con el enlace de Google Meet en cuanto la confirmemos.`;
      document.getElementById("booking-step-pick").classList.add("hidden");
      document.getElementById("booking-step-done").classList.remove("hidden");
    } catch (e) {
      console.error(e);
      showBookingError("No hemos podido enviar la solicitud. Revisa tu conexión e inténtalo de nuevo.");
    } finally {
      submitBtn.disabled = false;
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const companyInput = document.getElementById("reservar-company");
    const error = document.getElementById("reservar-error");
    const companyLabel = document.getElementById("reservar-company-label");
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const companyName = companyInput.value.trim();

    if (!companyName) return;

    error.classList.add("hidden");
    submitBtn.disabled = true;
    const slotsPromise = fetchSlots();

    // Close the form modal and open the hero animation
    closeModal();
    companyLabel.textContent = companyName;
    animateHeroOpen();

    // Wait for the hero open animation to finish before rendering particles
    await new Promise((resolve) => setTimeout(resolve, 850));
    await waitForLayout();
    await startParticles(null, false);

    let logoLoaded = false;
    let resolvedName = companyName;

    try {
      const result = await resolveLogoPath(companyName);
      resolvedName = result.companyName;
      companyLabel.textContent = resolvedName;

      const maskSource = result.svgPath
        ? { pathData: result.svgPath, companyName: resolvedName }
        : { imageUrl: result.imageUrl, companyName: resolvedName };

      try {
        const particleMask = await buildParticleMask(maskSource);
        if (particleMask) {
          await waitForLayout();
          await startParticles(particleMask, true);
          logoLoaded = true;
        }
      } catch (e) {
        console.warn("Error building particle mask:", e);
      }
    } catch (e) {
      console.error("Error resolving logo path:", e);
    }

    const delay = logoLoaded ? 5000 : 2000;
    await Promise.all([new Promise((resolve) => setTimeout(resolve, delay)), slotsPromise.catch(() => {})]);

    destroyParticles();
    animateHeroClose();
    submitBtn.disabled = false;
    setTimeout(() => openBooking(resolvedName, slotsPromise), 850);
  }

  function bindEvents() {
    document.querySelectorAll("[data-reservar-close]").forEach((el) => {
      el.addEventListener("click", closeModal);
    });

    document.querySelectorAll("[data-booking-close]").forEach((el) => {
      el.addEventListener("click", closeBooking);
    });

    document.getElementById("reservar-form").addEventListener("submit", handleSubmit);
    document.getElementById("booking-form").addEventListener("submit", handleBookingSubmit);

    document.addEventListener("keydown", (event) => {
      if (event.key !== "Escape") return;
      if (!getModal().classList.contains("hidden")) closeModal();
      if (!document.getElementById("reservar-booking").classList.contains("hidden")) closeBooking();
    });

    document.querySelectorAll(".js-reservar").forEach((trigger) => {
      trigger.addEventListener("click", (event) => {
        event.preventDefault();
        openModal();
      });
    });
  }

  injectModal();
  bindEvents();

  // Auto-open modal when arriving from another page with ?reservar=1
  if (new URLSearchParams(location.search).get("reservar") === "1") {
    // Wait for page to paint before opening
    requestAnimationFrame(() => openModal());
  }
})();
