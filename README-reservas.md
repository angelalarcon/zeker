# Reservas con Google Calendar

El botón **Reservar** ya no usa Calendly. Ahora:

1. La persona elige un hueco libre de tu Google Calendar (lunes a viernes, 9:00–15:00 hora canaria, reuniones de 30 min; ninguna termina después de las 15:00, mínimo 24 h de antelación).
2. Te llega un email con la solicitud y los botones **Aprobar** / **Rechazar**.
3. Al aprobar se crea el evento en tu calendario con **Google Meet** y la persona recibe un email: reunión aprobada para la fecha que eligió, enlace de Meet y que esté lista 5 minutos antes. Al rechazar, recibe un email para que elija otra fecha.

Los emails salen de tu propia cuenta de Gmail. La lógica está en `worker.js` y los horarios se cambian arriba del todo (`DAY_START`, `DAY_END`, `WORKDAYS`, `MIN_NOTICE_HOURS`…).

## Configuración (una sola vez)

1. **Google Cloud** (https://console.cloud.google.com), con la cuenta de tu calendario:
   - Crea un proyecto y activa **Google Calendar API** y **Gmail API**.
   - *Pantalla de consentimiento OAuth*: tipo «Externo», añade tu email como usuario de prueba y luego pulsa **Publicar aplicación** (en modo prueba el token caduca a los 7 días).
   - *Credenciales → Crear ID de cliente OAuth* → tipo **Aplicación de escritorio**. Copia el ID y el secreto.
2. **Token** (en tu ordenador, dentro del repo):
   ```sh
   GOOGLE_CLIENT_ID=… GOOGLE_CLIENT_SECRET=… node tools/google-token.mjs
   ```
   Abre el enlace, acepta los permisos y copia el `GOOGLE_REFRESH_TOKEN`.
3. **Secretos del Worker** (`npx wrangler login` si hace falta), o en el panel de Cloudflare → Workers → zeker → Settings → Variables and Secrets:
   ```sh
   npx wrangler secret put GOOGLE_CLIENT_ID
   npx wrangler secret put GOOGLE_CLIENT_SECRET
   npx wrangler secret put GOOGLE_REFRESH_TOKEN
   npx wrangler secret put BOOKING_SECRET   # una frase larga y aleatoria, p. ej. `openssl rand -hex 32`
   ```
   Opcional: `OWNER_EMAIL` si quieres recibir las solicitudes en otro correo (por defecto, la cuenta de Gmail conectada).
4. Despliega (`npx wrangler deploy`) y prueba en `/api/slots`: debe devolver tus huecos libres.
