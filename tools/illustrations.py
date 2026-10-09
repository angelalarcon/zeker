"""Genera las ilustraciones SVG del sitio en estilo póster de viaje (capas planas, nubes de círculos,
carreteras sinuosas). Ejecuta `python3 tools/illustrations.py` desde la raíz del repo:
escribe assets/illustrations/*.svg e inserta el hero en index.html entre los marcadores HERO-SVG."""

import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "illustrations"

# Paleta
SKY_TOP, SKY_MID, SKY_LOW = "#7FAEE0", "#B9D5EE", "#F3E6CC"
CREAM, CLOUD, PEACH, PEACH_D = "#FBF4E4", "#FFF8EA", "#F2C3A7", "#E9A88A"
LILAC, LILAC_D, LILAC_L, SNOW = "#B8B2DD", "#948BC4", "#CEC9EA", "#F7F4FB"
PLUM, PLUM_M, PLUM_L = "#42344A", "#5B4B66", "#7A6788"
G_LIGHT, G_MID, G_MID2, G_DARK, G_DEEP = "#D3E28F", "#A6CB72", "#82B862", "#4F9460", "#2F6B47"
MUSTARD, ORANGE, RED, POPPY = "#EDB84E", "#E8743B", "#D9483B", "#F08A2C"
ROAD, LINE = "#6E6178", "#F7EEDC"
SEA, SEA_L = "#5F9BD6", "#9CC3E8"
ROOF, WALL, WALL2 = "#C9573A", "#F6E7CB", "#E9D3AE"
BLUE_CAR, DARK = "#5E8FD6", "#2E2638"


def f(n):
    return f"{n:.1f}".rstrip("0").rstrip(".")


# ---------- geometría ----------

def catmull(points, steps=12):
    """Muestrea una curva Catmull-Rom que pasa por todos los puntos."""
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for s in range(steps):
            t = s / steps
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(points[-1])
    return out


def poly_d(pts, close=True):
    d = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts)
    return d + (" Z" if close else "")


def hill(points, color, extra="", bottom=2000):
    """Colina suave que baja hasta el borde inferior (el viewBox recorta lo que sobra)."""
    pts = catmull(points, 10)
    pts = [(pts[0][0], bottom)] + pts + [(pts[-1][0], bottom)]
    return f'<path d="{poly_d(pts)}" fill="{color}"{extra}/>'


def cloud(x, y, s=1.0, color=CLOUD, extra=""):
    circles = [(0, 0, 34), (40, -22, 44), (92, -8, 36), (128, 6, 26), (-30, 10, 22)]
    parts = [f'<circle cx="{f(x + cx * s)}" cy="{f(y + cy * s)}" r="{f(r * s)}"/>' for cx, cy, r in circles]
    parts.append(f'<rect x="{f(x - 52 * s)}" y="{f(y + 4 * s)}" width="{f(206 * s)}" height="{f(28 * s)}" rx="{f(14 * s)}"/>')
    return f'<g fill="{color}"{extra}>' + "".join(parts) + "</g>"


def dots(rng, n, box, rmin, rmax, colors):
    x0, y0, x1, y1 = box
    return "".join(
        f'<circle cx="{f(rng.uniform(x0, x1))}" cy="{f(rng.uniform(y0, y1))}" r="{f(rng.uniform(rmin, rmax))}" fill="{rng.choice(colors)}"/>'
        for _ in range(n)
    )


def mountains(peaks, base, color, shade, snow=None):
    """peaks: lista de (x, y) alternando valles y picos; dibuja cara en sombra y nieve."""
    pts = [(peaks[0][0], base)] + peaks + [(peaks[-1][0], base)]
    out = [f'<path d="{poly_d(pts)}" fill="{color}"/>']
    for i in range(1, len(peaks) - 1):
        px, py = peaks[i]
        if py >= peaks[i - 1][1] or py >= peaks[i + 1][1]:
            continue  # no es un pico
        nx, ny = peaks[i + 1]
        out.append(f'<path d="{poly_d([(px, py), (nx, ny), (nx - 10, base), (px + (nx - px) * 0.15, base)])}" fill="{shade}"/>')
        if snow:
            d = (base - py) * 0.22
            cap = [(px, py), (px + d * 0.9, py + d * 1.1), (px + d * 0.3, py + d * 0.8), (px - d * 0.1, py + d * 1.25),
                   (px - d * 0.5, py + d * 0.85), (px - d * 0.95, py + d * 1.15)]
            out.append(f'<path d="{poly_d(cap)}" fill="{snow}"/>')
    return "".join(out)


def conifer(x, y, h, dark=G_DEEP, light=G_DARK):
    w = h * 0.42
    return (f'<path d="M{f(x)},{f(y - h)} L{f(x - w)},{f(y)} L{f(x)},{f(y)} Z" fill="{dark}"/>'
            f'<path d="M{f(x)},{f(y - h)} L{f(x + w)},{f(y)} L{f(x)},{f(y)} Z" fill="{light}"/>')


def cypress(x, y, h, dark=PLUM_M, light=PLUM_L):
    w = h * 0.16
    return (f'<path d="M{f(x)},{f(y - h)} C{f(x - w * 1.6)},{f(y - h * 0.55)} {f(x - w * 1.2)},{f(y)} {f(x)},{f(y)} Z" fill="{dark}"/>'
            f'<path d="M{f(x)},{f(y - h)} C{f(x + w * 1.6)},{f(y - h * 0.55)} {f(x + w * 1.2)},{f(y)} {f(x)},{f(y)} Z" fill="{light}"/>')


def round_tree(x, y, r, dark=G_DARK, light=G_MID2, trunk=PLUM_M):
    return (f'<rect x="{f(x - r * 0.09)}" y="{f(y - r * 0.9)}" width="{f(r * 0.18)}" height="{f(r * 0.9)}" fill="{trunk}"/>'
            f'<circle cx="{f(x)}" cy="{f(y - r * 1.5)}" r="{f(r)}" fill="{dark}"/>'
            f'<circle cx="{f(x + r * 0.25)}" cy="{f(y - r * 1.65)}" r="{f(r * 0.7)}" fill="{light}"/>')


def road(center, w0, w1, color=ROAD, line=LINE, dash=True, steps=14):
    pts = catmull(center, steps)
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        ax, ay = pts[max(i - 1, 0)]
        bx, by = pts[min(i + 1, n - 1)]
        dx, dy = bx - ax, by - ay
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        w = (w0 + (w1 - w0) * (i / (n - 1))) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    out = f'<path d="{poly_d(left + right[::-1])}" fill="{color}"/>'
    if dash:
        out += f'<path d="{poly_d(pts, close=False)}" fill="none" stroke="{line}" stroke-width="{f(max(w0 * 0.035, 2))}" stroke-dasharray="{f(w0 * 0.18)} {f(w0 * 0.22)}" stroke-linecap="round"/>'
    return out, poly_d(pts, close=False)


def birds(x, y, s=1.0, color=PLUM, extra=""):
    def b(bx, by, k):
        return (f'<path d="M{f(bx)},{f(by)} q{f(7 * k)},{f(-7 * k)} {f(14 * k)},0 q{f(7 * k)},{f(-7 * k)} {f(14 * k)},0" '
                f'fill="none" stroke="{color}" stroke-width="{f(3 * k)}" stroke-linecap="round" stroke-linejoin="round"/>')
    return f"<g{extra}>" + b(x, y, s) + b(x + 40 * s, y - 18 * s, s * 0.8) + b(x + 70 * s, y + 8 * s, s * 0.7) + "</g>"


# ---------- objetos ----------

def van_back():
    """Furgoneta vista desde atrás; origen en el centro de las ruedas, sobre el suelo."""
    return (
        '<ellipse cx="0" cy="0" rx="72" ry="9" fill="#2E2638" opacity=".25"/>'
        '<rect x="-60" y="-20" width="22" height="20" rx="4" fill="#2E2638"/>'
        '<rect x="38" y="-20" width="22" height="20" rx="4" fill="#2E2638"/>'
        f'<rect x="-66" y="-118" width="132" height="102" rx="16" fill="{RED}"/>'
        f'<path d="M-66,-88 v-14 a16,16 0 0 1 16,-16 h100 a16,16 0 0 1 16,16 v14 z" fill="{CREAM}"/>'
        '<rect x="-52" y="-108" width="104" height="34" rx="7" fill="#3B3550"/>'
        '<rect x="-46" y="-104" width="40" height="8" rx="4" fill="#5B5272"/>'
        f'<rect x="-62" y="-66" width="11" height="18" rx="3" fill="{MUSTARD}"/>'
        f'<rect x="51" y="-66" width="11" height="18" rx="3" fill="{MUSTARD}"/>'
        f'<rect x="-18" y="-44" width="36" height="11" rx="2" fill="{CREAM}"/>'
        f'<rect x="-70" y="-28" width="140" height="13" rx="5" fill="{WALL2}"/>'
        # bicis en el techo
        f'<rect x="-50" y="-126" width="100" height="6" rx="3" fill="{PLUM}"/>'
    )


def van_side(color=RED, flip=False):
    """Furgoneta de reparto de perfil; origen abajo al centro."""
    g = (
        '<ellipse cx="0" cy="2" rx="96" ry="8" fill="#2E2638" opacity=".22"/>'
        f'<path d="M-92,-14 v-78 a12,12 0 0 1 12,-12 h108 l34,40 h20 a10,10 0 0 1 10,10 v40 a6,6 0 0 1 -6,6 h-172 a6,6 0 0 1 -6,-6 z" fill="{color}"/>'
        f'<path d="M32,-100 l28,34 h-34 v-34 z" fill="#3B3550"/>'
        f'<rect x="-80" y="-90" width="96" height="40" rx="6" fill="{CREAM}"/>'
        f'<rect x="-70" y="-80" width="44" height="6" rx="3" fill="{color}"/>'
        f'<rect x="-70" y="-68" width="70" height="6" rx="3" fill="{MUSTARD}"/>'
        f'<rect x="84" y="-40" width="10" height="10" rx="2" fill="{MUSTARD}"/>'
        '<circle cx="-56" cy="-10" r="17" fill="#2E2638"/><circle cx="-56" cy="-10" r="7" fill="#B8B2C4"/>'
        '<circle cx="62" cy="-10" r="17" fill="#2E2638"/><circle cx="62" cy="-10" r="7" fill="#B8B2C4"/>'
        # cajas en el techo
        f'<rect x="-76" y="-122" width="34" height="18" rx="2" fill="{WALL2}"/><rect x="-38" y="-118" width="26" height="14" rx="2" fill="{MUSTARD}"/>'
    )
    return f'<g transform="scale(-1,1)">{g}</g>' if flip else g


def car_side(color=BLUE_CAR):
    """Coche clásico de perfil; origen abajo al centro."""
    return (
        '<ellipse cx="0" cy="2" rx="88" ry="7" fill="#2E2638" opacity=".22"/>'
        f'<path d="M-84,-16 c0,-18 8,-28 28,-30 l22,-22 c6,-6 14,-8 22,-8 h34 c10,0 18,4 24,12 l18,20 c22,2 30,10 30,26 v6 a4,4 0 0 1 -4,4 h-170 a4,4 0 0 1 -4,-4 z" fill="{color}"/>'
        '<path d="M-28,-48 l18,-18 c4,-4 8,-5 14,-5 h10 v23 z" fill="#3B3550"/>'
        '<path d="M20,-71 h12 c8,0 13,3 17,8 l14,15 h-43 z" fill="#3B3550"/>'
        f'<rect x="-84" y="-22" width="172" height="5" rx="2" fill="{CREAM}" opacity=".7"/>'
        '<circle cx="-50" cy="-8" r="16" fill="#2E2638"/><circle cx="-50" cy="-8" r="6" fill="#B8B2C4"/>'
        '<circle cx="54" cy="-8" r="16" fill="#2E2638"/><circle cx="54" cy="-8" r="6" fill="#B8B2C4"/>'
        f'<rect x="80" y="-34" width="8" height="8" rx="2" fill="{MUSTARD}"/>'
    )


def house(x, y, w, h, wall=WALL, roof=ROOF, windows=1):
    rh = w * 0.42
    out = (f'<rect x="{f(x)}" y="{f(y - h)}" width="{f(w)}" height="{f(h)}" fill="{wall}"/>'
           f'<path d="M{f(x - w * 0.08)},{f(y - h)} L{f(x + w / 2)},{f(y - h - rh)} L{f(x + w * 1.08)},{f(y - h)} Z" fill="{roof}"/>'
           f'<rect x="{f(x + w * 0.6)}" y="{f(y - h)}" width="{f(w * 0.4)}" height="{f(h)}" fill="#000" opacity=".06"/>')
    for i in range(windows):
        wx = x + w * (0.2 + i * 0.4)
        out += f'<rect x="{f(wx)}" y="{f(y - h * 0.7)}" width="{f(w * 0.18)}" height="{f(h * 0.28)}" fill="{PLUM_M}"/>'
    return out


def restaurant(x, y, s=1.0):
    """Fachada de restaurante con toldo de rayas; origen abajo a la izquierda."""
    w, h = 150 * s, 92 * s
    stripes = "".join(
        f'<rect x="{f(x + i * w / 8)}" y="{f(y - h * 0.62)}" width="{f(w / 8)}" height="{f(16 * s)}" fill="{RED if i % 2 == 0 else CREAM}"/>'
        for i in range(8))
    scallops = "".join(
        f'<circle cx="{f(x + (i + 0.5) * w / 8)}" cy="{f(y - h * 0.62 + 16 * s)}" r="{f(w / 16)}" fill="{RED if i % 2 == 0 else CREAM}"/>'
        for i in range(8))
    return (
        f'<rect x="{f(x)}" y="{f(y - h)}" width="{f(w)}" height="{f(h)}" fill="{WALL}"/>'
        f'<path d="M{f(x - 8 * s)},{f(y - h)} h{f(w + 16 * s)} l{f(-14 * s)},{f(-26 * s)} h{f(-w + 12 * s)} z" fill="{ROOF}"/>'
        f'<rect x="{f(x + w * 0.62)}" y="{f(y - h)}" width="{f(w * 0.38)}" height="{f(h)}" fill="#000" opacity=".05"/>'
        f'<rect x="{f(x + 12 * s)}" y="{f(y - h * 0.4)}" width="{f(30 * s)}" height="{f(h * 0.4)}" fill="{PLUM_M}"/>'
        f'<rect x="{f(x + 56 * s)}" y="{f(y - h * 0.4)}" width="{f(38 * s)}" height="{f(h * 0.3)}" fill="{SEA_L}"/>'
        f'<rect x="{f(x + 106 * s)}" y="{f(y - h * 0.4)}" width="{f(30 * s)}" height="{f(h * 0.4)}" fill="{PLUM_M}"/>'
        + stripes + scallops +
        f'<rect x="{f(x + w * 0.25)}" y="{f(y - h * 0.92)}" width="{f(w * 0.5)}" height="{f(14 * s)}" rx="{f(3 * s)}" fill="{PLUM}"/>'
        f'<circle cx="{f(x + w * 0.5)}" cy="{f(y - h * 0.92 + 7 * s)}" r="{f(4 * s)}" fill="{MUSTARD}"/>'
    )


def workshop(x, y, s=1.0):
    """Taller mecánico con puerta de garaje; origen abajo a la izquierda."""
    w, h = 140 * s, 84 * s
    door = "".join(
        f'<rect x="{f(x + 18 * s)}" y="{f(y - h * 0.66 + i * 9 * s)}" width="{f(68 * s)}" height="{f(5 * s)}" fill="#5B5272"/>'
        for i in range(6))
    return (
        f'<rect x="{f(x)}" y="{f(y - h)}" width="{f(w)}" height="{f(h)}" fill="#A9C3E0"/>'
        f'<rect x="{f(x - 6 * s)}" y="{f(y - h - 10 * s)}" width="{f(w + 12 * s)}" height="{f(12 * s)}" fill="{PLUM_M}"/>'
        f'<rect x="{f(x + w * 0.66)}" y="{f(y - h)}" width="{f(w * 0.34)}" height="{f(h)}" fill="#000" opacity=".07"/>'
        f'<rect x="{f(x + 14 * s)}" y="{f(y - h * 0.7)}" width="{f(76 * s)}" height="{f(h * 0.7)}" fill="#3B3550"/>'
        + door +
        f'<rect x="{f(x + 100 * s)}" y="{f(y - h * 0.6)}" width="{f(26 * s)}" height="{f(22 * s)}" fill="{SEA_L}"/>'
        f'<rect x="{f(x + 22 * s)}" y="{f(y - h - 36 * s)}" width="{f(96 * s)}" height="{f(22 * s)}" rx="{f(4 * s)}" fill="{MUSTARD}"/>'
        # llave inglesa en el cartel
        f'<rect x="{f(x + 52 * s)}" y="{f(y - h - 27 * s)}" width="{f(36 * s)}" height="{f(5 * s)}" rx="{f(2.5 * s)}" fill="{PLUM}"/>'
        f'<circle cx="{f(x + 52 * s)}" cy="{f(y - h - 24.5 * s)}" r="{f(6 * s)}" fill="{PLUM}"/>'
        f'<circle cx="{f(x + 52 * s)}" cy="{f(y - h - 24.5 * s)}" r="{f(2.5 * s)}" fill="{MUSTARD}"/>'
        # neumáticos apilados
        f'<ellipse cx="{f(x + w + 16 * s)}" cy="{f(y - 7 * s)}" rx="{f(14 * s)}" ry="{f(7 * s)}" fill="#2E2638"/>'
        f'<ellipse cx="{f(x + w + 16 * s)}" cy="{f(y - 17 * s)}" rx="{f(14 * s)}" ry="{f(7 * s)}" fill="#3B3550"/>'
    )


def warehouse(x, y, s=1.0):
    """Nave de transportes con tejado curvo; origen abajo a la izquierda."""
    w, h = 170 * s, 70 * s
    return (
        f'<rect x="{f(x)}" y="{f(y - h)}" width="{f(w)}" height="{f(h)}" fill="{MUSTARD}"/>'
        f'<path d="M{f(x - 6 * s)},{f(y - h)} Q{f(x + w / 2)},{f(y - h - 46 * s)} {f(x + w + 6 * s)},{f(y - h)} Z" fill="{ORANGE}"/>'
        f'<rect x="{f(x + w * 0.64)}" y="{f(y - h)}" width="{f(w * 0.36)}" height="{f(h)}" fill="#000" opacity=".07"/>'
        f'<rect x="{f(x + 18 * s)}" y="{f(y - h * 0.72)}" width="{f(54 * s)}" height="{f(h * 0.72)}" fill="{PLUM_M}"/>'
        f'<rect x="{f(x + 86 * s)}" y="{f(y - h * 0.72)}" width="{f(54 * s)}" height="{f(h * 0.72)}" fill="{PLUM_M}"/>'
        f'<rect x="{f(x + 26 * s)}" y="{f(y - h * 0.5)}" width="{f(18 * s)}" height="{f(14 * s)}" fill="{WALL2}"/>'
        f'<rect x="{f(x + 46 * s)}" y="{f(y - h * 0.36)}" width="{f(16 * s)}" height="{f(14 * s)}" fill="{WALL}"/>'
    )


def church(x, y, s=1.0):
    return (
        f'<rect x="{f(x)}" y="{f(y - 110 * s)}" width="{f(26 * s)}" height="{f(110 * s)}" fill="{WALL}"/>'
        f'<path d="M{f(x - 3 * s)},{f(y - 110 * s)} L{f(x + 13 * s)},{f(y - 150 * s)} L{f(x + 29 * s)},{f(y - 110 * s)} Z" fill="{PLUM_M}"/>'
        f'<rect x="{f(x + 8 * s)}" y="{f(y - 96 * s)}" width="{f(10 * s)}" height="{f(14 * s)}" rx="{f(5 * s)}" fill="{PLUM_M}"/>'
    )


def flowers(rng, n, box, colors=(CREAM, POPPY, PEACH, "#FFFFFF")):
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        r = rng.uniform(2.5, 6) * (0.6 + 0.8 * (y - y0) / max(y1 - y0, 1))
        out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{rng.choice(colors)}"/>')
    return "".join(out)


def poppy(x, y, s=1.0):
    return (f'<path d="M{f(x)},{f(y)} q{f(-4 * s)},{f(-30 * s)} {f(2 * s)},{f(-48 * s)}" stroke="{G_DARK}" stroke-width="{f(3 * s)}" fill="none"/>'
            f'<circle cx="{f(x - 6 * s)}" cy="{f(y - 52 * s)}" r="{f(13 * s)}" fill="{POPPY}"/>'
            f'<circle cx="{f(x + 10 * s)}" cy="{f(y - 50 * s)}" r="{f(12 * s)}" fill="{ORANGE}"/>'
            f'<circle cx="{f(x + 2 * s)}" cy="{f(y - 60 * s)}" r="{f(11 * s)}" fill="{POPPY}"/>'
            f'<circle cx="{f(x + 2 * s)}" cy="{f(y - 52 * s)}" r="{f(4 * s)}" fill="{PLUM}"/>')


def sky(id_, w, h, stops):
    st = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return (f'<defs><linearGradient id="{id_}" x1="0" y1="0" x2="0" y2="1">{st}</linearGradient></defs>'
            f'<rect width="{w}" height="{h}" fill="url(#{id_})"/>')


def svg(w, h, body, cls="", extra_attrs="", style=""):
    st = f"<style>{style}</style>" if style else ""
    c = f' class="{cls}"' if cls else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"{c}{extra_attrs}>{st}{body}</svg>')


DRIFT_CSS = (
    "@keyframes drift{from{transform:translateX(-30px)}to{transform:translateX(30px)}}"
    ".drift{animation:drift 24s ease-in-out infinite alternate}.drift.slow{animation-duration:38s}"
    "@media (prefers-reduced-motion:reduce){.drift{animation:none}}"
)


# ---------- escenas ----------

def browser_site(x0, y0, w, h, url="tunegocio.es"):
    """Ventana de navegador con una web a medio construir; la tercera tarjeta queda vacía
    para que la grúa la coloque. Devuelve (svg, (x, y, w, h) del hueco)."""
    font = "font-family=\"'Josefin Sans', system-ui, sans-serif\" font-weight=\"700\""
    o = [f'<rect x="{x0 + 10}" y="{y0 + 10}" width="{w}" height="{h}" rx="16" fill="{PLUM}"/>',
         f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="16" fill="{CREAM}" stroke="{PLUM}" stroke-width="4"/>',
         f'<path d="M{x0 + 2},{y0 + 36} V{y0 + 16} a14,14 0 0 1 14,-14 h{w - 32} a14,14 0 0 1 14,14 V{y0 + 36} z" fill="#F6E7CB"/>',
         f'<rect x="{x0}" y="{y0 + 36}" width="{w}" height="3" fill="{PLUM}"/>']
    for i, c in enumerate((RED, MUSTARD, G_MID2)):
        o.append(f'<circle cx="{x0 + 20 + i * 17}" cy="{y0 + 19}" r="5.5" fill="{c}"/>')
    o.append(f'<rect x="{x0 + 76}" y="{y0 + 9}" width="{w - 96}" height="20" rx="10" fill="{CREAM}" stroke="{PLUM}" stroke-width="2"/>')
    o.append(f'<circle cx="{x0 + 90}" cy="{y0 + 19}" r="4" fill="{G_DARK}"/>')
    o.append(f'<text x="{x0 + 100}" y="{y0 + 24}" font-size="13" fill="{PLUM_M}" {font}>{url}</text>')
    # cabecera de la web
    cx0, cw = x0 + 16, w - 32
    o.append(f'<circle cx="{cx0 + 9}" cy="{y0 + 56}" r="8" fill="{RED}"/>'
             f'<rect x="{cx0 + 24}" y="{y0 + 52}" width="70" height="8" rx="4" fill="{PLUM}"/>'
             f'<rect x="{x0 + w - 110}" y="{y0 + 47}" width="94" height="18" rx="9" fill="{RED}"/>'
             f'<rect x="{x0 + w - 96}" y="{y0 + 54}" width="66" height="4" rx="2" fill="{CREAM}"/>')
    # portada de la web: un paisaje dentro del paisaje
    hy, hh = y0 + 76, 104
    o.append(f'<defs><clipPath id="site-hero"><rect x="{cx0}" y="{hy}" width="{cw}" height="{hh}" rx="10"/></clipPath>'
             f'<linearGradient id="site-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SKY_MID}"/><stop offset="1" stop-color="{SKY_LOW}"/></linearGradient></defs>')
    o.append(f'<g clip-path="url(#site-hero)"><rect x="{cx0}" y="{hy}" width="{cw}" height="{hh}" fill="url(#site-sky)"/>'
             f'<circle cx="{cx0 + cw - 70}" cy="{hy + 40}" r="20" fill="{CLOUD}"/>'
             + hill([(cx0, hy + 82), (cx0 + cw * 0.35, hy + 70), (cx0 + cw * 0.7, hy + 84), (cx0 + cw, hy + 72)], G_MID, bottom=hy + hh)
             + f'</g>')
    o.append(f'<text x="{cx0 + 18}" y="{hy + 38}" font-size="22" letter-spacing="1.5" fill="{PLUM}" {font}>TU NEGOCIO</text>'
             f'<rect x="{cx0 + 18}" y="{hy + 48}" width="120" height="6" rx="3" fill="{PLUM_L}"/>'
             f'<rect x="{cx0 + 18}" y="{hy + 62}" width="78" height="20" rx="10" fill="{RED}"/>'
             f'<rect x="{cx0 + 32}" y="{hy + 70}" width="50" height="4" rx="2" fill="{CREAM}"/>')
    # tarjetas: restaurante, taller y el hueco que falta
    ty, th, gap = hy + hh + 12, h - (hy + hh + 12 - y0) - 14, 12
    tw = (cw - 2 * gap) / 3
    for i in range(2):
        tx = cx0 + i * (tw + gap)
        o.append(f'<rect x="{f(tx)}" y="{ty}" width="{f(tw)}" height="{th}" rx="8" fill="{CLOUD}" stroke="{WALL2}" stroke-width="2"/>')
        o.append(f'<rect x="{f(tx + 12)}" y="{ty + th - 22}" width="{f(tw * 0.55)}" height="6" rx="3" fill="{PLUM}"/>'
                 f'<rect x="{f(tx + 12)}" y="{ty + th - 12}" width="{f(tw * 0.35)}" height="4" rx="2" fill="{PLUM_L}"/>')
        ix, iy = tx + 12, ty + 10
        if i == 0:  # toldo de restaurante
            o.append("".join(f'<rect x="{f(ix + k * 8)}" y="{iy}" width="8" height="10" fill="{RED if k % 2 == 0 else CREAM}"/>' for k in range(5)))
            o.append("".join(f'<circle cx="{f(ix + 4 + k * 8)}" cy="{iy + 10}" r="4" fill="{RED if k % 2 == 0 else CREAM}"/>' for k in range(5)))
        else:  # llave de taller
            o.append(f'<rect x="{f(ix + 6)}" y="{iy + 6}" width="30" height="6" rx="3" fill="{BLUE_CAR}" transform="rotate(-20 {f(ix + 20)} {iy + 9})"/>'
                     f'<circle cx="{f(ix + 6)}" cy="{iy + 14}" r="7" fill="{BLUE_CAR}"/><circle cx="{f(ix + 6)}" cy="{iy + 14}" r="3" fill="{CLOUD}"/>')
    slot = (cx0 + 2 * (tw + gap), ty, tw, th)
    sx, sy, sw, sh = slot
    o.append(f'<rect x="{f(sx)}" y="{sy}" width="{f(sw)}" height="{sh}" rx="8" fill="none" stroke="{PLUM_L}" stroke-width="2" stroke-dasharray="7 6"/>')
    return "".join(o), slot


def transport_card(w, h):
    """Tarjeta de transporte que baja la grúa; origen arriba a la izquierda."""
    return (f'<rect width="{f(w)}" height="{h}" rx="8" fill="{CLOUD}" stroke="{PLUM}" stroke-width="2"/>'
            f'<rect x="12" y="12" width="26" height="14" rx="2" fill="{ORANGE}"/><path d="M38,15 h7 l5,6 v5 h-12 z" fill="{ORANGE}"/>'
            f'<circle cx="18" cy="27" r="4" fill="{PLUM}"/><circle cx="42" cy="27" r="4" fill="{PLUM}"/>'
            f'<rect x="12" y="{h - 22}" width="{f(w * 0.55)}" height="6" rx="3" fill="{PLUM}"/>'
            f'<rect x="12" y="{h - 12}" width="{f(w * 0.35)}" height="4" rx="2" fill="{PLUM_L}"/>')


def scaffolding(x0, x1, top, base):
    o = []
    for x in (x0, x1):
        o.append(f'<rect x="{x - 2}" y="{top}" width="4" height="{base - top}" fill="{PLUM_M}"/>')
    y = base
    while y - 50 >= top:
        o.append(f'<path d="M{x0},{y} L{x1},{y - 50}" stroke="{PLUM_L}" stroke-width="2.5"/>')
        o.append(f'<rect x="{x0 - 6}" y="{y - 52}" width="{x1 - x0 + 12}" height="6" rx="1" fill="{MUSTARD}"/>')
        y -= 50
    return "".join(o)


def crane(mast_x, base, top, jib_left, jib_right, trolley_x):
    o = [f'<rect x="{mast_x - 12}" y="{top}" width="24" height="{base - top}" fill="none" stroke="{ORANGE}" stroke-width="4"/>']
    y = base
    while y - 24 > top:
        o.append(f'<path d="M{mast_x - 12},{y} L{mast_x + 12},{y - 24} M{mast_x + 12},{y - 24} L{mast_x - 12},{y - 48}" stroke="{ORANGE}" stroke-width="2.5"/>')
        y -= 48
    o.append(f'<rect x="{jib_left}" y="{top - 16}" width="{jib_right - jib_left}" height="14" fill="none" stroke="{ORANGE}" stroke-width="3.5"/>')
    x = jib_left
    while x + 28 <= jib_right:
        o.append(f'<path d="M{x},{top - 2} L{x + 14},{top - 16} L{x + 28},{top - 2}" fill="none" stroke="{ORANGE}" stroke-width="2"/>')
        x += 28
    o.append(f'<path d="M{mast_x},{top - 16} L{mast_x},{top - 52} L{jib_left + 30},{top - 16} M{mast_x},{top - 52} L{jib_right - 10},{top - 16}" fill="none" stroke="{PLUM_M}" stroke-width="2"/>')
    o.append(f'<rect x="{jib_right - 36}" y="{top - 2}" width="34" height="30" rx="3" fill="{PLUM_M}"/>')
    o.append(f'<rect x="{mast_x + 12}" y="{top}" width="30" height="24" rx="4" fill="{MUSTARD}"/><rect x="{mast_x + 18}" y="{top + 5}" width="18" height="10" rx="2" fill="{SEA_L}"/>')
    o.append(f'<rect x="{trolley_x - 10}" y="{top - 2}" width="20" height="8" rx="2" fill="{PLUM}"/>')
    return "".join(o)


def hero():
    W, H = 1600, 1000
    rng = random.Random(7)
    b = [sky("hero-sky", W, H, [(0, SKY_TOP), (0.42, SKY_MID), (0.62, SKY_LOW)])]
    b.append(f'<circle cx="1260" cy="430" r="66" fill="{CLOUD}" opacity=".9"/>')
    b.append(dots(rng, 12, (0, 40, W, 380), 3, 8, [CLOUD]))
    b.append(cloud(60, 120, 1.3, CLOUD, ' class="drift"'))
    b.append(cloud(1300, 90, 1.5, CLOUD, ' class="drift slow"'))
    b.append(cloud(330, 330, 0.8, PEACH, ' class="drift slow"'))
    b.append(cloud(-40, 440, 1.0, CLOUD, ' class="drift slow"'))
    b.append(cloud(1420, 380, 1.1, PEACH, ' class="drift"'))
    b.append(birds(1240, 220, 1.2, PLUM, ' class="hero-birds"'))
    b.append(mountains([(0, 640), (120, 560), (230, 600), (360, 480), (470, 560), (560, 520), (660, 600), (760, 540),
                        (880, 470), (990, 560), (1080, 500), (1200, 590), (1320, 470), (1450, 560), (1600, 520)],
                       700, LILAC, LILAC_D, SNOW))
    b.append(hill([(0, 640), (260, 610), (520, 660), (800, 630), (1100, 650), (1380, 600), (1600, 640)], G_MID))
    for x in range(20, 1600, 46):
        if 470 < x < 1130:
            continue
        b.append(conifer(x + rng.uniform(-10, 10), 680 + rng.uniform(-24, 10), rng.uniform(40, 70)))
    b.append(hill([(0, 720), (300, 690), (640, 700), (900, 680), (1200, 710), (1600, 680)], G_MID2))
    # los negocios del pueblo, a los lados
    b.append(house(170, 716, 54, 46, WALL, ROOF))
    b.append(church(236, 718, 0.9))
    b.append(restaurant(280, 730, 0.95))
    b.append(cypress(460, 744, 96))
    b.append(workshop(1170, 732, 0.92))
    b.append(warehouse(1340, 736, 0.85))
    b.append(cypress(1150, 748, 86))
    b.append(round_tree(1500, 766, 22))
    b.append(hill([(0, 790), (250, 760), (500, 775), (800, 760), (1100, 780), (1350, 750), (1600, 780)], G_LIGHT))
    for x in (90, 180, 1440, 1530):
        b.append(conifer(x, 800 + rng.uniform(-10, 10), rng.uniform(90, 130), G_DARK, G_MID2))
    b.append(flowers(rng, 150, (0, 800, W, 1000)))
    # la carretera lleva a la web
    rd, center = road([(760, 1030), (835, 970), (790, 925), (800, 892)], 160, 44, steps=18)
    b.append(rd)
    # la web en construcción: andamio, ventana y grúa
    bx, by, bw, bh = 560, 626, 480, 270
    b.append(scaffolding(522, 548, by + 40, by + bh + 4))
    site, (sx, sy, sw, sh) = browser_site(bx, by, bw, bh)
    b.append(site)
    trolley = sx + sw / 2
    b.append(crane(1100, by + bh + 4, 606, int(sx - 10), 1230, round(trolley)))
    # la grúa baja la última pieza a su hueco
    drop = 120
    b.append(f'<line x1="{f(trolley)}" y1="612" x2="{f(trolley)}" y2="{f(sy - 14)}" stroke="{PLUM}" stroke-width="2">'
             f'<animate attributeName="y2" values="{f(sy - 14 - drop)};{f(sy - 14)};{f(sy - 14)}" keyTimes="0;0.55;1" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1;0 0 1 1"/></line>')
    b.append(f'<g><animateTransform attributeName="transform" type="translate" values="0,{-drop};0,0;0,0" keyTimes="0;0.55;1" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1;0 0 1 1"/>'
             f'<path d="M{f(trolley - 14)},{f(sy)} L{f(trolley)},{f(sy - 14)} L{f(trolley + 14)},{f(sy)}" fill="none" stroke="{PLUM}" stroke-width="2"/>'
             f'<g transform="translate({f(sx)},{f(sy)})">{transport_card(sw, sh)}</g></g>')
    # primer plano: crema del papel para fundirse con la página
    b.append(hill([(0, 960), (300, 940), (700, 975), (1000, 950), (1300, 935), (1600, 960)], CREAM))
    for x, s in ((150, 1.4), (230, 1.0), (1380, 1.2), (1470, 1.5)):
        b.append(poppy(x, 990, s))
    # la furgoneta llega con lo que nos cuentas
    b.append(
        '<g class="hero-van">'
        f'<animateMotion dur="9s" repeatCount="indefinite" rotate="0" path="{center}" keyTimes="0;1" keyPoints="0;1" calcMode="linear"/>'
        '<g><animateTransform attributeName="transform" type="scale" values="0.95;0.32" keyTimes="0;1" dur="9s" repeatCount="indefinite" calcMode="spline" keySplines="0.2 0.6 0.4 1"/>'
        + van_back() + '</g>'
        '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.08;0.85;1" dur="9s" repeatCount="indefinite"/>'
        '</g>')
    return svg(W, H, "".join(b), cls="hero-svg",
               extra_attrs=' preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false"')


def meeting():
    W, H = 600, 450
    rng = random.Random(3)
    b = [sky("m-sky", W, H, [(0, "#F6E7CB"), (1, "#FBF4E4")])]
    b.append(f'<circle cx="470" cy="110" r="44" fill="{PEACH}"/>')
    b.append(cloud(30, 70, 0.8, PEACH, ' class="drift"'))
    b.append(cloud(330, 140, 0.6, CLOUD, ' class="drift slow"'))
    b.append(dots(rng, 10, (0, 20, W, 180), 3, 8, [PEACH, CLOUD]))
    b.append(hill([(0, 250), (150, 220), (320, 240), (460, 210), (600, 235)], LILAC))
    b.append(hill([(0, 280), (200, 260), (400, 275), (600, 255)], G_MID))
    b.append(cypress(70, 300, 120))
    b.append(cypress(100, 302, 80))
    b.append(cypress(540, 300, 130))
    # suelo de terraza
    b.append(f'<rect x="0" y="300" width="{W}" height="150" fill="#E9C9A0"/>')
    for i in range(7):
        b.append(f'<path d="M{f(-200 + i * 140)},450 L{f(150 + i * 50)},300" stroke="#DDB98C" stroke-width="3"/>')
    # sombrilla
    b.append(f'<rect x="296" y="96" width="8" height="250" fill="{PLUM_M}"/>')
    b.append(f'<path d="M140,150 Q300,40 460,150 Z" fill="{ORANGE}"/>')
    for i in range(4):
        b.append(f'<path d="M{f(140 + i * 80)},150 Q{f(180 + i * 80)},120 {f(220 + i * 80)},150 Z" fill="{CREAM if i % 2 else POPPY}"/>')
    # sillas
    b.append(f'<rect x="120" y="270" width="14" height="110" rx="4" fill="{PLUM}"/><rect x="110" y="330" width="70" height="12" rx="4" fill="{PLUM}"/><rect x="166" y="336" width="10" height="60" fill="{PLUM}"/>')
    b.append(f'<rect x="466" y="270" width="14" height="110" rx="4" fill="{PLUM}"/><rect x="420" y="330" width="70" height="12" rx="4" fill="{PLUM}"/><rect x="424" y="336" width="10" height="60" fill="{PLUM}"/>')
    # mesa
    b.append(f'<rect x="290" y="300" width="20" height="120" fill="{PLUM_M}"/><ellipse cx="300" cy="420" rx="60" ry="10" fill="{PLUM_M}"/>')
    b.append(f'<ellipse cx="300" cy="300" rx="170" ry="34" fill="{CREAM}"/><ellipse cx="300" cy="306" rx="170" ry="34" fill="{WALL2}" opacity=".6"/><ellipse cx="300" cy="298" rx="170" ry="32" fill="{CREAM}"/>')
    # tableta con la web
    b.append('<g transform="translate(232,214) rotate(-4)">'
             f'<rect width="140" height="96" rx="10" fill="{PLUM}"/>'
             f'<rect x="8" y="8" width="124" height="80" rx="4" fill="{CREAM}"/>'
             f'<rect x="8" y="8" width="124" height="34" rx="4" fill="{SEA_L}"/>'
             f'<path d="M8,42 Q40,26 70,36 T132,30 V42 Z" fill="{G_MID}"/>'
             f'<rect x="14" y="48" width="50" height="6" rx="3" fill="{PLUM}"/>'
             f'<rect x="14" y="58" width="34" height="4" rx="2" fill="{PLUM_L}"/>'
             f'<rect x="14" y="70" width="34" height="11" rx="5.5" fill="{RED}"/>'
             f'<rect x="80" y="50" width="22" height="30" rx="3" fill="{PEACH}"/><rect x="106" y="50" width="22" height="30" rx="3" fill="{G_LIGHT}"/>'
             '</g>')
    b.append(f'<rect x="352" y="288" width="78" height="10" rx="3" fill="{PLUM_M}" opacity=".18"/>')
    # tazas
    for cx in (190, 420):
        b.append(f'<ellipse cx="{cx}" cy="300" rx="22" ry="6" fill="{WALL2}"/>'
                 f'<path d="M{cx - 14},274 h28 v14 a14,12 0 0 1 -28,0 z" fill="{RED if cx < 300 else BLUE_CAR}"/>'
                 f'<path d="M{cx + 14},278 a7,7 0 0 1 0,12" fill="none" stroke="{RED if cx < 300 else BLUE_CAR}" stroke-width="4"/>'
                 f'<path d="M{cx - 4},262 q-6,-8 0,-16 M{cx + 5},262 q-6,-8 0,-16" fill="none" stroke="{CREAM}" stroke-width="3" stroke-linecap="round"/>')
    # maceta
    b.append(f'<path d="M548,450 l8,-56 h40 l8,56 z" fill="{ROOF}"/>'
             f'<circle cx="566" cy="380" r="22" fill="{G_DARK}"/><circle cx="590" cy="372" r="18" fill="{G_MID2}"/><circle cx="578" cy="356" r="16" fill="{G_DARK}"/>')
    return svg(W, H, "".join(b), style=DRIFT_CSS)


def cover_restaurante():
    W, H = 600, 800
    rng = random.Random(11)
    b = [sky("cr-sky", W, H, [(0, "#F6E7CB"), (0.5, "#FBEBD6"), (1, "#FBF4E4")])]
    b.append(dots(rng, 10, (0, 30, W, 330), 3, 9, [PEACH, PEACH_D]))
    b.append(cloud(-70, 340, 0.9, PEACH, ' class="drift"'))
    b.append(cloud(470, 320, 0.8, PEACH, ' class="drift slow"'))
    b.append(birds(80, 360, 0.8, PLUM))
    b.append(hill([(0, 430), (140, 400), (300, 420), (450, 380), (600, 410)], LILAC))
    b.append(hill([(0, 470), (180, 440), (360, 455), (600, 430)], G_MID))
    for i, x in enumerate((60, 140, 220, 300, 380)):
        b.append(house(x, 470 + (i % 2) * 8, 46, 32, WALL if i % 2 else WALL2, ROOF))
    b.append(church(450, 470, 0.7))
    # fachada del restaurante
    b.append(f'<rect x="250" y="440" width="350" height="250" fill="#F2D7B0"/>')
    b.append(f'<rect x="250" y="430" width="350" height="16" fill="{ROOF}"/>')
    for x in (280, 380, 480):
        b.append(f'<path d="M{x},690 v-110 a40,40 0 0 1 80,0 v110 z" fill="{PLUM_M}"/>'
                 f'<path d="M{x + 8},690 v-104 a32,32 0 0 1 64,0 v104 z" fill="#3B3550"/>'
                 f'<rect x="{x + 14}" y="610" width="52" height="34" rx="4" fill="{MUSTARD}" opacity=".85"/>')
    b.append("".join(f'<rect x="{250 + i * 35}" y="520" width="35" height="22" fill="{RED if i % 2 == 0 else CREAM}"/>' for i in range(10)))
    b.append("".join(f'<circle cx="{267.5 + i * 35}" cy="542" r="17.5" fill="{RED if i % 2 == 0 else CREAM}"/>' for i in range(10)))
    b.append(f'<rect x="330" y="470" width="190" height="34" rx="6" fill="{PLUM}"/>'
             f'<circle cx="372" cy="487" r="9" fill="{CREAM}"/><rect x="390" y="482" width="110" height="10" rx="5" fill="{CREAM}"/>')
    # guirnalda de luces
    b.append(f'<path d="M0,380 Q150,440 300,410 T600,420" fill="none" stroke="{PLUM}" stroke-width="2"/>')
    for t in range(1, 12):
        x = t * 50
        y = 380 + 40 * math.sin(math.pi * x / 300) * (1 if x < 300 else 0.4) + (0 if x < 300 else 20)
        b.append(f'<circle cx="{x}" cy="{f(y + 6)}" r="6" fill="{MUSTARD}"/>')
    b.append(cypress(200, 700, 260))
    b.append(cypress(150, 700, 180))
    # suelo
    b.append(f'<rect x="0" y="690" width="{W}" height="110" fill="#E9C9A0"/>')
    for i in range(9):
        b.append(f'<path d="M{-300 + i * 120},800 L{60 + i * 60},690" stroke="#DDB98C" stroke-width="3"/>')
    # mesas con sombrillas
    for x, c in ((110, ORANGE), (420, RED)):
        b.append(f'<rect x="{x - 3}" y="560" width="6" height="190" fill="{PLUM}"/>'
                 f'<path d="M{x - 90},600 Q{x},530 {x + 90},600 Z" fill="{c}"/>'
                 f'<path d="M{x - 30},600 Q{x},585 {x + 30},600 Z" fill="{CREAM}"/>'
                 f'<ellipse cx="{x}" cy="720" rx="64" ry="14" fill="{CREAM}"/>'
                 f'<rect x="{x - 4}" y="720" width="8" height="60" fill="{PLUM_M}"/>'
                 f'<path d="M{x - 26},700 h12 l-2,14 h-8 z M{x + 14},700 h12 l-2,14 h-8 z" fill="{RED}" opacity=".85"/>'
                 f'<rect x="{x - 21}" y="714" width="2" height="8" fill="{PLUM}"/><rect x="{x + 19}" y="714" width="2" height="8" fill="{PLUM}"/>')
    b.append(f'<path d="M520,800 l10,-70 h50 l10,70 z" fill="{ROOF}"/><circle cx="545" cy="716" r="28" fill="{G_DARK}"/><circle cx="572" cy="704" r="22" fill="{G_MID2}"/>')
    return svg(W, H, "".join(b), style=DRIFT_CSS)


def cover_taller():
    W, H = 600, 800
    rng = random.Random(5)
    b = [sky("ct-sky", W, H, [(0, SKY_TOP), (0.45, SKY_MID), (0.7, SKY_LOW)])]
    b.append(dots(rng, 8, (0, 30, W, 300), 3, 8, [CLOUD]))
    b.append(cloud(-80, 330, 0.85, CLOUD, ' class="drift"'))
    b.append(cloud(500, 410, 0.6, CLOUD, ' class="drift slow"'))
    b.append(birds(430, 330, 0.9, PLUM))
    b.append(mountains([(0, 440), (90, 360), (180, 410), (290, 330), (390, 420), (480, 350), (600, 410)], 500, LILAC, LILAC_D, SNOW))
    b.append(hill([(0, 470), (200, 450), (400, 470), (600, 440)], G_MID))
    for x in range(10, 600, 40):
        b.append(conifer(x + rng.uniform(-8, 8), 500 + rng.uniform(-14, 6), rng.uniform(34, 56)))
    b.append(hill([(0, 540), (220, 510), (420, 530), (600, 505)], G_MID2))
    # taller
    b.append(workshop(330, 600, 1.35))
    b.append(cypress(310, 610, 130))
    # carretera
    rd, _ = road([(-40, 810), (180, 720), (360, 650), (520, 620), (640, 600)], 170, 40)
    b.append(rd)
    b.append(f'<path d="M0,790 Q260,690 640,605" fill="none" stroke="{CREAM}" stroke-width="5" opacity=".0"/>')
    b.append(hill([(0, 820), (600, 820)], G_LIGHT))
    b.append('<g transform="translate(220,742) rotate(-17) scale(0.9)">' + car_side() + '</g>')
    b.append(flowers(rng, 40, (380, 680, 600, 800)))
    b.append(hill([(330, 800), (450, 730), (600, 700)], G_LIGHT))
    b.append(flowers(rng, 50, (400, 720, 600, 800)))
    for x, s in ((470, 1.1), (540, 1.4), (590, 1.0)):
        b.append(poppy(x, 805, s))
    return svg(W, H, "".join(b), style=DRIFT_CSS)


def cover_transporte():
    W, H = 600, 800
    rng = random.Random(9)
    b = [sky("cx-sky", W, H, [(0, "#C9C3E8"), (0.4, "#E4E0F3"), (0.65, "#FBF4E4")])]
    b.append(dots(rng, 8, (0, 30, W, 300), 3, 8, [LILAC_L, CLOUD]))
    b.append(cloud(-70, 330, 0.9, LILAC_L, ' class="drift"'))
    b.append(cloud(480, 320, 0.75, CLOUD, ' class="drift slow"'))
    b.append(birds(90, 340, 0.8, PLUM))
    b.append(hill([(0, 400), (200, 380), (420, 410), (600, 385)], LILAC))
    b.append(f'<rect x="0" y="430" width="{W}" height="140" fill="{SEA}"/>')
    for i in range(10):
        y = 445 + i * 13
        b.append(f'<rect x="{rng.uniform(0, 520)}" y="{y}" width="{rng.uniform(30, 90)}" height="3" rx="1.5" fill="{SEA_L}"/>')
    b.append(hill([(-10, 440), (110, 430), (200, 480), (250, 640)], G_MID))
    # acantilado
    b.append(hill([(180, 640), (300, 460), (430, 370), (610, 330)], MUSTARD))
    b.append(hill([(260, 660), (370, 500), (480, 440), (610, 415)], ORANGE))
    b.append(dots(rng, 40, (360, 420, 600, 600), 2, 5, [PLUM_M, G_DARK]))
    b.append(hill([(0, 600), (150, 580), (300, 610), (600, 560)], G_MID2))
    rd, _ = road([(640, 690), (420, 650), (240, 640), (60, 600), (-40, 590)], 170, 60)
    b.append(rd)
    # quitamiedos
    b.append(f'<path d="M640,740 Q400,700 220,700 T-40,650" fill="none" stroke="{CREAM}" stroke-width="6"/>')
    for x in range(0, 620, 40):
        y = 740 - (640 - x) * 0.06 - (x < 300) * (300 - x) * 0.12
        b.append(f'<rect x="{x}" y="{f(y - 2)}" width="5" height="24" fill="{PLUM_M}"/>')
    b.append('<g transform="translate(300,662) rotate(4) scale(0.95)">' + van_side(RED) + '</g>')
    b.append(hill([(0, 760), (300, 740), (600, 770)], G_LIGHT))
    b.append(flowers(rng, 60, (0, 750, 600, 800)))
    for x, s in ((40, 1.2), (110, 1.5), (520, 1.3), (580, 1.0)):
        b.append(poppy(x, 812, s))
    return svg(W, H, "".join(b), style=DRIFT_CSS)


def sunset():
    W, H = 1600, 700
    rng = random.Random(21)
    b = [sky("ss-sky", W, H, [(0, "#F6D9B8"), (0.45, "#F2B48E"), (0.75, "#E9895A")])]
    b.append(f'<circle cx="800" cy="470" r="230" fill="#FCE3B0" opacity=".45"/>')
    b.append(f'<rect x="610" y="330" width="380" height="250" rx="22" fill="#FCE3B0"/>'
             f'<rect x="610" y="330" width="380" height="44" rx="22" fill="#F9D58E"/><rect x="610" y="352" width="380" height="22" fill="#F9D58E"/>'
             '<circle cx="640" cy="352" r="7" fill="#E9895A"/><circle cx="662" cy="352" r="7" fill="#EDB84E"/><circle cx="684" cy="352" r="7" fill="#A6CB72"/>'
             '<rect x="708" y="343" width="250" height="18" rx="9" fill="#FCE3B0"/>'
             '<circle cx="800" cy="418" r="36" fill="#E9895A"/><path d="M783,419 l11,11 l23,-25" stroke="#FCE3B0" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(dots(rng, 20, (0, 30, W, 300), 4, 12, ["#F9E6CC", PEACH]))
    b.append(cloud(80, 160, 1.2, "#F9E6CC", ' class="drift"'))
    b.append(cloud(1250, 120, 1.4, "#F9E6CC", ' class="drift slow"'))
    b.append(cloud(1000, 300, 0.8, PEACH, ' class="drift"'))
    b.append(birds(1080, 220, 1.1, PLUM))
    b.append(hill([(0, 480), (250, 430), (520, 470), (800, 440), (1100, 470), (1350, 420), (1600, 460)], "#B48AA8"))
    b.append(hill([(0, 540), (300, 500), (640, 530), (960, 505), (1280, 540), (1600, 500)], "#8E6F9E"))
    for x in range(30, 1600, 60):
        if 620 < x < 980:
            continue
        b.append(cypress(x + rng.uniform(-12, 12), 560 + rng.uniform(-14, 10), rng.uniform(60, 110), "#5B4B6E", "#6E5A80"))
    # luces del pueblo
    for _ in range(26):
        b.append(f'<rect x="{f(rng.uniform(640, 960))}" y="{f(rng.uniform(510, 560))}" width="6" height="8" rx="1" fill="#FCE3B0"/>')
    b.append(hill([(0, 600), (360, 570), (800, 590), (1200, 565), (1600, 600)], "#6E5480"))
    b.append(hill([(0, 670), (400, 650), (800, 675), (1200, 645), (1600, 670)], "#33283B"))
    return svg(W, H, "".join(b), extra_attrs=' preserveAspectRatio="xMidYMax slice"', style=DRIFT_CSS)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "meeting.svg": meeting(),
        "cover-restaurante.svg": cover_restaurante(),
        "cover-taller.svg": cover_taller(),
        "cover-transporte.svg": cover_transporte(),
        "sunset.svg": sunset(),
    }
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
