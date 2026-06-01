(function () {
  const CALENDLY_BASE = "https://calendly.com/angelalarcon-aa/30min";
  const SIMPLE_ICONS_BASE = "https://cdn.jsdelivr.net/npm/simple-icons@11.14.0/icons";
  const MASK_SIZE = 1000;
  let particlesContainer = null;

  const modalHtml = `
    <div id="reservar-modal" class="fixed inset-0 z-50 hidden" role="dialog" aria-modal="true" aria-labelledby="reservar-title">
      <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" data-reservar-close></div>
      <div class="relative flex min-h-full items-center justify-center">
        <div class="w-full h-full overflow-hidden bg-white mx-auto">
          <div id="reservar-form-panel" class="relative p-8 sm:p-10">
            <button type="button" class="absolute right-4 top-4 rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600" data-reservar-close aria-label="Cerrar">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
            <p class="text-sm font-semibold text-indigo-600">Reserva gratuita · 30 min</p>
            <h2 id="reservar-title" class="mt-2 text-2xl font-extrabold tracking-tight text-slate-900">¿Cómo se llama tu negocio?</h2>
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
          <div id="reservar-loading-panel" class="relative hidden h-screen w-screen bg-indigo-950">
            <div id="reservar-particles" class="absolute inset-0"></div>
            <div id="reservar-loading-ui" class="pointer-events-none relative z-10 pb-10 flex h-full flex-col items-center justify-end gap-2 text-center">
              <div id="reservar-logo-wrap" class="mb-auto mt-auto hidden flex h-24 w-24 items-center justify-center">
                <img id="reservar-logo-img" alt="" class="max-h-full max-w-full object-contain opacity-90" />
              </div>
              <p id="reservar-company-label" class="text-sm font-medium text-indigo-200/90"></p>
              <p class="text-2xl font-bold tracking-wide text-white">
                Cargando<span class="reservar-dots">...</span>
              </p>
            </div>
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
      #reservar-form-panel { position: relative; }
      #reservar-particles canvas { display: block; vertical-align: bottom; }
      #reservar-loading-panel.reservar-has-mask #reservar-loading-ui { justify-content: flex-end; }
      #reservar-loading-panel.reservar-has-mask #reservar-logo-wrap { display: none !important; }
    `;
    document.head.appendChild(style);
  }

  function getModal() {
    return document.getElementById("reservar-modal");
  }

  function openModal() {
    const modal = getModal();
    const formPanel = document.getElementById("reservar-form-panel");
    const loadingPanel = document.getElementById("reservar-loading-panel");
    const error = document.getElementById("reservar-error");

    formPanel.classList.remove("hidden");
    loadingPanel.classList.add("hidden");
    loadingPanel.classList.remove("reservar-has-mask");
    document.getElementById("reservar-form").reset();
    error.classList.add("hidden");
    error.textContent = "";
    modal.classList.remove("hidden");
    document.body.classList.add("overflow-hidden");
    document.getElementById("reservar-company").focus();
  }

  function closeModal() {
    destroyParticles();
    resetLoadingVisuals();
    const modal = getModal();
    modal.classList.add("hidden");
    document.body.classList.remove("overflow-hidden");
  }

  function destroyParticles() {
    if (typeof tsParticles === "undefined") return;
    const existing = tsParticles.dom().find((c) => c.id === "reservar-particles");
    if (existing) existing.destroy();
    particlesContainer = null;
  }

  function resetLoadingVisuals() {
    const logoWrap = document.getElementById("reservar-logo-wrap");
    const logoImg = document.getElementById("reservar-logo-img");
    const loadingPanel = document.getElementById("reservar-loading-panel");
    logoWrap.classList.add("hidden");
    logoImg.removeAttribute("src");
    logoImg.alt = "";
    loadingPanel.classList.remove("reservar-has-mask");
  }

  function showFallbackLogo(imageUrl, alt) {
    const logoWrap = document.getElementById("reservar-logo-wrap");
    const logoImg = document.getElementById("reservar-logo-img");
    logoImg.alt = alt;
    logoImg.src = imageUrl;
    logoWrap.classList.remove("hidden");
  }

  async function searchClearbit(query) {
    const url = `https://autocomplete.clearbit.com/v1/companies/suggest?query=${encodeURIComponent(query)}`;
    const res = await fetch(url);
    if (!res.ok) return [];
    return res.json();
  }

  function matchClearbitResult(companyName, suggestions) {
    const normalized = companyName.toLowerCase().trim();
    return (
      suggestions.find((item) => item.name.toLowerCase() === normalized) ||
      suggestions.find(
        (item) =>
          item.name.toLowerCase().includes(normalized.slice(0, 4)) ||
          normalized.includes(item.name.toLowerCase().slice(0, 4))
      ) ||
      suggestions[0] ||
      null
    );
  }

  function slugCandidates(name, domain) {
    const slugs = new Set();
    if (domain) {
      const host = domain.replace(/^www\./, "").split(".");
      slugs.add(host[0]);
      if (host.length > 2) slugs.add(host[host.length - 2]);
    }

    const plain = name
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .trim();

    slugs.add(plain.replace(/[^a-z0-9]+/g, ""));
    slugs.add(plain.replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""));

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

  function loadImage(url) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.onload = () => resolve(img);
      img.onerror = () => reject(new Error("No se pudo cargar la imagen"));
      img.src = url;
    });
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

    return pathsFromSvgText(svgString) || pickMainPath(svgString);
  }

  async function buildParticleMask({ pathData, imageUrl }) {
    const canvas = document.createElement("canvas");
    canvas.width = MASK_SIZE;
    canvas.height = MASK_SIZE;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, MASK_SIZE, MASK_SIZE);
    ctx.fillStyle = "#000000";

    if (pathData?.path) {
      const scale = (MASK_SIZE * 0.78) / Math.max(pathData.width, pathData.height);
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
      const img = await loadImage(imageUrl);
      const scale = Math.min((MASK_SIZE * 0.78) / img.width, (MASK_SIZE * 0.78) / img.height);
      const w = img.width * scale;
      const h = img.height * scale;
      ctx.drawImage(img, (MASK_SIZE - w) / 2, (MASK_SIZE - h) / 2, w, h);
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

  async function resolveLogoPath(companyName) {
    const suggestions = await searchClearbit(companyName);
    const match = matchClearbitResult(companyName, suggestions);
    const searchName = match?.name || companyName.replace(/\.(com|es|net|org|io)$/i, "").trim() || companyName;
    const inputDomain = extractDomainFromInput(companyName);
    const domain = inputDomain || match?.domain || null;
    const slugs = slugCandidates(searchName, domain);
    const imageUrl = domain ? `https://icon.horse/icon/${domain}` : null;
    const svgPath = await fetchSimpleIconsPath(slugs);

    return { companyName: searchName, svgPath, imageUrl };
  }

  function startParticles(pathData, useMask) {
    destroyParticles();

    const config = {
      detectRetina: false,
      fpsLimit: 60,
      background: { color: "#1e1b4b" },
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
        scale: 0.5,
        type: "inline",
        data: {
          path: pathData.path,
          size: { width: pathData.width, height: pathData.height },
        },
      };
    }

    return tsParticles.load("reservar-particles", config).then((container) => {
      particlesContainer = container;
    });
  }

  function buildCalendlyUrl(companyName) {
    const params = new URLSearchParams();
    params.set("a1", companyName);
    return `${CALENDLY_BASE}?${params.toString()}`;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const companyInput = document.getElementById("reservar-company");
    const error = document.getElementById("reservar-error");
    const formPanel = document.getElementById("reservar-form-panel");
    const loadingPanel = document.getElementById("reservar-loading-panel");
    const companyLabel = document.getElementById("reservar-company-label");
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const companyName = companyInput.value.trim();

    if (!companyName) return;

    error.classList.add("hidden");
    submitBtn.disabled = true;

    formPanel.classList.add("hidden");
    loadingPanel.classList.remove("hidden");
    resetLoadingVisuals();
    companyLabel.textContent = companyName;

    await waitForLayout();
    await startParticles(null, false);

    let usedMask = false;
    try {
      const result = await resolveLogoPath(companyName);
      companyLabel.textContent = result.companyName;

      let particleMask = null;
      if (result.svgPath) {
        particleMask = await buildParticleMask({ pathData: result.svgPath });
      }
      if (!particleMask && result.imageUrl) {
        particleMask = await buildParticleMask({ imageUrl: result.imageUrl });
      }

      if (particleMask) {
        loadingPanel.classList.add("reservar-has-mask");
        await waitForLayout();
        await startParticles(particleMask, true);
        usedMask = true;
      } else if (result.imageUrl) {
        showFallbackLogo(result.imageUrl, result.companyName);
        await startParticles(null, false);
      }
    } catch {
      /* animación genérica */
    }

    const delay = usedMask ? 3500 : 2200;
    window.setTimeout(() => {
      window.open(buildCalendlyUrl(companyLabel.textContent || companyName), "_blank", "noopener,noreferrer");
      closeModal();
      submitBtn.disabled = false;
    }, delay);
  }

  function bindEvents() {
    document.querySelectorAll("[data-reservar-close]").forEach((el) => {
      el.addEventListener("click", closeModal);
    });

    document.getElementById("reservar-form").addEventListener("submit", handleSubmit);

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !getModal().classList.contains("hidden")) {
        closeModal();
      }
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
})();
