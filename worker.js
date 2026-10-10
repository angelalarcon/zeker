// Reservas con Google Calendar (sustituye a Calendly).
//
// Flujo:
//  1. GET  /api/slots              → huecos libres de tu calendario (L–V, mañanas, nunca después de las 15:00 hora canaria)
//  2. POST /api/request            → la persona pide un hueco; te llega un email con "Aprobar" / "Rechazar"
//  3. GET  /api/review?t=…         → página para revisar la solicitud (los enlaces del email llevan aquí)
//  4. POST /api/review             → al aprobar: evento en Calendar con Google Meet + email de confirmación a la persona
//
// No hay base de datos: cada solicitud viaja firmada (HMAC) dentro del enlace que recibes por email.
// Secretos (wrangler secret put …): GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN, BOOKING_SECRET.

const TIMEZONE = "Atlantic/Canary";
const CALENDAR_ID = "primary";
const MEETING_MINUTES = 30;
const DAY_START = "09:00"; // las mañanas son las mejores horas
const DAY_END = "15:00";   // ninguna reunión termina después de las 15:00 hora canaria
const WORKDAYS = [1, 2, 3, 4, 5]; // lunes a viernes
const MIN_NOTICE_HOURS = 24;
const DAYS_AHEAD = 21;
const MAX_FIELD = 500;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    try {
      if (url.pathname === "/api/slots" && request.method === "GET") return await handleSlots(env);
      if (url.pathname === "/api/request" && request.method === "POST") return await handleRequest(request, env);
      if (url.pathname === "/api/review" && request.method === "GET") return await handleReviewPage(url, env);
      if (url.pathname === "/api/review" && request.method === "POST") return await handleReviewAction(request, env);
    } catch (error) {
      console.error(error);
      if (url.pathname === "/api/review") return page("Algo ha fallado", `<p>${escapeHtml(error.message)}</p>`, 500);
      return json({ error: "Ahora mismo no podemos procesar la reserva. Inténtalo de nuevo en unos minutos." }, 500);
    }
    if (url.pathname.startsWith("/api/")) return json({ error: "No encontrado" }, 404);
    return env.ASSETS.fetch(request);
  },
};

// ---------- Huecos disponibles ----------

async function handleSlots(env) {
  const slots = await availableSlots(env);
  return json({ timeZone: TIMEZONE, minutes: MEETING_MINUTES, slots }, 200, { "Cache-Control": "no-store" });
}

async function availableSlots(env) {
  const now = Date.now();
  const earliest = now + MIN_NOTICE_HOURS * 3600e3;
  const candidates = [];
  const today = zonedParts(new Date(now));

  for (let offset = 0; offset <= DAYS_AHEAD; offset++) {
    const day = new Date(Date.UTC(today.year, today.month - 1, today.day + offset));
    if (!WORKDAYS.includes(day.getUTCDay())) continue;
    const [y, m, d] = [day.getUTCFullYear(), day.getUTCMonth() + 1, day.getUTCDate()];
    const dayEnd = zonedToUtc(y, m, d, ...hm(DAY_END));
    for (let t = zonedToUtc(y, m, d, ...hm(DAY_START)); t + MEETING_MINUTES * 60e3 <= dayEnd; t += MEETING_MINUTES * 60e3) {
      if (t >= earliest) candidates.push(t);
    }
  }
  if (!candidates.length) return [];

  const busy = await freeBusy(env, candidates[0], candidates[candidates.length - 1] + MEETING_MINUTES * 60e3);
  return candidates
    .filter((start) => !overlapsBusy(busy, start, start + MEETING_MINUTES * 60e3))
    .map((start) => new Date(start).toISOString());
}

async function freeBusy(env, from, to) {
  const data = await google(env, "https://www.googleapis.com/calendar/v3/freeBusy", {
    method: "POST",
    body: { timeMin: new Date(from).toISOString(), timeMax: new Date(to).toISOString(), timeZone: TIMEZONE, items: [{ id: CALENDAR_ID }] },
  });
  return (data.calendars?.[CALENDAR_ID]?.busy || []).map((b) => [Date.parse(b.start), Date.parse(b.end)]);
}

function overlapsBusy(busy, start, end) {
  return busy.some(([bs, be]) => bs < end && be > start);
}

async function isSlotStillAvailable(env, start) {
  const slots = await availableSlots(env);
  return slots.includes(new Date(start).toISOString());
}

// ---------- Nueva solicitud ----------

async function handleRequest(request, env) {
  const body = await request.json().catch(() => ({}));
  if (body.website) return json({ ok: true }); // honeypot: los bots rellenan este campo oculto

  const name = clean(body.name);
  const email = clean(body.email).toLowerCase();
  const company = clean(body.company);
  const message = clean(body.message);
  const start = Date.parse(body.start);

  if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return json({ error: "Revisa tu nombre y tu email." }, 400);
  if (!Number.isFinite(start) || !(await isSlotStillAvailable(env, start))) {
    return json({ error: "Ese hueco ya no está disponible. Elige otro, por favor." }, 409);
  }

  const booking = { id: crypto.randomUUID(), name, email, company, message, start: new Date(start).toISOString(), createdAt: new Date().toISOString() };
  const token = await sign(env, booking);
  const origin = new URL(request.url).origin;
  const reviewUrl = `${origin}/api/review?t=${encodeURIComponent(token)}`;
  const owner = await ownerEmail(env);
  const when = formatWhen(start);

  await sendEmail(env, {
    to: owner,
    replyTo: email,
    subject: `Nueva solicitud de reunión: ${company || name} · ${when}`,
    html: emailLayout(`
      <h1 style="margin:0 0 16px;font-size:22px">Nueva solicitud de reunión</h1>
      ${detailsTable(booking)}
      <p style="margin:24px 0 8px">
        ${button(`${reviewUrl}&action=approve`, "Aprobar", "#3E7F4F")}
        &nbsp;
        ${button(`${reviewUrl}&action=reject`, "Rechazar", "#85727A")}
      </p>
      <p style="color:#6A5868;font-size:13px">Al aprobar se crea el evento en tu Google Calendar con enlace de Google Meet y la persona recibe la confirmación por email.</p>
    `),
  });

  return json({ ok: true, start: booking.start });
}

// ---------- Revisión (aprobar / rechazar) ----------

async function handleReviewPage(url, env) {
  const booking = await verify(env, url.searchParams.get("t"));
  if (!booking) return page("Enlace no válido", "<p>Este enlace no es válido o ha sido modificado.</p>", 400);

  const existing = await findEvent(env, booking.id);
  if (existing) return page("Ya aprobada", `<p>Esta reunión ya está en tu calendario.</p>${meetLine(existing)}`);

  const action = url.searchParams.get("action") === "reject" ? "reject" : "approve";
  const token = escapeHtml(url.searchParams.get("t"));
  const approveForm = `<form method="post"><input type="hidden" name="t" value="${token}"><input type="hidden" name="action" value="approve"><button class="btn ok">Aprobar y enviar confirmación</button></form>`;
  const rejectForm = `<form method="post"><input type="hidden" name="t" value="${token}"><input type="hidden" name="action" value="reject"><button class="btn no">Rechazar</button></form>`;

  // Los enlaces del email solo abren esta página; la acción requiere pulsar el botón (así los
  // escáneres de enlaces del correo no aprueban nada por su cuenta).
  return page(
    action === "approve" ? "¿Aprobar esta reunión?" : "¿Rechazar esta solicitud?",
    `${detailsTable(booking)}<div class="actions">${action === "approve" ? approveForm + rejectForm : rejectForm + approveForm}</div>`,
  );
}

async function handleReviewAction(request, env) {
  const form = await request.formData();
  const booking = await verify(env, form.get("t"));
  if (!booking) return page("Enlace no válido", "<p>Este enlace no es válido o ha sido modificado.</p>", 400);

  const existing = await findEvent(env, booking.id);
  if (existing) return page("Ya aprobada", `<p>Esta reunión ya estaba en tu calendario.</p>${meetLine(existing)}`);

  const start = Date.parse(booking.start);
  const when = formatWhen(start);

  if (form.get("action") === "reject") {
    await sendEmail(env, {
      to: booking.email,
      subject: "Sobre tu solicitud de reunión con Zeker",
      html: emailLayout(`
        <p>Hola ${escapeHtml(booking.name)},</p>
        <p>Gracias por tu interés. No podemos reunirnos el <strong>${escapeHtml(when)}</strong> (hora canaria).</p>
        <p>Puedes elegir otro hueco en <a href="${new URL(request.url).origin}/?reservar=1">nuestra web</a> o responder a este email.</p>
      `),
    });
    return page("Solicitud rechazada", `<p>Hemos avisado a ${escapeHtml(booking.name)} de que elija otra fecha.</p>`);
  }

  if (start <= Date.now()) return page("Demasiado tarde", "<p>La hora de esta reunión ya ha pasado.</p>", 410);
  const busy = await freeBusy(env, start, start + MEETING_MINUTES * 60e3);
  if (busy.length) {
    return page("Hueco ocupado", `<p>Ya tienes algo en tu calendario el ${escapeHtml(when)}. No se ha creado la reunión; puedes rechazar la solicitud para que elija otra hora.</p>`, 409);
  }

  const event = await createMeetEvent(env, booking);
  const meetUrl = event.hangoutLink || event.conferenceData?.entryPoints?.find((e) => e.entryPointType === "video")?.uri;

  await sendEmail(env, {
    to: booking.email,
    subject: `Tu reunión con Zeker está confirmada · ${when}`,
    html: emailLayout(`
      <p>Hola ${escapeHtml(booking.name)},</p>
      <p>¡Tu reunión ha sido aprobada para la fecha que elegiste!</p>
      <p style="font-size:18px;margin:20px 0"><strong>${escapeHtml(when)}</strong> (hora canaria) · ${MEETING_MINUTES} min</p>
      ${meetUrl ? `<p>Aquí tienes el enlace de Google Meet:</p><p style="margin:16px 0">${button(meetUrl, "Entrar en Google Meet", "#C24F2C")}</p><p style="font-size:13px;color:#6A5868">${escapeHtml(meetUrl)}</p>` : "<p>Te enviaremos el enlace de la videollamada en breve.</p>"}
      <p><strong>Recuerda estar listo 5 minutos antes</strong> para empezar a tiempo.</p>
      <p>También te llegará la invitación de Google Calendar para que la tengas en tu agenda.</p>
      <p>¡Hasta pronto!</p>
    `),
  });

  return page("Reunión aprobada", `<p>Evento creado en tu Google Calendar y confirmación enviada a ${escapeHtml(booking.email)}.</p>${meetLine(event)}`);
}

async function createMeetEvent(env, booking) {
  const start = new Date(booking.start);
  const end = new Date(start.getTime() + MEETING_MINUTES * 60e3);
  const description = [
    `Reunión con ${booking.name} <${booking.email}>`,
    booking.company && `Negocio: ${booking.company}`,
    booking.message && `Mensaje: ${booking.message}`,
  ].filter(Boolean).join("\n");

  return google(env, `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(CALENDAR_ID)}/events?conferenceDataVersion=1&sendUpdates=all`, {
    method: "POST",
    body: {
      summary: `Zeker × ${booking.company || booking.name}`,
      description,
      start: { dateTime: start.toISOString(), timeZone: TIMEZONE },
      end: { dateTime: end.toISOString(), timeZone: TIMEZONE },
      attendees: [{ email: booking.email, displayName: booking.name }],
      conferenceData: { createRequest: { requestId: booking.id, conferenceSolutionKey: { type: "hangoutsMeet" } } },
      extendedProperties: { private: { zekerBookingId: booking.id } },
      reminders: { useDefault: false, overrides: [{ method: "popup", minutes: 10 }] },
    },
  });
}

async function findEvent(env, bookingId) {
  const params = new URLSearchParams({ privateExtendedProperty: `zekerBookingId=${bookingId}`, maxResults: "1" });
  const data = await google(env, `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(CALENDAR_ID)}/events?${params}`);
  return data.items?.find((e) => e.status !== "cancelled") || null;
}

// ---------- Google APIs ----------

let cachedToken = null;

async function accessToken(env) {
  if (cachedToken && cachedToken.expires > Date.now() + 60e3) return cachedToken.value;
  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: env.GOOGLE_CLIENT_ID,
      client_secret: env.GOOGLE_CLIENT_SECRET,
      refresh_token: env.GOOGLE_REFRESH_TOKEN,
      grant_type: "refresh_token",
    }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(`Google OAuth: ${data.error_description || data.error || res.status}`);
  cachedToken = { value: data.access_token, expires: Date.now() + data.expires_in * 1000 };
  return cachedToken.value;
}

async function google(env, url, { method = "GET", body } = {}) {
  const res = await fetch(url, {
    method,
    headers: { Authorization: `Bearer ${await accessToken(env)}`, ...(body ? { "Content-Type": "application/json" } : {}) },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`Google API ${res.status}: ${data.error?.message || "error"}`);
  return data;
}

async function ownerEmail(env) {
  if (env.OWNER_EMAIL) return env.OWNER_EMAIL;
  const profile = await google(env, "https://gmail.googleapis.com/gmail/v1/users/me/profile");
  return profile.emailAddress;
}

// Envía desde tu propia cuenta de Gmail (scope gmail.send).
async function sendEmail(env, { to, subject, html, replyTo }) {
  const headers = [
    `To: ${to}`,
    replyTo && `Reply-To: ${replyTo}`,
    `Subject: =?UTF-8?B?${base64(subject)}?=`,
    "MIME-Version: 1.0",
    "Content-Type: text/html; charset=UTF-8",
    "Content-Transfer-Encoding: base64",
  ].filter(Boolean);
  const raw = `${headers.join("\r\n")}\r\n\r\n${base64(html).replace(/.{76}/g, "$&\r\n")}`;
  await google(env, "https://gmail.googleapis.com/gmail/v1/users/me/messages/send", {
    method: "POST",
    body: { raw: base64(raw).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "") },
  });
}

// ---------- Firma de solicitudes ----------

async function hmacKey(env) {
  if (!env.BOOKING_SECRET) throw new Error("Falta el secreto BOOKING_SECRET");
  return crypto.subtle.importKey("raw", new TextEncoder().encode(env.BOOKING_SECRET), { name: "HMAC", hash: "SHA-256" }, false, ["sign", "verify"]);
}

async function sign(env, payload) {
  const data = base64url(JSON.stringify(payload));
  const sig = await crypto.subtle.sign("HMAC", await hmacKey(env), new TextEncoder().encode(data));
  return `${data}.${bytesToBase64url(new Uint8Array(sig))}`;
}

async function verify(env, token) {
  if (!token || !token.includes(".")) return null;
  const [data, sig] = token.split(".");
  try {
    const ok = await crypto.subtle.verify("HMAC", await hmacKey(env), base64urlToBytes(sig), new TextEncoder().encode(data));
    return ok ? JSON.parse(new TextDecoder().decode(base64urlToBytes(data))) : null;
  } catch {
    return null;
  }
}

// ---------- Fechas en hora canaria ----------

function hm(value) {
  return value.split(":").map(Number);
}

function zonedParts(date) {
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat("en-US", { timeZone: TIMEZONE, hourCycle: "h23", year: "numeric", month: "numeric", day: "numeric", hour: "numeric", minute: "numeric" })
      .formatToParts(date).map((p) => [p.type, Number(p.value)]),
  );
  return parts;
}

// Hora local canaria → instante UTC (ms), teniendo en cuenta el horario de verano.
function zonedToUtc(year, month, day, hour, minute) {
  const guess = Date.UTC(year, month - 1, day, hour, minute);
  const p = zonedParts(new Date(guess));
  const offset = Date.UTC(p.year, p.month - 1, p.day, p.hour, p.minute) - guess;
  return guess - offset;
}

function formatWhen(ms) {
  const text = new Intl.DateTimeFormat("es-ES", { timeZone: TIMEZONE, weekday: "long", day: "numeric", month: "long", hour: "2-digit", minute: "2-digit" }).format(new Date(ms));
  return text.charAt(0).toUpperCase() + text.slice(1);
}

// ---------- Utilidades ----------

function clean(value) {
  return String(value ?? "").replace(/[\r\n]+/g, " ").trim().slice(0, MAX_FIELD);
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

function base64(text) {
  return bytesToBase64(new TextEncoder().encode(text));
}

function bytesToBase64(bytes) {
  let binary = "";
  for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(binary);
}

function base64url(text) {
  return bytesToBase64url(new TextEncoder().encode(text));
}

function bytesToBase64url(bytes) {
  return bytesToBase64(bytes).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function base64urlToBytes(text) {
  const binary = atob(text.replace(/-/g, "+").replace(/_/g, "/"));
  return Uint8Array.from(binary, (c) => c.charCodeAt(0));
}

function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json; charset=utf-8", ...headers } });
}

function detailsTable(b) {
  const rows = [
    ["Fecha", `${formatWhen(Date.parse(b.start))} (hora canaria)`],
    ["Nombre", b.name],
    ["Email", b.email],
    ["Negocio", b.company],
    ["Mensaje", b.message],
  ].filter(([, v]) => v);
  return `<table style="border-collapse:collapse">${rows
    .map(([k, v]) => `<tr><td style="padding:6px 16px 6px 0;color:#6A5868;vertical-align:top">${k}</td><td style="padding:6px 0"><strong>${escapeHtml(v)}</strong></td></tr>`)
    .join("")}</table>`;
}

function meetLine(event) {
  const link = event.hangoutLink;
  return link ? `<p>Google Meet: <a href="${escapeHtml(link)}">${escapeHtml(link)}</a></p>` : "";
}

function button(href, label, color) {
  return `<a href="${escapeHtml(href)}" style="display:inline-block;background:${color};color:#FBF4E4;text-decoration:none;font-weight:bold;padding:12px 22px;border-radius:999px">${escapeHtml(label)}</a>`;
}

function emailLayout(inner) {
  return `<!doctype html><html><body style="margin:0;background:#FBF4E4;font-family:Arial,sans-serif;color:#42344A">
    <div style="max-width:560px;margin:0 auto;padding:32px 24px;line-height:1.5">${inner}
    <p style="margin-top:32px;color:#85727A;font-size:13px">Zeker</p></div></body></html>`;
}

function page(title, body, status = 200) {
  const html = `<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>${escapeHtml(title)} · Zeker</title><style>
body{margin:0;background:#FBF4E4;color:#42344A;font-family:system-ui,sans-serif;line-height:1.5}
main{max-width:560px;margin:0 auto;padding:48px 16px}h1{font-size:26px;margin:0 0 20px}
.actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:28px}
.btn{border:0;border-radius:999px;padding:12px 22px;font:inherit;font-weight:700;color:#FBF4E4;cursor:pointer}
.ok{background:#3E7F4F}.no{background:#85727A}a{color:#C24F2C}
</style></head><body><main><h1>${escapeHtml(title)}</h1>${body}</main></body></html>`;
  return new Response(html, { status, headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store" } });
}
