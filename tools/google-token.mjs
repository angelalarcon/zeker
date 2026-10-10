// Obtiene el GOOGLE_REFRESH_TOKEN que usa worker.js para leer tu Google Calendar,
// crear las reuniones con Meet y enviar los emails desde tu Gmail.
//
// Uso: GOOGLE_CLIENT_ID=… GOOGLE_CLIENT_SECRET=… node tools/google-token.mjs
// Abre el enlace que aparece, acepta los permisos con tu cuenta y copia el token que se imprime.
import http from "node:http";

const { GOOGLE_CLIENT_ID: clientId, GOOGLE_CLIENT_SECRET: clientSecret } = process.env;
if (!clientId || !clientSecret) {
  console.error("Define GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET (cliente OAuth de tipo «Aplicación de escritorio»).");
  process.exit(1);
}

const PORT = 53682;
const redirectUri = `http://127.0.0.1:${PORT}`;
const scopes = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/gmail.send"];

const authUrl = new URL("https://accounts.google.com/o/oauth2/v2/auth");
authUrl.search = new URLSearchParams({
  client_id: clientId,
  redirect_uri: redirectUri,
  response_type: "code",
  scope: scopes.join(" "),
  access_type: "offline",
  prompt: "consent",
});

const server = http.createServer(async (req, res) => {
  const code = new URL(req.url, redirectUri).searchParams.get("code");
  if (!code) return res.end("Esperando autorización…");
  const tokenRes = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ code, client_id: clientId, client_secret: clientSecret, redirect_uri: redirectUri, grant_type: "authorization_code" }),
  });
  const data = await tokenRes.json();
  res.end(data.refresh_token ? "Listo. Vuelve a la terminal." : "Algo ha fallado. Mira la terminal.");
  if (data.refresh_token) console.log(`\nGOOGLE_REFRESH_TOKEN:\n${data.refresh_token}\n\nGuárdalo con: npx wrangler secret put GOOGLE_REFRESH_TOKEN`);
  else console.error(data);
  server.close();
});

server.listen(PORT, "127.0.0.1", () => console.log(`Abre este enlace en el navegador:\n\n${authUrl}\n`));
