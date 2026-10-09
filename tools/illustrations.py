"""Ilustraciones del sitio sobre fondo blanco: solo construcción y objetos, sin paisaje.

- hero: la web que se construye (andamio, grúa que baja la última pieza y cursor que pulsa el botón);
  se inserta en index.html entre los marcadores HERO-SVG.
- meeting.svg: la mesa de la reunión con el portátil.
- wheel.svg: rueda de coche detallada (ejemplo "Creamos tu web" de un taller).
- old-site-1..3.svg: miniaturas de webs anticuadas (ejemplo "Mejoramos la tuya").

Ejecuta `python3 tools/illustrations.py` desde la raíz del repo."""

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "illustrations"

CREAM, CLOUD, WALL2 = "#FBF4E4", "#FFF8EA", "#E9D3AE"
PLUM, PLUM_M, PLUM_L = "#42344A", "#5B4B66", "#7A6788"
G_MID, G_MID2, G_DARK = "#A6CB72", "#82B862", "#4F9460"
MUSTARD, MUSTARD_D, ORANGE, ORANGE_D, RED, POPPY = "#EDB84E", "#D99A36", "#E8743B", "#C95F2E", "#D9483B", "#F08A2C"
SKY_MID, SKY_LOW, SEA_L, BLUE, PEACH = "#A9CBEA", "#F1E4C8", "#9CC3E8", "#5E8FD6", "#F2C3A7"
WALL_SH, ROOF, ROOF_D = "#E2C9A6", "#C9573A", "#A8432E"
FONT = "font-family=\"'Josefin Sans', system-ui, sans-serif\" font-weight=\"700\""


def f(n):
    return f"{n:.1f}".rstrip("0").rstrip(".")


def svg(viewbox, body, defs="", extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}"{extra}>'
            + (f"<defs>{defs}</defs>" if defs else "") + body + "</svg>")


def awning(x, y, w, n, h, c1=RED, c2=CREAM):
    sw = w / n
    o = [f'<path d="M{f(x + i * sw)},{f(y)} h{f(sw)} v{f(h)} a{f(sw / 2)},{f(sw / 2)} 0 0 1 {f(-sw)},0 z" fill="{c1 if i % 2 == 0 else c2}"/>'
         for i in range(n)]
    return "".join(o)


# ---------- la web en construcción (hero) ----------

def browser_site(x0, y0, w, h, url="tunegocio.es"):
    """Ventana de navegador con una web a medio construir; la tercera tarjeta queda vacía.
    Devuelve (svg, (x, y, w, h) del hueco)."""
    o = [f'<rect x="{x0 + 12}" y="{y0 + 12}" width="{w}" height="{h}" rx="16" fill="{PLUM}"/>',
         f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="16" fill="{CLOUD}" stroke="{PLUM}" stroke-width="4"/>',
         f'<path d="M{x0 + 2},{y0 + 36} V{y0 + 16} a14,14 0 0 1 14,-14 h{w - 32} a14,14 0 0 1 14,14 V{y0 + 36} z" fill="#F6E7CB"/>',
         f'<rect x="{x0}" y="{y0 + 36}" width="{w}" height="3" fill="{PLUM}"/>']
    for i, c in enumerate((RED, MUSTARD, G_MID2)):
        o.append(f'<circle cx="{x0 + 20 + i * 17}" cy="{y0 + 19}" r="5.5" fill="{c}"/>')
    o.append(f'<rect x="{x0 + 76}" y="{y0 + 9}" width="{w - 96}" height="20" rx="10" fill="{CLOUD}" stroke="{PLUM}" stroke-width="2"/>'
             f'<circle cx="{x0 + 90}" cy="{y0 + 19}" r="4" fill="{G_DARK}"/>'
             f'<text x="{x0 + 100}" y="{y0 + 24}" font-size="13" fill="{PLUM_M}" {FONT}>{url}</text>')
    cx0, cw = x0 + 16, w - 32
    o.append(f'<circle cx="{cx0 + 9}" cy="{y0 + 56}" r="8" fill="{RED}"/>'
             f'<rect x="{cx0 + 24}" y="{y0 + 52}" width="70" height="8" rx="4" fill="{PLUM}"/>'
             f'<rect x="{x0 + w - 110}" y="{y0 + 47}" width="94" height="18" rx="9" fill="{RED}"/>'
             f'<rect x="{x0 + w - 96}" y="{y0 + 54}" width="66" height="4" rx="2" fill="{CLOUD}"/>')
    # portada de la web: bloque de color con imagen a la derecha
    hy, hh = y0 + 76, 104
    o.append(f'<rect x="{cx0}" y="{hy}" width="{cw}" height="{hh}" rx="10" fill="#F6E7CB"/>'
             f'<rect x="{cx0 + cw - 150}" y="{hy + 14}" width="134" height="{hh - 28}" rx="8" fill="{PEACH}"/>'
             f'<circle cx="{cx0 + cw - 83}" cy="{hy + hh / 2}" r="24" fill="{CLOUD}" opacity=".7"/>'
             f'<path d="M{cx0 + cw - 92},{hy + hh / 2 - 10} l18,10 l-18,10 z" fill="{ORANGE_D}"/>'
             f'<text x="{cx0 + 18}" y="{hy + 38}" font-size="22" letter-spacing="1.5" fill="{PLUM}" {FONT}>TU NEGOCIO</text>'
             f'<rect x="{cx0 + 18}" y="{hy + 48}" width="120" height="6" rx="3" fill="{PLUM_L}"/>'
             f'<rect x="{cx0 + 18}" y="{hy + 62}" width="78" height="20" rx="10" fill="{RED}"/>'
             f'<rect x="{cx0 + 32}" y="{hy + 70}" width="50" height="4" rx="2" fill="{CLOUD}"/>')
    ty, th, gap = hy + hh + 12, h - (hy + hh + 12 - y0) - 14, 12
    tw = (cw - 2 * gap) / 3
    for i in range(2):
        tx = cx0 + i * (tw + gap)
        o.append(f'<rect x="{f(tx)}" y="{ty}" width="{f(tw)}" height="{th}" rx="8" fill="#FFFFFF" stroke="{WALL2}" stroke-width="2"/>'
                 f'<rect x="{f(tx + 12)}" y="{ty + th - 22}" width="{f(tw * 0.55)}" height="6" rx="3" fill="{PLUM}"/>'
                 f'<rect x="{f(tx + 12)}" y="{ty + th - 12}" width="{f(tw * 0.35)}" height="4" rx="2" fill="{PLUM_L}"/>')
        ix, iy = tx + 12, ty + 10
        if i == 0:
            o.append(awning(ix, iy, 40, 5, 10))
        else:
            o.append(f'<rect x="{f(ix + 6)}" y="{iy + 6}" width="30" height="6" rx="3" fill="{BLUE}" transform="rotate(-20 {f(ix + 20)} {iy + 9})"/>'
                     f'<circle cx="{f(ix + 6)}" cy="{iy + 14}" r="7" fill="{BLUE}"/><circle cx="{f(ix + 6)}" cy="{iy + 14}" r="3" fill="#FFFFFF"/>')
    slot = (cx0 + 2 * (tw + gap), ty, tw, th)
    sx, sy, sw, sh = slot
    o.append(f'<rect x="{f(sx)}" y="{sy}" width="{f(sw)}" height="{sh}" rx="8" fill="none" stroke="{PLUM_L}" stroke-width="2" stroke-dasharray="7 6"/>')
    return "".join(o), slot


def transport_card(w, h):
    return (f'<rect width="{f(w)}" height="{h}" rx="8" fill="#FFFFFF" stroke="{PLUM}" stroke-width="2"/>'
            f'<rect x="12" y="12" width="26" height="14" rx="2" fill="{ORANGE}"/><path d="M38,15 h7 l5,6 v5 h-12 z" fill="{ORANGE}"/>'
            f'<circle cx="18" cy="27" r="4" fill="{PLUM}"/><circle cx="42" cy="27" r="4" fill="{PLUM}"/>'
            f'<rect x="12" y="{h - 22}" width="{f(w * 0.55)}" height="6" rx="3" fill="{PLUM}"/>'
            f'<rect x="12" y="{h - 12}" width="{f(w * 0.35)}" height="4" rx="2" fill="{PLUM_L}"/>')


def scaffolding(x0, x1, top, base):
    o = [f'<rect x="{x - 2}" y="{top}" width="4" height="{base - top}" fill="{PLUM_M}"/>' for x in (x0, x1)]
    y = base
    while y - 50 >= top:
        o.append(f'<path d="M{x0},{y} L{x1},{y - 50}" stroke="{PLUM_L}" stroke-width="2.5"/>'
                 f'<rect x="{x0 - 6}" y="{y - 52}" width="{x1 - x0 + 12}" height="6" rx="1" fill="{MUSTARD}"/>')
        y -= 50
    return "".join(o)


def crane(mast_x, base, top, jib_left, jib_right, trolley_x):
    o = [f'<rect x="{mast_x - 12}" y="{top}" width="24" height="{base - top}" fill="none" stroke="{ORANGE}" stroke-width="4"/>']
    y = base
    while y - 24 > top:
        o.append(f'<path d="M{mast_x - 12},{y} L{mast_x + 12},{y - 24} M{mast_x + 12},{y - 24} L{mast_x - 12},{y - 48}" stroke="{ORANGE_D}" stroke-width="2.5"/>')
        y -= 48
    o.append(f'<rect x="{jib_left}" y="{top - 16}" width="{jib_right - jib_left}" height="14" fill="none" stroke="{ORANGE}" stroke-width="3.5"/>')
    x = jib_left
    while x + 28 <= jib_right:
        o.append(f'<path d="M{x},{top - 2} L{x + 14},{top - 16} L{x + 28},{top - 2}" fill="none" stroke="{ORANGE_D}" stroke-width="2"/>')
        x += 28
    o.append(f'<path d="M{mast_x},{top - 16} L{mast_x},{top - 52} L{jib_left + 30},{top - 16} M{mast_x},{top - 52} L{jib_right - 10},{top - 16}" fill="none" stroke="{PLUM_M}" stroke-width="2"/>'
             f'<rect x="{jib_right - 36}" y="{top - 2}" width="34" height="30" rx="3" fill="{PLUM_M}"/>'
             f'<rect x="{mast_x + 12}" y="{top}" width="30" height="24" rx="4" fill="{MUSTARD}"/><rect x="{mast_x + 18}" y="{top + 5}" width="16" height="10" rx="2" fill="{SEA_L}"/>'
             f'<rect x="{trolley_x - 10}" y="{top - 2}" width="20" height="8" rx="2" fill="{PLUM}"/>')
    return "".join(o)


def cursor_icon():
    return ('<path d="M3,4 l0,34 l9,-8 l7,15 l7,-3 l-7,-15 l12,-1 z" fill="#2E2638" opacity=".2"/>'
            f'<path d="M0,0 l0,34 l9,-8 l7,15 l7,-3 l-7,-15 l12,-1 z" fill="#FFFFFF" stroke="{PLUM}" stroke-width="3" stroke-linejoin="round"/>')


def hero():
    bx, by, bw, bh = 560, 626, 480, 270
    o = [f'<ellipse cx="{bx + bw / 2 + 60}" cy="{by + bh + 22}" rx="420" ry="10" fill="{PLUM}" opacity=".08"/>',
         scaffolding(522, 548, by + 40, by + bh + 4)]
    site, (sx, sy, sw, sh) = browser_site(bx, by, bw, bh)
    o.append(site)
    trolley = round(sx + sw / 2)
    o.append(crane(1100, by + bh + 4, 606, int(sx - 10), 1230, trolley))
    drop = 120
    o.append(f'<line x1="{trolley}" y1="612" x2="{trolley}" y2="{f(sy - 14)}" stroke="{PLUM}" stroke-width="2">'
             f'<animate attributeName="y2" values="{f(sy - 14 - drop)};{f(sy - 14)};{f(sy - 14)}" keyTimes="0;0.55;1" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1;0 0 1 1"/></line>')
    o.append(f'<g><animateTransform attributeName="transform" type="translate" values="0,{-drop};0,0;0,0" keyTimes="0;0.55;1" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1;0 0 1 1"/>'
             f'<path d="M{f(trolley - 14)},{f(sy)} L{trolley},{f(sy - 14)} L{f(trolley + 14)},{f(sy)}" fill="none" stroke="{PLUM}" stroke-width="2"/>'
             f'<g transform="translate({f(sx)},{f(sy)})">{transport_card(sw, sh)}</g></g>')
    cta_x, cta_y = bx + 16 + 18 + 40, by + 76 + 72
    o.append(f'<circle cx="{cta_x}" cy="{cta_y}" r="6" fill="none" stroke="{RED}" stroke-width="3" opacity="0">'
             '<animate attributeName="r" values="6;6;26" keyTimes="0;0.62;0.8" dur="7s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="0;0;.9;0" keyTimes="0;0.6;0.64;0.8" dur="7s" repeatCount="indefinite"/></circle>')
    o.append(f'<g><animateMotion dur="7s" repeatCount="indefinite" path="M{bx + 300},{by + 220} C{bx + 260},{by + 170} {bx + 150},{by + 200} {cta_x},{cta_y} '
             f'L{cta_x},{cta_y} C{bx + 150},{by + 120} {bx + 300},{by + 260} {bx + 300},{by + 220}" keyTimes="0;0.55;0.75;1" keyPoints="0;0.45;0.45;1" calcMode="linear"/>'
             f'<g><animateTransform attributeName="transform" type="scale" values="1;1;.85;1;1" keyTimes="0;0.6;0.63;0.67;1" dur="7s" repeatCount="indefinite"/>'
             + cursor_icon() + '</g></g>')
    return svg("500 540 760 400", "".join(o), extra=' class="hero-svg" aria-hidden="true" focusable="false"')


# ---------- la reunión ----------

def meeting():
    o = [f'<ellipse cx="300" cy="420" rx="240" ry="18" fill="{PLUM}" opacity=".08"/>']
    for cx in (78, 522):
        w = 76
        x = cx - w / 2
        o.append(f'<rect x="{f(x + 8)}" y="250" width="6" height="150" rx="3" fill="{PLUM_M}"/>'
                 f'<rect x="{f(x + w - 14)}" y="250" width="6" height="150" rx="3" fill="{PLUM_M}"/>'
                 f'<rect x="{f(x)}" y="242" width="{w}" height="46" rx="12" fill="{PLUM}"/>'
                 f'<rect x="{f(x + 10)}" y="254" width="{w - 20}" height="5" rx="2.5" fill="{PLUM_L}"/>'
                 f'<rect x="{f(x + 10)}" y="268" width="{w - 20}" height="5" rx="2.5" fill="{PLUM_L}"/>'
                 f'<rect x="{f(x - 6)}" y="326" width="{w + 12}" height="14" rx="5" fill="{PLUM}"/>'
                 f'<rect x="{f(x - 2)}" y="338" width="7" height="74" rx="3" fill="{PLUM}"/>'
                 f'<rect x="{f(x + w - 5)}" y="338" width="7" height="74" rx="3" fill="{PLUM}"/>')
    o.append(f'<rect x="290" y="300" width="20" height="120" fill="{PLUM_M}"/><ellipse cx="300" cy="420" rx="60" ry="10" fill="{PLUM_M}"/>'
             f'<ellipse cx="300" cy="306" rx="170" ry="34" fill="{WALL_SH}"/><ellipse cx="300" cy="298" rx="170" ry="32" fill="{CREAM}"/>')
    o.append('<g transform="translate(222,196)">'
             f'<path d="M-6,104 h168 l-10,14 h-148 z" fill="{PLUM_M}"/>'
             f'<rect width="156" height="104" rx="8" fill="{PLUM}"/><rect x="8" y="8" width="140" height="88" rx="4" fill="#FFFFFF"/>'
             f'<rect x="8" y="8" width="140" height="12" rx="4" fill="#F6E7CB"/>'
             f'<circle cx="16" cy="14" r="2.5" fill="{RED}"/><circle cx="24" cy="14" r="2.5" fill="{MUSTARD}"/><circle cx="32" cy="14" r="2.5" fill="{G_MID2}"/>'
             f'<rect x="12" y="24" width="132" height="34" rx="3" fill="#F6E7CB"/><rect x="104" y="28" width="36" height="26" rx="3" fill="{PEACH}"/>'
             f'<rect x="18" y="30" width="44" height="6" rx="3" fill="{PLUM}"/><rect x="18" y="40" width="22" height="7" rx="3.5" fill="{RED}"/>'
             f'<rect x="12" y="64" width="40" height="26" rx="3" fill="{PEACH}"/><rect x="58" y="64" width="40" height="26" rx="3" fill="#D3E28F"/>'
             f'<rect x="104" y="64" width="40" height="26" rx="3" fill="none" stroke="{PLUM_L}" stroke-width="1.5" stroke-dasharray="4 3"/></g>')
    for cx, col in ((178, RED), (432, BLUE)):
        o.append(f'<ellipse cx="{cx}" cy="300" rx="22" ry="6" fill="{WALL2}"/>'
                 f'<path d="M{cx - 14},274 h28 v14 a14,12 0 0 1 -28,0 z" fill="{col}"/>'
                 f'<path d="M{cx + 14},278 a7,7 0 0 1 0,12" fill="none" stroke="{col}" stroke-width="4"/>'
                 f'<path d="M{cx - 4},262 q-6,-8 0,-16 M{cx + 5},262 q-6,-8 0,-16" fill="none" stroke="{PLUM_L}" stroke-width="3" stroke-linecap="round" opacity=".5"/>')
    return svg("0 170 600 270", "".join(o))


# ---------- rueda de coche (taller) ----------

def wheel():
    """Rueda con neumático de dibujo marcado, llanta de cinco radios dobles, disco perforado y pinza roja."""
    cx = cy = 200
    defs = ('<radialGradient id="tire" cx="45%" cy="40%" r="62%"><stop offset="0" stop-color="#4A4450"/><stop offset=".72" stop-color="#2B2730"/><stop offset="1" stop-color="#18151C"/></radialGradient>'
            '<linearGradient id="rim" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F4F6F9"/><stop offset=".45" stop-color="#C5CCD5"/><stop offset="1" stop-color="#7E8794"/></linearGradient>'
            '<linearGradient id="spoke" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".5" stop-color="#D3D9E1"/><stop offset="1" stop-color="#8F98A5"/></linearGradient>'
            '<radialGradient id="disc" cx="50%" cy="50%" r="50%"><stop offset=".55" stop-color="#9AA1AB"/><stop offset="1" stop-color="#6B727C"/></radialGradient>'
            '<radialGradient id="hub" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#8A93A0"/></radialGradient>')
    o = [f'<ellipse cx="{cx + 10}" cy="{cy + 184}" rx="150" ry="14" fill="{PLUM}" opacity=".18"/>',
         f'<circle cx="{cx}" cy="{cy}" r="178" fill="url(#tire)"/>']
    for i in range(48):  # dibujo de la banda de rodadura
        a = i * 360 / 48
        o.append(f'<rect x="{cx - 7}" y="{cy - 178}" width="14" height="20" rx="3" fill="{"#1F1B23" if i % 2 else "#3A3540"}" transform="rotate({f(a)} {cx} {cy})"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="150" fill="#2F2A35"/><circle cx="{cx}" cy="{cy}" r="148" fill="none" stroke="#45404C" stroke-width="3"/>')
    for i in range(12):  # marcas en el flanco
        o.append(f'<path d="M{cx},{cy - 138} a138,138 0 0 1 {f(138 * math.sin(math.radians(14)))},{f(138 - 138 * math.cos(math.radians(14)))}" '
                 f'stroke="#4E4856" stroke-width="5" fill="none" stroke-linecap="round" transform="rotate({i * 30 + 8} {cx} {cy})"/>')
    o.append(f'<path d="M{cx - 120},{cy - 90} A150,150 0 0 1 {cx + 40},{cy - 146}" stroke="#FFFFFF" stroke-width="10" fill="none" stroke-linecap="round" opacity=".12"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="112" fill="#3B3640"/><circle cx="{cx}" cy="{cy}" r="98" fill="url(#disc)"/>')
    for ring, n in ((84, 18), (72, 14)):
        for i in range(n):
            a = math.radians(i * 360 / n + ring)
            o.append(f'<circle cx="{f(cx + math.cos(a) * ring)}" cy="{f(cy + math.sin(a) * ring)}" r="3" fill="#5A616B"/>')
    o.append(f'<path d="M{cx + 52},{cy - 86} a100,100 0 0 1 46,62 l-26,10 a72,72 0 0 0 -32,-46 z" fill="{RED}"/>'
             f'<path d="M{cx + 56},{cy - 80} a92,92 0 0 1 36,48" stroke="#F27A6C" stroke-width="5" fill="none" stroke-linecap="round"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="112" fill="none" stroke="url(#rim)" stroke-width="16"/>'
             f'<circle cx="{cx}" cy="{cy}" r="104" fill="none" stroke="#6E7682" stroke-width="2"/>')
    for i in range(5):
        o.append(f'<g transform="rotate({i * 72} {cx} {cy})">'
                 f'<path d="M{cx - 14},{cy - 26} L{cx - 22},{cy - 104} Q{cx - 8},{cy - 110} {cx - 2},{cy - 104} L{cx - 2},{cy - 28} Z" fill="url(#spoke)"/>'
                 f'<path d="M{cx + 14},{cy - 26} L{cx + 22},{cy - 104} Q{cx + 8},{cy - 110} {cx + 2},{cy - 104} L{cx + 2},{cy - 28} Z" fill="url(#spoke)"/>'
                 f'<path d="M{cx - 12},{cy - 30} L{cx - 18},{cy - 100}" stroke="#FFFFFF" stroke-width="2" opacity=".8"/></g>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="34" fill="url(#hub)"/><circle cx="{cx}" cy="{cy}" r="34" fill="none" stroke="#6E7682" stroke-width="2"/>')
    for i in range(5):
        a = math.radians(i * 72 + 36)
        o.append(f'<circle cx="{f(cx + math.cos(a) * 21)}" cy="{f(cy + math.sin(a) * 21)}" r="5" fill="#5A616B"/>'
                 f'<circle cx="{f(cx + math.cos(a) * 21 - 1)}" cy="{f(cy + math.sin(a) * 21 - 1)}" r="2" fill="#E8ECF1"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="11" fill="{PLUM}"/>')
    return svg("0 0 400 400", "".join(o), defs=defs)


# ---------- webs anticuadas (para "mejoramos la tuya") ----------

def old_site(variant):
    """Miniatura de una web vieja: cabecera degradada, letra diminuta, columnas apretadas, banners."""
    chrome = ('<rect width="320" height="220" rx="10" fill="#E6E6E6"/>'
              '<rect x="0" y="0" width="320" height="22" rx="10" fill="#BDBDBD"/><rect x="0" y="12" width="320" height="10" fill="#BDBDBD"/>'
              '<circle cx="12" cy="11" r="4" fill="#9E9E9E"/><circle cx="24" cy="11" r="4" fill="#9E9E9E"/><circle cx="36" cy="11" r="4" fill="#9E9E9E"/>'
              '<rect x="50" y="5" width="220" height="12" rx="2" fill="#F5F5F5"/>')

    def lines(x, y, n, w, c="#9A9A9A", gap=7):
        return "".join(f'<rect x="{x}" y="{y + i * gap}" width="{w - (i * 13) % 30}" height="3" fill="{c}"/>' for i in range(n))

    if variant == 1:
        body = ('<defs><linearGradient id="og1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A6EA5"/><stop offset="1" stop-color="#1D3E66"/></linearGradient></defs>'
                '<rect x="6" y="28" width="308" height="34" fill="url(#og1)"/><rect x="12" y="36" width="80" height="10" fill="#FFD84A"/><rect x="12" y="50" width="120" height="4" fill="#C9D8EA"/>'
                '<rect x="6" y="64" width="308" height="10" fill="#FFF36B"/>' + lines(12, 67, 1, 290, "#C0392B") +
                '<rect x="6" y="78" width="70" height="136" fill="#D6E2F0"/>' + lines(12, 84, 14, 58, "#1E5BB8", 9) +
                '<rect x="82" y="78" width="160" height="60" fill="#FFFFFF"/>' + lines(88, 84, 7, 148) +
                '<rect x="82" y="142" width="160" height="72" fill="#FFFFFF"/>' + lines(88, 148, 9, 148) +
                '<rect x="248" y="78" width="66" height="70" fill="#FF6B35"/><rect x="254" y="86" width="54" height="8" fill="#FFF"/><rect x="254" y="100" width="40" height="5" fill="#FFE3D6"/>'
                '<rect x="248" y="152" width="66" height="62" fill="#9ACD32"/>' + lines(254, 160, 6, 54, "#FFFFFF"))
    elif variant == 2:
        body = ('<rect x="6" y="28" width="308" height="22" fill="#7B1FA2"/><rect x="12" y="34" width="60" height="10" fill="#FFFFFF"/>'
                + "".join(f'<rect x="{90 + i * 38}" y="37" width="30" height="5" fill="#E1BEE7"/>' for i in range(6)) +
                '<rect x="6" y="52" width="308" height="44" fill="#FFFFFF"/><rect x="12" y="58" width="296" height="32" fill="#EEE"/>'
                + "".join(f'<rect x="{18 + i * 72}" y="64" width="62" height="20" fill="#{c}"/>' for i, c in enumerate(("FFFFFF", "FFFFFF", "FFFFFF", "F44336"))) +
                '<rect x="6" y="100" width="308" height="114" fill="#FFFFFF"/>'
                + "".join(f'<rect x="{12 + (i % 4) * 75}" y="{106 + (i // 4) * 54}" width="69" height="48" fill="#F3E5F5"/>' + lines(16 + (i % 4) * 75, 112 + (i // 4) * 54, 5, 60, "#8E8E8E", 8) for i in range(8)) +
                '<rect x="200" y="150" width="110" height="60" fill="#FFFFFF" stroke="#333" stroke-width="1.5"/><rect x="200" y="150" width="110" height="12" fill="#333"/>'
                '<rect x="296" y="152" width="10" height="8" fill="#F44336"/>' + lines(206, 168, 4, 96, "#555", 8))
    else:
        body = ('<rect x="6" y="28" width="308" height="186" fill="#F8F3D9"/><rect x="70" y="30" width="180" height="182" fill="#FFFFFF" stroke="#999" stroke-width="1"/>'
                '<rect x="80" y="36" width="160" height="26" fill="#2E7D32"/><rect x="88" y="44" width="90" height="10" fill="#FFF59D"/>'
                + "".join(f'<rect x="{80 + i * 41}" y="66" width="37" height="12" fill="#C8E6C9" stroke="#2E7D32" stroke-width="1"/>' for i in range(4)) +
                lines(82, 86, 12, 156, "#6D6D6D", 8) +
                '<rect x="80" y="186" width="70" height="18" fill="#E0E0E0" stroke="#777" stroke-width="1.5"/><rect x="90" y="193" width="50" height="4" fill="#555"/>'
                '<rect x="12" y="40" width="50" height="150" fill="#FFCC80"/>' + lines(16, 46, 15, 42, "#8D6E63", 9) +
                '<rect x="258" y="40" width="50" height="150" fill="#B3E5FC"/>' + lines(262, 46, 15, 42, "#0277BD", 9))
    return svg("0 0 320 220", chrome + body)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    files = {"meeting.svg": meeting(), "wheel.svg": wheel(), **{f"old-site-{i}.svg": old_site(i) for i in (1, 2, 3)}}
    for name, content in files.items():
        (OUT / name).write_text(content + "\n")
        print(f"{name}: {len(content) // 1024} KB")
    index = ROOT / "index.html"
    html = index.read_text()
    start, end = "<!-- HERO-SVG:START -->", "<!-- HERO-SVG:END -->"
    if start in html and end in html:
        before, rest = html.split(start, 1)
        _, after = rest.split(end, 1)
        index.write_text(before + start + hero() + end + after)
        print(f"hero inline: {len(hero()) // 1024} KB")


if __name__ == "__main__":
    main()
