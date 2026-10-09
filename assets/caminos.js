// "Dos caminos": al pulsar una tarjeta, se expande a pantalla completa y muestra la demostración.
// - nuevo: la rueda vuela desde la sección hasta la web del taller, que se construye por partes.
// - mejora: una web anticuada se transforma en una limpia con un barrido diagonal (la Z).
(function () {
  const demo = document.getElementById("demo");
  if (!demo) return;
  const title = document.getElementById("demo-title");
  const kicker = document.getElementById("demo-kicker");
  const wheelSrc = document.getElementById("wheel-src");
  const wheelFly = document.getElementById("wheel-fly");
  const slot = document.getElementById("wheel-slot");
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const texts = {
    nuevo: ["Desde cero", "Creamos tu web"],
    mejora: ["Ya tienes web", "Mejoramos la tuya"],
  };
  let openCard = null;
  let timers = [];

  function later(fn, ms) { timers.push(setTimeout(fn, reduce ? 0 : ms)); }
  function clearTimers() { timers.forEach(clearTimeout); timers = []; }

  function clipTo(rect) {
    demo.style.setProperty("--t", rect.top + "px");
    demo.style.setProperty("--l", rect.left + "px");
    demo.style.setProperty("--r", window.innerWidth - rect.right + "px");
    demo.style.setProperty("--b", window.innerHeight - rect.bottom + "px");
    demo.style.setProperty("--rad", "28px");
  }
  function clipFull() {
    ["--t", "--l", "--r", "--b", "--rad"].forEach(function (k) { demo.style.setProperty(k, "0px"); });
  }

  function flyWheel() {
    slot.innerHTML = "";
    const from = wheelSrc.getBoundingClientRect();
    const to = slot.getBoundingClientRect();
    if (reduce || !from.width || !to.width) {
      slot.innerHTML = '<img src="assets/illustrations/wheel.svg" alt="" />';
      return;
    }
    wheelFly.style.transition = "none";
    wheelFly.style.width = from.width + "px";
    wheelFly.style.opacity = "1";
    wheelFly.style.transform = "translate(" + from.left + "px," + from.top + "px) rotate(0deg)";
    wheelFly.getBoundingClientRect();
    wheelFly.style.transition = "transform 1.1s cubic-bezier(.5,0,.2,1)";
    const s = to.width / from.width;
    wheelFly.style.transform = "translate(" + to.left + "px," + to.top + "px) scale(" + s + ") rotate(540deg)";
    later(function () {
      slot.innerHTML = '<img src="assets/illustrations/wheel.svg" alt="Rueda de coche" />';
      wheelFly.style.opacity = "0";
    }, 1150);
  }

  function play(mode) {
    clearTimers();
    demo.classList.remove("is-built", "is-improved");
    if (mode === "nuevo") {
      later(function () { demo.classList.add("is-built"); }, 250);
      later(flyWheel, 700);
    } else {
      later(function () { demo.classList.add("is-improved"); }, 1400);
    }
  }

  function open(card) {
    const mode = card.dataset.demo;
    openCard = card;
    kicker.textContent = texts[mode][0];
    title.textContent = texts[mode][1];
    demo.dataset.mode = mode;
    clipTo(card.getBoundingClientRect());
    demo.style.transition = "none";
    demo.hidden = false;
    document.body.style.overflow = "hidden";
    demo.getBoundingClientRect();
    demo.style.transition = "";
    requestAnimationFrame(function () { clipFull(); });
    demo.querySelector("[data-demo-close]").focus({ preventScroll: true });
    later(function () { play(mode); }, 450);
  }

  function close() {
    if (demo.hidden) return;
    clearTimers();
    wheelFly.style.opacity = "0";
    if (openCard) clipTo(openCard.getBoundingClientRect());
    setTimeout(function () {
      demo.hidden = true;
      demo.classList.remove("is-built", "is-improved");
      slot.innerHTML = "";
      document.body.style.overflow = "";
      if (openCard) openCard.focus({ preventScroll: true });
      openCard = null;
    }, reduce ? 0 : 600);
  }

  document.querySelectorAll("[data-demo]").forEach(function (card) {
    card.addEventListener("click", function () { open(card); });
  });
  demo.querySelector("[data-demo-close]").addEventListener("click", close);
  demo.querySelector("[data-demo-replay]").addEventListener("click", function () { play(demo.dataset.mode); });
  demo.querySelectorAll(".js-reservar").forEach(function (a) { a.addEventListener("click", close); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
})();
