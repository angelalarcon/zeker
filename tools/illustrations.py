"""Ilustraciones del sitio en estilo póster de viaje: formas planas con luz desde arriba a la izquierda,
sombras lavanda, crestas iluminadas, montañas facetadas, punteado y nubes en dos tonos.

Cada escena se genera por capas (cielo, fondo, medio, escena, primer plano) para poder animarlas con
parallax. Ejecuta `python3 tools/illustrations.py` desde la raíz del repo: escribe
assets/illustrations/<escena>-<n>-<capa>.svg e inserta el hero (en capas <g data-depth>) en index.html
entre los marcadores HERO-SVG."""

import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "illustrations"

# ---------- paleta ----------
SKY_TOP, SKY_MID, SKY_LOW = "#6F9FD8", "#A9CBEA", "#F1E4C8"
CREAM, CLOUD, CLOUD_SH = "#FBF4E4", "#FFF8EA", "#EBD9C6"
PEACH, PEACH_D, PEACH_SH = "#F2C3A7", "#E9A88A", "#DDA088"
LILAC_L, LILAC, LILAC_D, LILAC_DD = "#D6D1EE", "#B8B2DD", "#9289C2", "#7569A8"
SNOW, SNOW_SH = "#FBF9FD", "#D9D3EE"
PLUM, PLUM_M, PLUM_L = "#42344A", "#5B4B66", "#7A6788"
G_PALE, G_LIGHT, G_MID, G_MID2, G_DARK, G_DEEP = "#E4EBA3", "#D3E28F", "#A6CB72", "#82B862", "#4F9460", "#2F6B47"
G_SH = "#7FAF6E"  # sombra de colina: verde algo más frío
G_SH2 = "#6E9F63"
MUSTARD, MUSTARD_D, ORANGE, RED, POPPY = "#EDB84E", "#D99A36", "#E8743B", "#D9483B", "#F08A2C"
ROAD, ROAD_L, LINE = "#6E6178", "#857895", "#F7EEDC"
SEA, SEA_D, SEA_L = "#5F9BD6", "#4A82C2", "#9CC3E8"
ROOF, ROOF_D, WALL, WALL_SH, WALL2 = "#C9573A", "#A8432E", "#F6E7CB", "#E2C9A6", "#E9D3AE"
BLUE_CAR, BLUE_CAR_D, DARK = "#5E8FD6", "#46729F", "#2E2638"


def f(n):
    return f"{n:.1f}".rstrip("0").rstrip(".")


# ---------- defs por archivo ----------

class Defs:
    """Acumula <defs> (degradados, clipPaths) de la capa que se está dibujando."""

    def __init__(self, prefix):
        self.prefix, self.items, self.n = prefix, [], 0

    def uid(self, kind):
        self.n += 1
        return f"{self.prefix}{kind}{self.n}"

    def add(self, item):
        self.items.append(item)

    def render(self):
        return f"<defs>{''.join(self.items)}</defs>" if self.items else ""


D = Defs("x")


def new_defs(prefix):
    global D
    D = Defs(prefix)
    return D


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
            out.append(tuple(
                0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                       + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    out.append(points[-1])
    return out


def poly_d(pts, close=True):
    d = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts)
    return d + (" Z" if close else "")


def y_at(curve, x):
    """Altura de una curva muestreada en x (interpolación lineal)."""
    for (x0, y0), (x1, y1) in zip(curve, curve[1:]):
        if x0 <= x <= x1 or x1 <= x <= x0:
            t = 0 if x1 == x0 else (x - x0) / (x1 - x0)
            return y0 + (y1 - y0) * t
    return curve[0][1] if x < curve[0][0] else curve[-1][1]


def clip(d):
    cid = D.uid("c")
    D.add(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
    return cid


def lin_grad(stops, vertical=True):
    gid = D.uid("g")
    x2, y2 = ("0", "1") if vertical else ("1", "0")
    st = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else "") + "/>"
                 for o, c, a in [(s + (None,))[:3] for s in stops])
    D.add(f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}">{st}</linearGradient>')
    return gid


def rad_grad(stops):
    gid = D.uid("r")
    st = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    D.add(f'<radialGradient id="{gid}">{st}</radialGradient>')
    return gid


# ---------- paisaje ----------

def sky(w, h, stops):
    return f'<rect width="{w}" height="{h}" fill="url(#{lin_grad(stops)})"/>'


def sun_glow(x, y, r, color=CLOUD, core=None):
    g = rad_grad([(0, color, 0.85), (0.35, color, 0.35), (1, color, 0)])
    out = f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * 3.2)}" fill="url(#{g})"/>'
    return out + f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{core or color}"/>'


CLOUD_SHAPE = [(0, 0, 34), (40, -24, 46), (94, -10, 38), (132, 6, 26), (-32, 10, 22), (66, 8, 30)]


def cloud(x, y, s=1.0, light=CLOUD, shade=CLOUD_SH, extra=""):
    """Cúmulo de base plana: parte alta iluminada y franja inferior en sombra."""
    circles = "".join(f'<circle cx="{f(x + cx * s)}" cy="{f(y + cy * s)}" r="{f(r * s)}"/>' for cx, cy, r in CLOUD_SHAPE)
    base = f'<rect x="{f(x - 54 * s)}" y="{f(y + 4 * s)}" width="{f(212 * s)}" height="{f(30 * s)}" rx="{f(15 * s)}"/>'
    cid = D.uid("k")
    D.add(f'<clipPath id="{cid}">{circles}{base}</clipPath>')
    return (f'<g{extra}><g fill="{light}">{circles}{base}</g>'
            f'<g clip-path="url(#{cid})"><path d="M{f(x - 60 * s)},{f(y + 14 * s)} q{f(70 * s)},{f(-12 * s)} {f(140 * s)},{f(-4 * s)} '
            f't{f(90 * s)},{f(6 * s)} V{f(y + 40 * s)} H{f(x - 60 * s)} Z" fill="{shade}"/>'
            f'<circle cx="{f(x + 30 * s)}" cy="{f(y - 30 * s)}" r="{f(16 * s)}" fill="#FFFFFF" opacity=".45"/></g></g>')


def puffs(rng, n, box, colors, rmin=3, rmax=9):
    x0, y0, x1, y1 = box
    return "".join(f'<circle cx="{f(rng.uniform(x0, x1))}" cy="{f(rng.uniform(y0, y1))}" r="{f(rng.uniform(rmin, rmax))}" fill="{rng.choice(colors)}"/>'
                   for _ in range(n))


def lit_hill(points, base, light, shadow, rng, rim=9, folds=0, stipple=None, dapple=None, bottom=2000, extra=""):
    """Colina con cresta iluminada, pliegues de sombra diagonales y textura opcional.
    stipple=(color, n, rmin, rmax); dapple=[(color, n), ...] manchas sueltas."""
    curve = catmull(points, 14)
    d = poly_d([(curve[0][0], bottom)] + curve + [(curve[-1][0], bottom)])
    cid = clip(d)
    xs = [p[0] for p in curve]
    x0, x1 = min(xs), max(xs)
    top = min(p[1] for p in curve)
    o = [f'<path d="{d}" fill="{light}"/>',
         f'<path d="{d}" fill="{base}" transform="translate({f(rim * 0.35)},{f(rim)})"/>']
    tries = 0
    made = 0
    while made < folds and tries < folds * 20:
        tries += 1
        fx = rng.uniform(x0, x1)
        if y_at(curve, fx + 12) - y_at(curve, fx - 12) < 1.5:  # solo laderas en sombra (bajan hacia la derecha)
            continue
        made += 1
        fy = y_at(curve, fx) + rim * 0.5
        w = rng.uniform(26, 80)
        drop = rng.uniform(50, 170)
        o.append(f'<path d="M{f(fx)},{f(fy)} C{f(fx + w * 0.6)},{f(fy + drop * 0.2)} {f(fx + w * 0.95)},{f(fy + drop * 0.55)} '
                 f'{f(fx + w)},{f(fy + drop)} C{f(fx + w * 0.55)},{f(fy + drop * 0.7)} {f(fx + w * 0.2)},{f(fy + drop * 0.35)} {f(fx)},{f(fy)} Z" fill="{shadow}"/>')
    if dapple:
        for color, n in dapple:
            for _ in range(n):
                cx = rng.uniform(x0, x1)
                cy = rng.uniform(y_at(curve, cx) + rim, y_at(curve, cx) + 320)
                rx, ry = rng.uniform(3, 10), rng.uniform(1.6, 3.6)
                o.append(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" transform="rotate({f(rng.uniform(-35, 10))} {f(cx)} {f(cy)})" fill="{color}"/>')
    if stipple:
        color, n, rmin, rmax = stipple
        for _ in range(n):
            cx = rng.uniform(x0, x1)
            cy = rng.uniform(y_at(curve, cx) + rim * 1.5, max(y_at(curve, cx) + rim * 2, top + 420))
            o.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(rng.uniform(rmin, rmax))}" fill="{color}"/>')
    return f'<g clip-path="url(#{cid})"{extra}>' + "".join(o) + "</g>"


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def mountain(rng, lv, peak, rv, base, light=LILAC, shadow=LILAC_D, deep=LILAC_DD, snow=SNOW, snow_sh=SNOW_SH, snow_t=0.32):
    """Una montaña facetada: cara izquierda iluminada, cara derecha en sombra separada por una arista
    quebrada, y casquete de nieve dentado con su propia mitad en sombra."""
    px, py = peak
    # arista que baja desde la cumbre
    arista, x, y = [peak], px, py
    while y < base:
        y = min(base, y + rng.uniform(28, 46))
        x += rng.uniform(-4, 16)
        arista.append((x, y))
    o = [f'<path d="{poly_d([(lv[0], base), lv, peak, rv, (rv[0], base)])}" fill="{light}"/>',
         f'<path d="{poly_d([peak, rv, (rv[0], base)] + arista[::-1])}" fill="{shadow}"/>']
    for _ in range(2):  # canales oscuros en la cara de sombra
        t = rng.uniform(0.25, 0.6)
        a = lerp(peak, rv, t)
        o.append(f'<path d="M{f(a[0])},{f(a[1])} l{f(rng.uniform(-14, -4))},{f(rng.uniform(40, 90))} l{f(rng.uniform(6, 12))},{f(rng.uniform(-20, -8))} z" fill="{deep}"/>')
    for _ in range(2):  # grietas iluminadas en la cara de luz
        t = rng.uniform(0.3, 0.7)
        a = lerp(peak, lv, t)
        o.append(f'<path d="M{f(a[0])},{f(a[1])} l{f(rng.uniform(6, 16))},{f(rng.uniform(30, 70))} l{f(rng.uniform(-4, 2))},{f(rng.uniform(-24, -10))} z" fill="{shadow}" opacity=".55"/>')
    # nieve
    lpt, rpt = lerp(peak, lv, snow_t), lerp(peak, rv, snow_t * 0.9)
    k = next((i for i, a in enumerate(arista) if a[1] >= lpt[1]), len(arista) - 1)
    apt = arista[k]
    teeth_l = []
    for i in range(1, 4):
        q = lerp(lpt, apt, i / 4)
        teeth_l.append((q[0], q[1] + (rng.uniform(-14, -6) if i % 2 else rng.uniform(4, 12))))
    teeth_r = []
    for i in range(1, 3):
        q = lerp(apt, rpt, i / 3)
        teeth_r.append((q[0], q[1] + (rng.uniform(-12, -4) if i % 2 else rng.uniform(4, 10))))
    o.append(f'<path d="{poly_d([peak, lpt] + teeth_l + arista[1:k + 1][::-1])}" fill="{snow}"/>')
    o.append(f'<path d="{poly_d([peak] + arista[1:k + 1] + teeth_r + [rpt])}" fill="{snow_sh}"/>')
    return "".join(o)


def mountain_range(rng, x0, x1, base, peaks, jag=1.0, **kw):
    """Cordillera: montañas facetadas solapadas, de la más lejana (alta) a la más cercana."""
    order = sorted(peaks, key=lambda p: p[1])
    o = []
    for px, py in order:
        hgt = base - py
        wl = hgt * rng.uniform(0.9, 1.3) * jag ** 0.3
        wr = hgt * rng.uniform(1.0, 1.4) * jag ** 0.3
        o.append(mountain(rng, (max(x0, px - wl), base - hgt * rng.uniform(0.0, 0.15)), (px, py),
                          (min(x1, px + wr), base - hgt * rng.uniform(0.0, 0.15)), base, **kw))
    return "".join(o)


def conifer(x, y, h, light=G_DARK, dark=G_DEEP, tiers=3):
    """Abeto de varios pisos: mitad iluminada y mitad en sombra."""
    w = h * 0.36
    o = []
    for i in range(tiers):
        t = i / tiers
        ty = y - h + h * t * 0.78
        tw = w * (0.55 + 0.45 * (i + 1) / tiers)
        by = ty + h * (0.42 + 0.1 * (i == tiers - 1))
        o.append(f'<path d="M{f(x)},{f(ty)} L{f(x - tw)},{f(by)} Q{f(x - tw * 0.4)},{f(by - h * 0.04)} {f(x)},{f(by + h * 0.02)} Z" fill="{light}"/>')
        o.append(f'<path d="M{f(x)},{f(ty)} L{f(x + tw)},{f(by)} Q{f(x + tw * 0.4)},{f(by - h * 0.04)} {f(x)},{f(by + h * 0.02)} Z" fill="{dark}"/>')
    return "".join(o)


def forest(rng, x0, x1, y_fn, hmin, hmax, spacing, light=G_DARK, dark=G_DEEP, skip=None):
    trees = []
    x = x0
    while x < x1:
        if not (skip and skip[0] < x < skip[1]):
            trees.append((x + rng.uniform(-spacing * 0.3, spacing * 0.3), y_fn(x) + rng.uniform(-6, 10), rng.uniform(hmin, hmax)))
        x += spacing * rng.uniform(0.6, 1.1)
    trees.sort(key=lambda t: t[1])
    return "".join(conifer(tx, ty, th, light, dark) for tx, ty, th in trees)


def cypress(x, y, h, dark=PLUM_M, light=PLUM_L):
    w = h * 0.15
    o = (f'<path d="M{f(x)},{f(y - h)} C{f(x - w * 1.7)},{f(y - h * 0.6)} {f(x - w * 1.3)},{f(y)} {f(x)},{f(y)} Z" fill="{light}"/>'
         f'<path d="M{f(x)},{f(y - h)} C{f(x + w * 1.7)},{f(y - h * 0.6)} {f(x + w * 1.3)},{f(y)} {f(x)},{f(y)} Z" fill="{dark}"/>')
    for k in range(3):  # trazos de ramas
        ky = y - h * (0.25 + k * 0.2)
        o += f'<path d="M{f(x - w * 0.2)},{f(ky)} q{f(-w * 0.6)},{f(-h * 0.04)} {f(-w * 0.9)},{f(-h * 0.12)}" stroke="{dark}" stroke-width="{f(max(1.5, w * 0.14))}" fill="none" stroke-linecap="round" opacity=".55"/>'
    return o


def round_tree(x, y, r, dark=G_DARK, light=G_MID2, trunk=PLUM_M):
    return (f'<rect x="{f(x - r * 0.09)}" y="{f(y - r * 0.9)}" width="{f(r * 0.18)}" height="{f(r * 0.9)}" fill="{trunk}"/>'
            f'<circle cx="{f(x)}" cy="{f(y - r * 1.5)}" r="{f(r)}" fill="{dark}"/>'
            f'<circle cx="{f(x - r * 0.25)}" cy="{f(y - r * 1.7)}" r="{f(r * 0.68)}" fill="{light}"/>'
            f'<circle cx="{f(x - r * 0.45)}" cy="{f(y - r * 1.9)}" r="{f(r * 0.25)}" fill="{G_LIGHT}" opacity=".7"/>')


def road(center, w0, w1, color=ROAD, edge=ROAD_L, line=LINE, dash=True, steps=16):
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
    # borde iluminado (lado izquierdo de la calzada)
    out += f'<path d="{poly_d(left, close=False)}" fill="none" stroke="{edge}" stroke-width="{f(max(w0 * 0.05, 2))}" stroke-linecap="round"/>'
    if dash:
        out += (f'<path d="{poly_d(pts, close=False)}" fill="none" stroke="{line}" stroke-width="{f(max(w0 * 0.035, 2))}" '
                f'stroke-dasharray="{f(w0 * 0.18)} {f(w0 * 0.22)}" stroke-linecap="round"/>')
    return out, poly_d(pts, close=False), left, right


def guardrail(edge_pts, every=3, color=CREAM, post=PLUM_M, h=22):
    out = [f'<path d="{poly_d([(x, y - h) for x, y in edge_pts], close=False)}" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round"/>']
    for i, (x, y) in enumerate(edge_pts):
        if i % every == 0:
            out.append(f'<rect x="{f(x - 2.5)}" y="{f(y - h - 2)}" width="5" height="{h + 4}" fill="{post}"/>')
    return "".join(out)


def birds(x, y, s=1.0, color=PLUM, extra=""):
    def b(bx, by, k):
        return (f'<path d="M{f(bx)},{f(by)} q{f(8 * k)},{f(-9 * k)} {f(16 * k)},{f(-1 * k)} q{f(7 * k)},{f(-9 * k)} {f(17 * k)},{f(-3 * k)} '
                f'q{f(-9 * k)},{f(2 * k)} {f(-17 * k)},{f(8 * k)} q{f(-7 * k)},{f(-6 * k)} {f(-16 * k)},{f(-4 * k)} z" fill="{color}"/>')
    return f"<g{extra}>" + b(x, y, s) + b(x + 46 * s, y - 20 * s, s * 0.8) + b(x + 80 * s, y + 6 * s, s * 0.65) + "</g>"


def poppy(x, y, s=1.0, rot=0):
    """Amapola de pétalos en copa, dos tonos, con tallo curvo y hoja."""
    return (f'<g transform="translate({f(x)},{f(y)}) scale({f(s)})">'
            f'<path d="M0,0 q-6,-30 4,-54" stroke="{G_DARK}" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
            f'<path d="M0,-18 q-18,-6 -24,-22 q14,2 24,16" fill="{G_MID2}"/>'
            f'<g transform="translate(4,-60) rotate({f(rot)})">'
            f'<path d="M-20,0 q-4,-22 14,-24 q-2,14 6,24 z" fill="{POPPY}"/>'
            f'<path d="M20,0 q4,-22 -14,-24 q2,14 -6,24 z" fill="{ORANGE}"/>'
            f'<path d="M-14,2 q14,-30 28,0 q-14,12 -28,0 z" fill="{RED}"/>'
            f'<ellipse cx="0" cy="-2" rx="6" ry="4" fill="{PLUM}"/></g></g>')


def meadow_flowers(rng, n, box, colors=(CREAM, "#FFFFFF", PEACH, POPPY, MUSTARD)):
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        r = rng.uniform(2, 5) * (0.5 + (y - y0) / max(y1 - y0, 1))
        c = rng.choice(colors)
        out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{c}"/>')
        if r > 4:
            out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * 0.35)}" fill="{MUSTARD if c != MUSTARD else ORANGE}"/>')
    return "".join(out)


# ---------- edificios (luz desde la izquierda: frente iluminado, costado derecho en sombra) ----------

def house(x, y, w, h, wall=WALL, side=WALL_SH, roof=ROOF, roof_d=ROOF_D, windows=1):
    sd = w * 0.32
    rh = w * 0.4
    o = (f'<path d="M{f(x + w)},{f(y)} V{f(y - h)} L{f(x + w + sd)},{f(y - h - sd * 0.25)} V{f(y - sd * 0.25)} Z" fill="{side}"/>'
         f'<rect x="{f(x)}" y="{f(y - h)}" width="{f(w)}" height="{f(h)}" fill="{wall}"/>'
         f'<path d="M{f(x - w * 0.06)},{f(y - h)} L{f(x + w / 2)},{f(y - h - rh)} L{f(x + w * 1.06)},{f(y - h)} Z" fill="{roof}"/>'
         f'<path d="M{f(x + w / 2)},{f(y - h - rh)} L{f(x + w / 2 + sd)},{f(y - h - rh - sd * 0.25)} L{f(x + w + sd + w * 0.04)},{f(y - h - sd * 0.25)} L{f(x + w * 1.06)},{f(y - h)} Z" fill="{roof_d}"/>')
    for i in range(windows):
        wx = x + w * (0.22 + i * 0.36)
        o += f'<rect x="{f(wx)}" y="{f(y - h * 0.68)}" width="{f(w * 0.16)}" height="{f(h * 0.3)}" rx="{f(w * 0.08)}" fill="{PLUM_M}"/>'
    return o


def church(x, y, s=1.0):
    return (f'<path d="M{f(x + 26 * s)},{f(y)} V{f(y - 110 * s)} l{f(9 * s)},{f(-3 * s)} V{f(y - 3 * s)} Z" fill="{WALL_SH}"/>'
            f'<rect x="{f(x)}" y="{f(y - 110 * s)}" width="{f(26 * s)}" height="{f(110 * s)}" fill="{WALL}"/>'
            f'<path d="M{f(x - 3 * s)},{f(y - 110 * s)} L{f(x + 13 * s)},{f(y - 152 * s)} L{f(x + 13 * s)},{f(y - 110 * s)} Z" fill="{PLUM_L}"/>'
            f'<path d="M{f(x + 13 * s)},{f(y - 152 * s)} L{f(x + 36 * s)},{f(y - 113 * s)} L{f(x + 13 * s)},{f(y - 110 * s)} Z" fill="{PLUM_M}"/>'
            f'<rect x="{f(x + 8 * s)}" y="{f(y - 96 * s)}" width="{f(10 * s)}" height="{f(16 * s)}" rx="{f(5 * s)}" fill="{PLUM_M}"/>')


def awning(x, y, w, n, h, c1=RED, c2=CREAM):
    sw = w / n
    o = []
    for i in range(n):
        c = c1 if i % 2 == 0 else c2
        o.append(f'<path d="M{f(x + i * sw)},{f(y)} h{f(sw)} v{f(h)} a{f(sw / 2)},{f(sw / 2)} 0 0 1 {f(-sw)},0 z" fill="{c}"/>')
    o.append(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h * 0.25)}" fill="#000" opacity=".08"/>')
    return "".join(o)


def restaurant(x, y, s=1.0):
    w, h = 150 * s, 92 * s
    sd = 30 * s
    return (f'<path d="M{f(x + w)},{f(y)} V{f(y - h)} l{f(sd)},{f(-sd * 0.25)} V{f(y - sd * 0.25)} Z" fill="{WALL_SH}"/>'
            f'<rect x="{f(x)}" y="{f(y - h)}" width="{f(w)}" height="{f(h)}" fill="{WALL}"/>'
            f'<path d="M{f(x - 8 * s)},{f(y - h)} h{f(w + 16 * s)} l{f(-14 * s)},{f(-26 * s)} h{f(-w + 12 * s)} z" fill="{ROOF}"/>'
            f'<path d="M{f(x + w + 8 * s)},{f(y - h)} l{f(sd)},{f(-sd * 0.25)} l{f(-14 * s)},{f(-24 * s)} l{f(-sd + 0)},{f(sd * 0.1)} z" fill="{ROOF_D}"/>'
            f'<path d="M{f(x + 12 * s)},{f(y)} v{f(-h * 0.34)} a{f(15 * s)},{f(15 * s)} 0 0 1 {f(30 * s)},0 v{f(h * 0.34)} z" fill="{PLUM_M}"/>'
            f'<rect x="{f(x + 56 * s)}" y="{f(y - h * 0.42)}" width="{f(38 * s)}" height="{f(h * 0.3)}" rx="{f(3 * s)}" fill="{SEA_L}"/>'
            f'<path d="M{f(x + 56 * s)},{f(y - h * 0.12)} l{f(38 * s)},{f(-h * 0.3)} v{f(h * 0.12)} l{f(-26 * s)},{f(h * 0.18)} z" fill="#FFFFFF" opacity=".35"/>'
            f'<path d="M{f(x + 106 * s)},{f(y)} v{f(-h * 0.34)} a{f(15 * s)},{f(15 * s)} 0 0 1 {f(30 * s)},0 v{f(h * 0.34)} z" fill="{PLUM_M}"/>'
            + awning(x, y - h * 0.62, w, 8, 16 * s) +
            f'<rect x="{f(x + w * 0.25)}" y="{f(y - h * 0.92)}" width="{f(w * 0.5)}" height="{f(14 * s)}" rx="{f(3 * s)}" fill="{PLUM}"/>'
            f'<circle cx="{f(x + w * 0.5)}" cy="{f(y - h * 0.92 + 7 * s)}" r="{f(4 * s)}" fill="{MUSTARD}"/>')


def workshop(x, y, s=1.0):
    w, h = 140 * s, 84 * s
    sd = 28 * s
    door = "".join(f'<rect x="{f(x + 18 * s)}" y="{f(y - h * 0.66 + i * 9 * s)}" width="{f(68 * s)}" height="{f(4 * s)}" fill="#5B5272"/>' for i in range(6))
    return (f'<path d="M{f(x + w)},{f(y)} V{f(y - h)} l{f(sd)},{f(-sd * 0.25)} V{f(y - sd * 0.25)} Z" fill="#7F9BC0"/>'
            f'<rect x="{f(x)}" y="{f(y - h)}" width="{f(w)}" height="{f(h)}" fill="#A9C3E0"/>'
            f'<path d="M{f(x - 6 * s)},{f(y - h - 10 * s)} h{f(w + 12 * s)} l{f(sd)},{f(-sd * 0.25)} v{f(10 * s)} l{f(-sd)},{f(sd * 0.25)} h{f(-w - 12 * s)} z" fill="{PLUM_M}"/>'
            f'<rect x="{f(x - 6 * s)}" y="{f(y - h - 10 * s)}" width="{f(w + 12 * s)}" height="{f(4 * s)}" fill="{PLUM_L}"/>'
            f'<rect x="{f(x + 14 * s)}" y="{f(y - h * 0.7)}" width="{f(76 * s)}" height="{f(h * 0.7)}" fill="#3B3550"/>' + door +
            f'<rect x="{f(x + 100 * s)}" y="{f(y - h * 0.6)}" width="{f(26 * s)}" height="{f(22 * s)}" rx="{f(2 * s)}" fill="{SEA_L}"/>'
            f'<rect x="{f(x + 22 * s)}" y="{f(y - h - 38 * s)}" width="{f(96 * s)}" height="{f(22 * s)}" rx="{f(4 * s)}" fill="{MUSTARD}"/>'
            f'<rect x="{f(x + 22 * s)}" y="{f(y - h - 20 * s)}" width="{f(96 * s)}" height="{f(4 * s)}" rx="{f(2 * s)}" fill="{MUSTARD_D}"/>'
            f'<rect x="{f(x + 52 * s)}" y="{f(y - h - 29 * s)}" width="{f(36 * s)}" height="{f(5 * s)}" rx="{f(2.5 * s)}" fill="{PLUM}"/>'
            f'<circle cx="{f(x + 52 * s)}" cy="{f(y - h - 26.5 * s)}" r="{f(6 * s)}" fill="{PLUM}"/>'
            f'<circle cx="{f(x + 52 * s)}" cy="{f(y - h - 26.5 * s)}" r="{f(2.5 * s)}" fill="{MUSTARD}"/>'
            f'<ellipse cx="{f(x + w + 20 * s)}" cy="{f(y - 7 * s)}" rx="{f(14 * s)}" ry="{f(7 * s)}" fill="{DARK}"/>'
            f'<ellipse cx="{f(x + w + 20 * s)}" cy="{f(y - 17 * s)}" rx="{f(14 * s)}" ry="{f(7 * s)}" fill="#3B3550"/>'
            f'<ellipse cx="{f(x + w + 17 * s)}" cy="{f(y - 19 * s)}" rx="{f(6 * s)}" ry="{f(2.5 * s)}" fill="#5B5272"/>')


def warehouse(x, y, s=1.0):
    w, h = 170 * s, 70 * s
    sd = 30 * s
    return (f'<path d="M{f(x + w)},{f(y)} V{f(y - h)} l{f(sd)},{f(-sd * 0.25)} V{f(y - sd * 0.25)} Z" fill="{MUSTARD_D}"/>'
            f'<rect x="{f(x)}" y="{f(y - h)}" width="{f(w)}" height="{f(h)}" fill="{MUSTARD}"/>'
            f'<path d="M{f(x - 6 * s)},{f(y - h)} Q{f(x + w / 2)},{f(y - h - 46 * s)} {f(x + w + 6 * s)},{f(y - h)} Z" fill="{ORANGE}"/>'
            f'<path d="M{f(x + w / 2)},{f(y - h - 23 * s)} Q{f(x + w * 0.85)},{f(y - h - 18 * s)} {f(x + w + 6 * s)},{f(y - h)} l{f(sd)},{f(-sd * 0.25)} Q{f(x + w * 0.9 + sd)},{f(y - h - 22 * s)} {f(x + w / 2 + sd)},{f(y - h - 30 * s)} Z" fill="#C95F2E"/>'
            f'<rect x="{f(x + 18 * s)}" y="{f(y - h * 0.72)}" width="{f(54 * s)}" height="{f(h * 0.72)}" fill="{PLUM_M}"/>'
            f'<rect x="{f(x + 86 * s)}" y="{f(y - h * 0.72)}" width="{f(54 * s)}" height="{f(h * 0.72)}" fill="{PLUM_M}"/>'
            f'<rect x="{f(x + 26 * s)}" y="{f(y - h * 0.5)}" width="{f(18 * s)}" height="{f(14 * s)}" fill="{WALL2}"/>'
            f'<rect x="{f(x + 46 * s)}" y="{f(y - h * 0.36)}" width="{f(16 * s)}" height="{f(14 * s)}" fill="{WALL}"/>')


# ---------- vehículos (solo donde el negocio los pide) ----------

def van_side(color=RED, dark="#B23A30"):
    return (f'<ellipse cx="4" cy="2" rx="100" ry="8" fill="{DARK}" opacity=".22"/>'
            f'<path d="M-92,-14 v-78 a12,12 0 0 1 12,-12 h108 l34,40 h20 a10,10 0 0 1 10,10 v40 a6,6 0 0 1 -6,6 h-172 a6,6 0 0 1 -6,-6 z" fill="{color}"/>'
            f'<path d="M-92,-40 h184 v20 a6,6 0 0 1 -6,6 h-172 a6,6 0 0 1 -6,-6 z" fill="{dark}"/>'
            f'<path d="M-80,-104 h108 l6,7 h-114 z" fill="#FFFFFF" opacity=".3"/>'
            '<path d="M32,-100 l28,34 h-34 v-34 z" fill="#3B3550"/><path d="M36,-96 l8,10 v-10 z" fill="#FFFFFF" opacity=".35"/>'
            f'<rect x="-80" y="-90" width="96" height="40" rx="6" fill="{CREAM}"/>'
            f'<rect x="-70" y="-80" width="44" height="6" rx="3" fill="{color}"/><rect x="-70" y="-68" width="70" height="6" rx="3" fill="{MUSTARD}"/>'
            f'<rect x="84" y="-40" width="10" height="10" rx="2" fill="{MUSTARD}"/>'
            f'<circle cx="-56" cy="-10" r="17" fill="{DARK}"/><circle cx="-56" cy="-10" r="7" fill="#B8B2C4"/>'
            f'<circle cx="62" cy="-10" r="17" fill="{DARK}"/><circle cx="62" cy="-10" r="7" fill="#B8B2C4"/>'
            f'<rect x="-76" y="-122" width="34" height="18" rx="2" fill="{WALL2}"/><rect x="-76" y="-122" width="34" height="5" rx="2" fill="{CREAM}"/>'
            f'<rect x="-38" y="-118" width="26" height="14" rx="2" fill="{MUSTARD}"/><rect x="-38" y="-118" width="26" height="4" rx="2" fill="#F5CF7A"/>')


def car_side(color=BLUE_CAR, dark=BLUE_CAR_D):
    return (f'<ellipse cx="4" cy="2" rx="92" ry="7" fill="{DARK}" opacity=".22"/>'
            f'<path d="M-84,-16 c0,-18 8,-28 28,-30 l22,-22 c6,-6 14,-8 22,-8 h34 c10,0 18,4 24,12 l18,20 c22,2 30,10 30,26 v6 a4,4 0 0 1 -4,4 h-170 a4,4 0 0 1 -4,-4 z" fill="{color}"/>'
            f'<path d="M-84,-22 h172 v8 a4,4 0 0 1 -4,4 h-164 a4,4 0 0 1 -4,-4 z" fill="{dark}"/>'
            '<path d="M-28,-48 l18,-18 c4,-4 8,-5 14,-5 h10 v23 z" fill="#3B3550"/>'
            '<path d="M20,-71 h12 c8,0 13,3 17,8 l14,15 h-43 z" fill="#3B3550"/>'
            '<path d="M-24,-50 l14,-14 h6 l-14,14 z M24,-68 h6 l-4,18 h-6 z" fill="#FFFFFF" opacity=".35"/>'
            f'<path d="M-40,-46 c20,-3 60,-3 104,0" stroke="#FFFFFF" stroke-width="3" opacity=".35" fill="none" stroke-linecap="round"/>'
            f'<circle cx="-50" cy="-8" r="16" fill="{DARK}"/><circle cx="-50" cy="-8" r="6" fill="#B8B2C4"/>'
            f'<circle cx="54" cy="-8" r="16" fill="{DARK}"/><circle cx="54" cy="-8" r="6" fill="#B8B2C4"/>'
            f'<rect x="80" y="-34" width="8" height="8" rx="2" fill="{MUSTARD}"/>')


# ---------- la web en construcción ----------

def browser_site(x0, y0, w, h, url="tunegocio.es"):
    """Ventana de navegador con una web a medio construir; la tercera tarjeta queda vacía.
    Devuelve (svg, (x, y, w, h) del hueco)."""
    font = "font-family=\"'Josefin Sans', system-ui, sans-serif\" font-weight=\"700\""
    o = [f'<rect x="{x0 + 12}" y="{y0 + 12}" width="{w}" height="{h}" rx="16" fill="{PLUM}"/>',
         f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="16" fill="{CREAM}" stroke="{PLUM}" stroke-width="4"/>',
         f'<path d="M{x0 + 2},{y0 + 36} V{y0 + 16} a14,14 0 0 1 14,-14 h{w - 32} a14,14 0 0 1 14,14 V{y0 + 36} z" fill="#F6E7CB"/>',
         f'<rect x="{x0}" y="{y0 + 36}" width="{w}" height="3" fill="{PLUM}"/>']
    for i, c in enumerate((RED, MUSTARD, G_MID2)):
        o.append(f'<circle cx="{x0 + 20 + i * 17}" cy="{y0 + 19}" r="5.5" fill="{c}"/>')
    o.append(f'<rect x="{x0 + 76}" y="{y0 + 9}" width="{w - 96}" height="20" rx="10" fill="{CREAM}" stroke="{PLUM}" stroke-width="2"/>')
    o.append(f'<circle cx="{x0 + 90}" cy="{y0 + 19}" r="4" fill="{G_DARK}"/>')
    o.append(f'<text x="{x0 + 100}" y="{y0 + 24}" font-size="13" fill="{PLUM_M}" {font}>{url}</text>')
    cx0, cw = x0 + 16, w - 32
    o.append(f'<circle cx="{cx0 + 9}" cy="{y0 + 56}" r="8" fill="{RED}"/>'
             f'<rect x="{cx0 + 24}" y="{y0 + 52}" width="70" height="8" rx="4" fill="{PLUM}"/>'
             f'<rect x="{x0 + w - 110}" y="{y0 + 47}" width="94" height="18" rx="9" fill="{RED}"/>'
             f'<rect x="{x0 + w - 96}" y="{y0 + 54}" width="66" height="4" rx="2" fill="{CREAM}"/>')
    hy, hh = y0 + 76, 104
    cid = D.uid("c")
    D.add(f'<clipPath id="{cid}"><rect x="{cx0}" y="{hy}" width="{cw}" height="{hh}" rx="10"/></clipPath>')
    g = lin_grad([(0, SKY_MID), (1, SKY_LOW)])
    rng = random.Random(4)
    o.append(f'<g clip-path="url(#{cid})"><rect x="{cx0}" y="{hy}" width="{cw}" height="{hh}" fill="url(#{g})"/>'
             f'<circle cx="{cx0 + cw - 70}" cy="{hy + 40}" r="18" fill="{CLOUD}"/>'
             + mountain_range(rng, cx0 + cw * 0.45, cx0 + cw, hy + 90, [(cx0 + cw * 0.62, hy + 34), (cx0 + cw * 0.86, hy + 44)], jag=0.5)
             + lit_hill([(cx0, hy + 82), (cx0 + cw * 0.35, hy + 70), (cx0 + cw * 0.7, hy + 84), (cx0 + cw, hy + 74)], G_MID, G_LIGHT, G_SH, rng, rim=4, folds=2, bottom=hy + hh)
             + '</g>')
    o.append(f'<text x="{cx0 + 18}" y="{hy + 38}" font-size="22" letter-spacing="1.5" fill="{PLUM}" {font}>TU NEGOCIO</text>'
             f'<rect x="{cx0 + 18}" y="{hy + 48}" width="120" height="6" rx="3" fill="{PLUM_L}"/>'
             f'<rect x="{cx0 + 18}" y="{hy + 62}" width="78" height="20" rx="10" fill="{RED}"/>'
             f'<rect x="{cx0 + 32}" y="{hy + 70}" width="50" height="4" rx="2" fill="{CREAM}"/>')
    ty, th, gap = hy + hh + 12, h - (hy + hh + 12 - y0) - 14, 12
    tw = (cw - 2 * gap) / 3
    for i in range(2):
        tx = cx0 + i * (tw + gap)
        o.append(f'<rect x="{f(tx)}" y="{ty}" width="{f(tw)}" height="{th}" rx="8" fill="{CLOUD}" stroke="{WALL2}" stroke-width="2"/>')
        o.append(f'<rect x="{f(tx + 12)}" y="{ty + th - 22}" width="{f(tw * 0.55)}" height="6" rx="3" fill="{PLUM}"/>'
                 f'<rect x="{f(tx + 12)}" y="{ty + th - 12}" width="{f(tw * 0.35)}" height="4" rx="2" fill="{PLUM_L}"/>')
        ix, iy = tx + 12, ty + 10
        if i == 0:
            o.append(awning(ix, iy, 40, 5, 10))
        else:
            o.append(f'<rect x="{f(ix + 6)}" y="{iy + 6}" width="30" height="6" rx="3" fill="{BLUE_CAR}" transform="rotate(-20 {f(ix + 20)} {iy + 9})"/>'
                     f'<circle cx="{f(ix + 6)}" cy="{iy + 14}" r="7" fill="{BLUE_CAR}"/><circle cx="{f(ix + 6)}" cy="{iy + 14}" r="3" fill="{CLOUD}"/>')
    slot = (cx0 + 2 * (tw + gap), ty, tw, th)
    sx, sy, sw, sh = slot
    o.append(f'<rect x="{f(sx)}" y="{sy}" width="{f(sw)}" height="{sh}" rx="8" fill="none" stroke="{PLUM_L}" stroke-width="2" stroke-dasharray="7 6"/>')
    return "".join(o), slot


def transport_card(w, h):
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
        o.append(f'<rect x="{x0 - 6}" y="{y - 52}" width="{x1 - x0 + 12}" height="6" rx="1" fill="{MUSTARD}"/>'
                 f'<rect x="{x0 - 6}" y="{y - 52}" width="{x1 - x0 + 12}" height="2" fill="#F5CF7A"/>')
        y -= 50
    return "".join(o)


def crane(mast_x, base, top, jib_left, jib_right, trolley_x):
    o = [f'<rect x="{mast_x - 12}" y="{top}" width="24" height="{base - top}" fill="none" stroke="{ORANGE}" stroke-width="4"/>']
    y = base
    while y - 24 > top:
        o.append(f'<path d="M{mast_x - 12},{y} L{mast_x + 12},{y - 24} M{mast_x + 12},{y - 24} L{mast_x - 12},{y - 48}" stroke="#C95F2E" stroke-width="2.5"/>')
        y -= 48
    o.append(f'<rect x="{jib_left}" y="{top - 16}" width="{jib_right - jib_left}" height="14" fill="none" stroke="{ORANGE}" stroke-width="3.5"/>')
    x = jib_left
    while x + 28 <= jib_right:
        o.append(f'<path d="M{x},{top - 2} L{x + 14},{top - 16} L{x + 28},{top - 2}" fill="none" stroke="#C95F2E" stroke-width="2"/>')
        x += 28
    o.append(f'<path d="M{mast_x},{top - 16} L{mast_x},{top - 52} L{jib_left + 30},{top - 16} M{mast_x},{top - 52} L{jib_right - 10},{top - 16}" fill="none" stroke="{PLUM_M}" stroke-width="2"/>')
    o.append(f'<rect x="{jib_right - 36}" y="{top - 2}" width="34" height="30" rx="3" fill="{PLUM_M}"/><rect x="{jib_right - 36}" y="{top - 2}" width="12" height="30" rx="3" fill="{PLUM_L}"/>')
    o.append(f'<rect x="{mast_x + 12}" y="{top}" width="30" height="24" rx="4" fill="{MUSTARD}"/><rect x="{mast_x + 36}" y="{top}" width="6" height="24" rx="2" fill="{MUSTARD_D}"/>'
             f'<rect x="{mast_x + 18}" y="{top + 5}" width="16" height="10" rx="2" fill="{SEA_L}"/>')
    o.append(f'<rect x="{trolley_x - 10}" y="{top - 2}" width="20" height="8" rx="2" fill="{PLUM}"/>')
    return "".join(o)


def cursor_icon():
    """Puntero del ratón con sombra; la punta está en el origen."""
    return ('<path d="M3,4 l0,34 l9,-8 l7,15 l7,-3 l-7,-15 l12,-1 z" fill="#2E2638" opacity=".25"/>'
            f'<path d="M0,0 l0,34 l9,-8 l7,15 l7,-3 l-7,-15 l12,-1 z" fill="{CLOUD}" stroke="{PLUM}" stroke-width="3" stroke-linejoin="round"/>')


# ---------- salida ----------

def svg(w, h, body, cls="", extra_attrs="", style="", defs=""):
    st = f"<style>{style}</style>" if style else ""
    c = f' class="{cls}"' if cls else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"{c}{extra_attrs}>{st}{defs}{body}</svg>'


DRIFT_CSS = ("@keyframes drift{from{transform:translateX(-26px)}to{transform:translateX(26px)}}"
             ".drift{animation:drift 26s ease-in-out infinite alternate}.drift.slow{animation-duration:40s}"
             "@keyframes fly{from{transform:translate(0,0)}to{transform:translate(-160px,-24px)}}"
             ".fly{animation:fly 30s linear infinite alternate}"
             "@media (prefers-reduced-motion:reduce){.drift,.fly{animation:none}}")


class Layers:
    """Escena dividida en capas; cada capa guarda su propio <defs>."""

    def __init__(self, name, w, h):
        self.name, self.w, self.h, self.items = name, w, h, []

    def layer(self, label, depth):
        defs = new_defs(f"{self.name[:2]}{len(self.items)}")
        self.items.append([label, depth, defs, []])
        return self.items[-1][3]

    def files(self):
        out = {}
        for i, (label, depth, defs, body) in enumerate(self.items):
            out[f"{self.name}-{i}-{label}.svg"] = svg(self.w, self.h, "".join(body), defs=defs.render(),
                                                      extra_attrs=' preserveAspectRatio="xMidYMax slice"', style=DRIFT_CSS)
        return out

    def inline(self, cls):
        groups = "".join(f'<g class="layer layer-{label}" data-depth="{depth}">{defs.render()}{"".join(body)}</g>'
                         for label, depth, defs, body in self.items)
        return svg(self.w, self.h, groups, cls=cls, extra_attrs=' preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false"')

    def depths(self):
        return [d for _, d, _, _ in self.items]


# ---------- escenas ----------

def hero():
    W, H = 1600, 1000
    rng = random.Random(7)
    L = Layers("hero", W, H)

    b = L.layer("sky", 0)
    b.append(sky(W, H, [(0, SKY_TOP), (0.45, SKY_MID), (0.66, SKY_LOW)]))
    b.append(sun_glow(1260, 440, 62, CLOUD))
    b.append(puffs(rng, 14, (0, 40, W, 400), [CLOUD, "#E8F0F8"], 3, 8))
    b.append(cloud(60, 130, 1.3, extra=' class="drift"'))
    b.append(cloud(1300, 100, 1.5, extra=' class="drift slow"'))
    b.append(cloud(320, 340, 0.8, PEACH, PEACH_SH, ' class="drift slow"'))
    b.append(cloud(-40, 450, 1.0, extra=' class="drift slow"'))
    b.append(cloud(1420, 390, 1.1, PEACH, PEACH_SH, ' class="drift"'))
    b.append(birds(1240, 220, 1.1, PLUM, ' class="hero-birds"'))

    b = L.layer("mountains", 0.15)
    b.append(mountain_range(rng, -20, 1620, 720, [(110, 560), (360, 470), (590, 520), (880, 455), (1100, 505), (1330, 462), (1540, 530)]))

    b = L.layer("hills", 0.3)
    b.append(lit_hill([(0, 650), (260, 615), (520, 660), (800, 632), (1100, 655), (1380, 605), (1600, 640)], G_MID, G_LIGHT, G_SH, rng, rim=10, folds=6,
                      stipple=(G_DARK, 70, 1.5, 3.5)))
    b.append(forest(rng, 0, 1600, lambda x: 690 + 18 * math.sin(x / 140), 40, 74, 34, skip=(470, 1130)))
    b.append(lit_hill([(0, 725), (300, 692), (640, 704), (900, 684), (1200, 712), (1600, 682)], G_MID2, G_MID, G_SH2, rng, rim=8, folds=5))
    b.append(house(170, 718, 54, 46))
    b.append(church(236, 720, 0.9))
    b.append(restaurant(280, 732, 0.95))
    b.append(cypress(462, 746, 98))
    b.append(cypress(440, 744, 64))
    b.append(workshop(1170, 734, 0.92))
    b.append(warehouse(1350, 738, 0.85))
    b.append(cypress(1150, 750, 88))
    b.append(round_tree(1520, 768, 22))

    b = L.layer("meadow", 0.45)
    b.append(lit_hill([(0, 795), (250, 762), (500, 778), (800, 762), (1100, 782), (1350, 752), (1600, 782)], G_LIGHT, G_PALE, G_MID, rng, rim=9, folds=7,
                      stipple=(G_MID2, 90, 1.5, 3)))
    for x in (70, 150, 1450, 1540):
        b.append(conifer(x, 810 + rng.uniform(-10, 10), rng.uniform(100, 140), G_DARK, G_DEEP, tiers=4))
    b.append(meadow_flowers(rng, 150, (0, 805, W, 1000)))
    path, _, _, _ = road([(760, 1030), (835, 970), (790, 925), (800, 892)], 150, 40, color="#EFDDB8", edge=CLOUD, dash=False)
    b.append(path)

    b = L.layer("site", 0.45)
    bx, by, bw, bh = 560, 626, 480, 270
    b.append(scaffolding(522, 548, by + 40, by + bh + 4))
    site, (sx, sy, sw, sh) = browser_site(bx, by, bw, bh)
    b.append(site)
    trolley = round(sx + sw / 2)
    b.append(crane(1100, by + bh + 4, 606, int(sx - 10), 1230, trolley))
    drop = 120
    b.append(f'<line x1="{trolley}" y1="612" x2="{trolley}" y2="{f(sy - 14)}" stroke="{PLUM}" stroke-width="2">'
             f'<animate attributeName="y2" values="{f(sy - 14 - drop)};{f(sy - 14)};{f(sy - 14)}" keyTimes="0;0.55;1" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1;0 0 1 1"/></line>')
    b.append(f'<g><animateTransform attributeName="transform" type="translate" values="0,{-drop};0,0;0,0" keyTimes="0;0.55;1" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines="0.4 0 0.2 1;0 0 1 1"/>'
             f'<path d="M{f(trolley - 14)},{f(sy)} L{trolley},{f(sy - 14)} L{f(trolley + 14)},{f(sy)}" fill="none" stroke="{PLUM}" stroke-width="2"/>'
             f'<g transform="translate({f(sx)},{f(sy)})">{transport_card(sw, sh)}</g></g>')
    # el cursor recorre la web y pulsa el botón de la portada
    cta_x, cta_y = bx + 16 + 18 + 40, by + 76 + 72
    b.append(f'<circle cx="{cta_x}" cy="{cta_y}" r="6" fill="none" stroke="{RED}" stroke-width="3" opacity="0">'
             '<animate attributeName="r" values="6;6;26" keyTimes="0;0.62;0.8" dur="7s" repeatCount="indefinite"/>'
             '<animate attributeName="opacity" values="0;0;.9;0" keyTimes="0;0.6;0.64;0.8" dur="7s" repeatCount="indefinite"/></circle>')
    b.append(f'<g><animateMotion dur="7s" repeatCount="indefinite" path="M{bx + 300},{by + 220} C{bx + 260},{by + 170} {bx + 150},{by + 200} {cta_x},{cta_y} '
             f'L{cta_x},{cta_y} C{bx + 150},{by + 120} {bx + 300},{by + 260} {bx + 300},{by + 220}" keyTimes="0;0.55;0.75;1" keyPoints="0;0.45;0.45;1" calcMode="linear"/>'
             f'<g><animateTransform attributeName="transform" type="scale" values="1;1;.85;1;1" keyTimes="0;0.6;0.63;0.67;1" dur="7s" repeatCount="indefinite"/>'
             + cursor_icon() + '</g></g>')

    b = L.layer("front", 0.7)
    b.append(lit_hill([(0, 965), (300, 942), (700, 978), (1000, 952), (1300, 936), (1600, 962)], CREAM, "#FFFBF2", "#EFE3CC", rng, rim=6))
    for x, s, r in ((150, 1.4, -8), (230, 1.0, 10), (1380, 1.2, 6), (1470, 1.5, -12)):
        b.append(poppy(x, 995, s, r))
    return L


def meeting():
    W, H = 600, 450
    rng = random.Random(3)
    L = Layers("meeting", W, H)
    b = L.layer("sky", 0)
    b.append(sky(W, H, [(0, "#F6E3C4"), (1, "#FBF4E4")]))
    b.append(sun_glow(470, 110, 40, PEACH, PEACH))
    b.append(cloud(30, 70, 0.8, PEACH, PEACH_SH, ' class="drift"'))
    b.append(cloud(330, 150, 0.55, extra=' class="drift slow"'))
    b.append(puffs(rng, 10, (0, 20, W, 180), [PEACH, CLOUD], 3, 7))
    b = L.layer("hills", 0.2)
    b.append(mountain_range(rng, -10, 610, 270, [(130, 200), (330, 215), (520, 190)], jag=0.6))
    b.append(lit_hill([(0, 268), (200, 252), (400, 266), (600, 248)], G_MID, G_LIGHT, G_SH, rng, rim=6, folds=4, stipple=(G_DARK, 30, 1, 2.2)))
    b.append(forest(rng, 0, 600, lambda x: 292, 26, 44, 26, skip=(150, 470)))
    b.append(cypress(70, 300, 120))
    b.append(cypress(100, 302, 80))
    b.append(cypress(540, 300, 130))
    b = L.layer("terrace", 0.45)
    b.append(f'<rect x="0" y="300" width="{W}" height="150" fill="#E9C9A0"/>')
    for i in range(8):
        b.append(f'<path d="M{f(-240 + i * 130)},450 L{f(130 + i * 50)},300" stroke="#DDB98C" stroke-width="3"/>')
    b.append(f'<path d="M0,300 h{W} v8 h-{W} z" fill="#DDB98C"/>')
    b.append(f'<ellipse cx="330" cy="420" rx="210" ry="22" fill="{PLUM}" opacity=".12"/>')
    # sombrilla
    b.append(f'<rect x="296" y="96" width="8" height="250" fill="{PLUM_M}"/><rect x="296" y="96" width="3" height="250" fill="{PLUM_L}"/>')
    b.append(f'<path d="M140,150 Q300,40 460,150 Z" fill="{ORANGE}"/>')
    for i in range(4):
        b.append(f'<path d="M{f(140 + i * 80)},150 Q{f(180 + i * 80)},122 {f(220 + i * 80)},150 Z" fill="{CREAM if i % 2 else POPPY}"/>')
    b.append(f'<path d="M300,62 Q400,80 460,150 L300,150 Z" fill="#000" opacity=".08"/>')
    # sillas
    for x0, flip in ((120, 1), (480, -1)):
        b.append(f'<g transform="translate({x0},0) scale({flip},1)"><rect x="0" y="270" width="14" height="110" rx="4" fill="{PLUM}"/>'
                 f'<rect x="-10" y="330" width="70" height="12" rx="4" fill="{PLUM}"/><rect x="46" y="336" width="10" height="60" fill="{PLUM}"/>'
                 f'<rect x="0" y="270" width="5" height="110" rx="2" fill="{PLUM_L}"/></g>')
    # mesa
    b.append(f'<rect x="290" y="300" width="20" height="120" fill="{PLUM_M}"/><ellipse cx="300" cy="420" rx="60" ry="10" fill="{PLUM_M}"/>')
    b.append(f'<ellipse cx="300" cy="306" rx="170" ry="34" fill="{WALL_SH}"/><ellipse cx="300" cy="298" rx="170" ry="32" fill="{CREAM}"/>'
             f'<path d="M140,290 Q300,268 460,290" stroke="#FFFFFF" stroke-width="4" fill="none" opacity=".6"/>')
    # portátil con la web
    b.append('<g transform="translate(222,196)">'
             f'<path d="M-6,104 h168 l-10,14 h-148 z" fill="{PLUM_M}"/><path d="M-6,104 h168 v3 h-168 z" fill="{PLUM_L}"/>'
             f'<rect width="156" height="104" rx="8" fill="{PLUM}"/>'
             f'<rect x="8" y="8" width="140" height="88" rx="4" fill="{CREAM}"/>'
             f'<rect x="8" y="8" width="140" height="12" rx="4" fill="#F6E7CB"/>'
             f'<circle cx="16" cy="14" r="2.5" fill="{RED}"/><circle cx="24" cy="14" r="2.5" fill="{MUSTARD}"/><circle cx="32" cy="14" r="2.5" fill="{G_MID2}"/>'
             f'<rect x="12" y="24" width="132" height="34" rx="3" fill="{SKY_MID}"/>'
             f'<path d="M12,58 V48 Q46,38 78,46 T144,42 V58 Z" fill="{G_MID}"/><path d="M12,48 Q46,38 78,46 T144,42 v3 Q110,46 78,49 T12,51 z" fill="{G_LIGHT}"/>'
             f'<rect x="18" y="30" width="44" height="6" rx="3" fill="{PLUM}"/><rect x="18" y="40" width="22" height="7" rx="3.5" fill="{RED}"/>'
             f'<rect x="12" y="64" width="40" height="26" rx="3" fill="{PEACH}"/><rect x="58" y="64" width="40" height="26" rx="3" fill="{G_LIGHT}"/>'
             f'<rect x="104" y="64" width="40" height="26" rx="3" fill="none" stroke="{PLUM_L}" stroke-width="1.5" stroke-dasharray="4 3"/>'
             '</g>')
    for cx, col in ((178, RED), (432, BLUE_CAR)):
        b.append(f'<ellipse cx="{cx}" cy="300" rx="22" ry="6" fill="{WALL2}"/>'
                 f'<path d="M{cx - 14},274 h28 v14 a14,12 0 0 1 -28,0 z" fill="{col}"/>'
                 f'<path d="M{cx - 14},274 h8 v18 a14,12 0 0 1 -8,-4 z" fill="#FFFFFF" opacity=".25"/>'
                 f'<path d="M{cx + 14},278 a7,7 0 0 1 0,12" fill="none" stroke="{col}" stroke-width="4"/>'
                 f'<path d="M{cx - 4},262 q-6,-8 0,-16 M{cx + 5},262 q-6,-8 0,-16" fill="none" stroke="{CREAM}" stroke-width="3" stroke-linecap="round"/>')
    b = L.layer("plant", 0.7)
    b.append(f'<path d="M548,450 l8,-56 h40 l8,56 z" fill="{ROOF}"/><path d="M576,394 h20 l8,56 h-20 z" fill="{ROOF_D}"/>'
             f'<circle cx="566" cy="380" r="22" fill="{G_DARK}"/><circle cx="590" cy="372" r="18" fill="{G_MID2}"/><circle cx="578" cy="356" r="16" fill="{G_DARK}"/>'
             f'<circle cx="572" cy="352" r="7" fill="{G_LIGHT}" opacity=".7"/>')
    return L


def cover_restaurante():
    W, H = 600, 800
    rng = random.Random(11)
    L = Layers("cover-restaurante", W, H)
    b = L.layer("sky", 0)
    b.append(sky(W, H, [(0, "#F4DFC0"), (0.5, "#FAE9D2"), (1, "#FBF4E4")]))
    b.append(sun_glow(470, 300, 38, "#FFF3DC", "#FFF6E6"))
    b.append(puffs(rng, 10, (0, 30, W, 330), [PEACH, PEACH_D], 3, 8))
    b.append(cloud(-70, 340, 0.9, PEACH, PEACH_SH, ' class="drift"'))
    b.append(cloud(470, 320, 0.8, PEACH, PEACH_SH, ' class="drift slow"'))
    b.append(birds(70, 370, 0.7, PLUM, ' class="fly"'))
    b = L.layer("village", 0.2)
    b.append(mountain_range(rng, -10, 610, 440, [(120, 380), (330, 365), (520, 390)], jag=0.6))
    b.append(lit_hill([(0, 470), (180, 442), (360, 456), (600, 432)], G_MID, G_LIGHT, G_SH, rng, rim=7, folds=4, stipple=(G_DARK, 40, 1.2, 2.6)))
    for i, x in enumerate((50, 128, 206, 284, 362)):
        b.append(house(x, 474 + (i % 2) * 8, 44, 30, WALL if i % 2 else WALL2))
    b.append(church(450, 472, 0.7))
    b = L.layer("facade", 0.4)
    b.append(f'<rect x="250" y="440" width="350" height="250" fill="#F2D7B0"/>')
    b.append(f'<path d="M250,440 h350 v250 h-350 z" fill="url(#{lin_grad([(0, "#F8E1BE"), (1, "#E9C59A")], vertical=False)})"/>')
    b.append(f'<rect x="250" y="428" width="350" height="18" fill="{ROOF}"/><rect x="250" y="440" width="350" height="6" fill="{ROOF_D}"/>')
    for x in (280, 380, 480):
        b.append(f'<path d="M{x},690 v-110 a40,40 0 0 1 80,0 v110 z" fill="{PLUM_M}"/>'
                 f'<path d="M{x + 8},690 v-104 a32,32 0 0 1 64,0 v104 z" fill="#3B3550"/>'
                 f'<rect x="{x + 14}" y="610" width="52" height="34" rx="4" fill="{MUSTARD}" opacity=".9"/>'
                 f'<rect x="{x + 14}" y="610" width="52" height="8" rx="4" fill="#F7D98C"/>')
    b.append(awning(250, 520, 350, 10, 22))
    b.append(f'<rect x="330" y="470" width="190" height="34" rx="6" fill="{PLUM}"/>'
             f'<circle cx="372" cy="487" r="9" fill="{CREAM}"/><rect x="390" y="482" width="110" height="10" rx="5" fill="{CREAM}"/>')
    b.append(f'<path d="M0,380 Q150,440 300,410 T600,420" fill="none" stroke="{PLUM}" stroke-width="2"/>')
    for t in range(1, 12):
        x = t * 50
        y = 380 + 40 * math.sin(math.pi * x / 300) * (1 if x < 300 else 0.4) + (0 if x < 300 else 20)
        b.append(f'<circle cx="{x}" cy="{f(y + 6)}" r="9" fill="{MUSTARD}" opacity=".3"/><circle cx="{x}" cy="{f(y + 6)}" r="5" fill="#FBE3A0"/>')
    b.append(cypress(200, 700, 260))
    b.append(cypress(150, 700, 180))
    b = L.layer("terrace", 0.6)
    b.append(f'<rect x="0" y="690" width="{W}" height="110" fill="#E9C9A0"/>')
    for i in range(9):
        b.append(f'<path d="M{-300 + i * 120},800 L{60 + i * 60},690" stroke="#DDB98C" stroke-width="3"/>')
    b.append(f'<path d="M0,690 h{W} v6 h-{W} z" fill="#D4AD7E"/>')
    for x, c in ((110, ORANGE), (420, RED)):
        b.append(f'<ellipse cx="{x + 30}" cy="752" rx="80" ry="12" fill="{PLUM}" opacity=".14"/>'
                 f'<rect x="{x - 3}" y="560" width="6" height="190" fill="{PLUM}"/>'
                 f'<path d="M{x - 90},600 Q{x},530 {x + 90},600 Z" fill="{c}"/>'
                 f'<path d="M{x},548 Q{x + 60},560 {x + 90},600 L{x},600 Z" fill="#000" opacity=".1"/>'
                 f'<path d="M{x - 30},600 Q{x},585 {x + 30},600 Z" fill="{CREAM}"/>'
                 f'<ellipse cx="{x}" cy="724" rx="64" ry="14" fill="{WALL_SH}"/><ellipse cx="{x}" cy="720" rx="64" ry="13" fill="{CREAM}"/>'
                 f'<rect x="{x - 4}" y="724" width="8" height="60" fill="{PLUM_M}"/>'
                 f'<path d="M{x - 26},700 h12 l-2,14 h-8 z M{x + 14},700 h12 l-2,14 h-8 z" fill="{RED}" opacity=".85"/>'
                 f'<rect x="{x - 21}" y="714" width="2" height="8" fill="{PLUM}"/><rect x="{x + 19}" y="714" width="2" height="8" fill="{PLUM}"/>')
    b.append(f'<path d="M520,800 l10,-70 h50 l10,70 z" fill="{ROOF}"/><path d="M555,730 h25 l10,70 h-25 z" fill="{ROOF_D}"/>'
             f'<circle cx="545" cy="716" r="28" fill="{G_DARK}"/><circle cx="572" cy="704" r="22" fill="{G_MID2}"/><circle cx="560" cy="694" r="8" fill="{G_LIGHT}" opacity=".7"/>')
    return L


def cover_taller():
    W, H = 600, 800
    rng = random.Random(5)
    L = Layers("cover-taller", W, H)
    b = L.layer("sky", 0)
    b.append(sky(W, H, [(0, SKY_TOP), (0.42, SKY_MID), (0.68, SKY_LOW)]))
    b.append(puffs(rng, 8, (0, 30, W, 300), [CLOUD], 3, 7))
    b.append(cloud(-80, 330, 0.85, extra=' class="drift"'))
    b.append(cloud(500, 410, 0.6, extra=' class="drift slow"'))
    b.append(birds(430, 350, 0.8, PLUM, ' class="fly"'))
    b = L.layer("mountains", 0.15)
    b.append(mountain_range(rng, -10, 610, 510, [(70, 380), (230, 330), (400, 370), (540, 345)]))
    b = L.layer("forest", 0.3)
    b.append(lit_hill([(0, 478), (200, 456), (400, 474), (600, 446)], G_MID, G_LIGHT, G_SH, rng, rim=8, folds=4, stipple=(G_DARK, 40, 1.2, 2.6)))
    b.append(forest(rng, -10, 610, lambda x: 506 - x * 0.03, 34, 62, 26))
    b.append(lit_hill([(0, 548), (220, 514), (420, 534), (600, 508)], G_MID2, G_MID, G_SH2, rng, rim=8, folds=5, stipple=(G_DARK, 40, 1.2, 2.6)))
    b.append(workshop(330, 604, 1.35))
    b.append(cypress(312, 612, 130))
    b = L.layer("road", 0.5)
    rd, _, _, _ = road([(-40, 810), (180, 722), (360, 652), (520, 622), (640, 602)], 170, 40)
    b.append(rd)
    b.append('<g transform="translate(220,744) rotate(-17) scale(0.9)">' + car_side() + '</g>')
    b = L.layer("front", 0.7)
    b.append(lit_hill([(330, 830), (450, 735), (600, 702), (640, 700)], G_LIGHT, G_PALE, G_MID, rng, rim=8, folds=2))
    b.append(meadow_flowers(rng, 50, (420, 730, 600, 800)))
    for x, s, r in ((470, 1.1, -6), (540, 1.4, 8), (595, 1.0, -10)):
        b.append(poppy(x, 812, s, r))
    return L


def cover_transporte():
    W, H = 600, 800
    rng = random.Random(9)
    L = Layers("cover-transporte", W, H)
    b = L.layer("sky", 0)
    b.append(sky(W, H, [(0, "#C9C3E8"), (0.4, "#E4E0F3"), (0.62, "#FBF0DE")]))
    b.append(puffs(rng, 8, (0, 30, W, 300), [LILAC_L, CLOUD], 3, 7))
    b.append(cloud(-70, 330, 0.9, LILAC_L, "#C2BCE0", ' class="drift"'))
    b.append(cloud(480, 320, 0.75, extra=' class="drift slow"'))
    b.append(birds(90, 360, 0.7, PLUM, ' class="fly"'))
    b = L.layer("sea", 0.15)
    b.append(lit_hill([(0, 400), (200, 380), (420, 408), (600, 384)], LILAC, LILAC_L, LILAC_D, rng, rim=6, folds=3))
    b.append(f'<rect x="0" y="428" width="{W}" height="160" fill="{SEA}"/>')
    b.append(f'<rect x="0" y="428" width="{W}" height="8" fill="{SEA_L}"/>')
    for i in range(14):
        y = 444 + i * 10
        b.append(f'<rect x="{f(rng.uniform(0, 520))}" y="{y}" width="{f(rng.uniform(26, 90))}" height="3" rx="1.5" fill="{SEA_L if i % 3 else CLOUD}" opacity=".85"/>')
    b = L.layer("cliffs", 0.35)
    b.append(lit_hill([(-10, 440), (110, 430), (200, 480), (250, 640)], G_MID, G_LIGHT, G_SH, rng, rim=7, folds=2))
    b.append(lit_hill([(180, 640), (300, 460), (430, 370), (610, 330)], MUSTARD, "#F6D27E", MUSTARD_D, rng, rim=9, folds=6,
                      dapple=[(G_MID2, 40), (PLUM_L, 30), (ORANGE, 30)]))
    b.append(lit_hill([(260, 660), (370, 500), (480, 440), (610, 415)], ORANGE, "#F2995E", "#C95F2E", rng, rim=8, folds=5,
                      dapple=[(G_DARK, 30), (PLUM_M, 40), (MUSTARD, 30)], stipple=(PLUM_M, 50, 2, 4)))
    b.append(lit_hill([(0, 600), (150, 580), (300, 610), (600, 560)], G_MID2, G_MID, G_SH2, rng, rim=8, folds=4, stipple=(G_DARK, 40, 1.2, 2.6)))
    b = L.layer("road", 0.55)
    rd, _, left, right = road([(640, 690), (420, 650), (240, 640), (60, 600), (-40, 590)], 170, 60)
    b.append(rd)
    b.append(lit_hill([(640, 760), (400, 718), (200, 716), (-40, 668)], G_LIGHT, G_PALE, G_MID, rng, rim=6))
    edge = catmull([(640, 744), (400, 706), (200, 704), (-40, 656)], 10)
    b.append(guardrail(edge[::2], 1))
    b.append('<g transform="translate(300,664) rotate(4) scale(0.95)">' + van_side() + '</g>')
    b = L.layer("front", 0.7)
    b.append(lit_hill([(0, 772), (300, 748), (600, 776)], G_LIGHT, G_PALE, G_MID, rng, rim=6, folds=2))
    b.append(meadow_flowers(rng, 60, (0, 760, 600, 800)))
    for x, s, r in ((40, 1.2, 6), (110, 1.5, -8), (520, 1.3, 10), (580, 1.0, -6)):
        b.append(poppy(x, 815, s, r))
    return L


def sunset():
    W, H = 1600, 700
    rng = random.Random(21)
    L = Layers("sunset", W, H)
    b = L.layer("sky", 0)
    b.append(sky(W, H, [(0, "#F6D9B8"), (0.45, "#F2B48E"), (0.75, "#E9895A")]))
    b.append(f'<circle cx="800" cy="470" r="240" fill="url(#{rad_grad([(0, "#FCE3B0", 0.7), (1, "#FCE3B0", 0)])})"/>')
    b.append(f'<rect x="610" y="330" width="380" height="250" rx="22" fill="#FCE3B0"/>'
             f'<rect x="610" y="330" width="380" height="44" rx="22" fill="#F9D58E"/><rect x="610" y="352" width="380" height="22" fill="#F9D58E"/>'
             '<circle cx="640" cy="352" r="7" fill="#E9895A"/><circle cx="662" cy="352" r="7" fill="#EDB84E"/><circle cx="684" cy="352" r="7" fill="#A6CB72"/>'
             '<rect x="708" y="343" width="250" height="18" rx="9" fill="#FCE3B0"/>'
             '<circle cx="800" cy="418" r="36" fill="#E9895A"/><path d="M783,419 l11,11 l23,-25" stroke="#FCE3B0" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(puffs(rng, 18, (0, 30, W, 300), ["#F9E6CC", PEACH], 3, 9))
    b.append(cloud(80, 170, 1.2, "#F9E6CC", PEACH, ' class="drift"'))
    b.append(cloud(1250, 130, 1.4, "#F9E6CC", PEACH, ' class="drift slow"'))
    b.append(cloud(1010, 300, 0.8, PEACH, PEACH_D, ' class="drift"'))
    b.append(birds(1080, 230, 1.0, PLUM, ' class="fly"'))
    b = L.layer("far", 0.2)
    b.append(lit_hill([(0, 480), (250, 430), (520, 470), (800, 440), (1100, 470), (1350, 420), (1600, 460)], "#B48AA8", "#E7B79E", "#9B7393", rng, rim=8, folds=7))
    b = L.layer("mid", 0.4)
    b.append(lit_hill([(0, 540), (300, 500), (640, 530), (960, 505), (1280, 540), (1600, 500)], "#8E6F9E", "#C99AA6", "#77598A", rng, rim=8, folds=7))
    trees = []
    for x in range(30, 1600, 60):
        if 620 < x < 980:
            continue
        trees.append(cypress(x + rng.uniform(-12, 12), 560 + rng.uniform(-14, 10), rng.uniform(60, 110), "#5B4B6E", "#7A6290"))
    b.append("".join(trees))
    for _ in range(26):
        b.append(f'<rect x="{f(rng.uniform(640, 960))}" y="{f(rng.uniform(510, 560))}" width="6" height="8" rx="1" fill="#FCE3B0"/>')
    b = L.layer("near", 0.6)
    b.append(lit_hill([(0, 600), (360, 570), (800, 590), (1200, 565), (1600, 600)], "#6E5480", "#A27896", "#5B4570", rng, rim=8, folds=6))
    b.append(lit_hill([(0, 670), (400, 650), (800, 675), (1200, 645), (1600, 670)], "#33283B", "#4A3A54", "#33283B", rng, rim=5))
    return L


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    manifest = {}
    for scene in (meeting(), cover_restaurante(), cover_taller(), cover_transporte(), sunset()):
        files = scene.files()
        for name, content in files.items():
            (OUT / name).write_text(content + "\n")
        manifest[scene.name] = list(zip(files.keys(), scene.depths()))
        print(f"{scene.name}: {len(files)} capas, {sum(len(c) for c in files.values()) // 1024} KB")

    index = ROOT / "index.html"
    html = index.read_text()
    start, end = "<!-- HERO-SVG:START -->", "<!-- HERO-SVG:END -->"
    if start in html and end in html:
        before, rest = html.split(start, 1)
        _, after = rest.split(end, 1)
        hero_svg = hero().inline("hero-svg")
        index.write_text(before + start + hero_svg + end + after)
        print(f"hero inline: {len(hero_svg) // 1024} KB")
    return manifest


if __name__ == "__main__":
    for name, layers in main().items():
        print(name, layers)
