"""Genera los SVG del README de GitHub con el estilo glassmorphism oscuro.
Uso: python3 build.py  ->  escribe en out/assets/*.svg y out/README.md
"""
import base64, io, os, re, random
from xml.sax.saxutils import escape
from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out", "assets")
os.makedirs(OUT, exist_ok=True)

FONT_FILES = {
    ("Sora", 600): "node_modules/@fontsource/sora/files/sora-latin-600-normal.woff2",
    ("Sora", 700): "node_modules/@fontsource/sora/files/sora-latin-700-normal.woff2",
    ("Outfit", 400): "node_modules/@fontsource/outfit/files/outfit-latin-400-normal.woff2",
    ("Outfit", 500): "node_modules/@fontsource/outfit/files/outfit-latin-500-normal.woff2",
    ("Outfit", 600): "node_modules/@fontsource/outfit/files/outfit-latin-600-normal.woff2",
}
FONTS = {k: TTFont(os.path.join(ROOT, v)) for k, v in FONT_FILES.items()}

# Paleta
NEGRO, HONDO_BG = "#06080b", "#0a2236"
CELESTE, CELESTE_CLARO, CELESTE_HONDO = "#3db4ef", "#93d6f8", "#0d6aa3"
TINTA, PLOMO, NIEBLA = "#0d1117", "#4a5562", "#f3f6f9"
TEXTO_CLARO, TEXTO_SUAVE = "#eef3f7", "#b4c0cc"
CURVA = "cubic-bezier(.22,.8,.24,1)"


def width(text, fam, wt, size, ls=0.0):
    f = FONTS[(fam, wt)]
    cmap, hmtx, upm = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    tot = 0
    for ch in text:
        g = cmap.get(ord(ch)) or cmap.get(32)
        tot += hmtx[g][0]
    return tot / upm * size + ls * size * max(len(text) - 1, 0)


def wrap(text, fam, wt, size, maxw):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if width(t, fam, wt, size) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Doc:
    """Acumula SVG y registra qué caracteres usa cada fuente para incrustar solo eso."""

    def __init__(self, w, h, title):
        self.w, self.h, self.title = w, h, title
        self.defs, self.body, self.css = [], [], []
        self.chars = {}

    def t(self, x, y, text, fam="Outfit", wt=400, size=16, fill=TEXTO_CLARO,
          ls=0.0, anchor="start", cls="", extra=""):
        self.chars.setdefault((fam, wt), set()).update(text)
        c = f' class="{cls}"' if cls else ""
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        l = f' letter-spacing="{ls}em"' if ls else ""
        self.body.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-weight="{wt}" '
            f'font-size="{size}" fill="{fill}"{l}{a}{c} {extra}>{escape(text)}</text>')

    def raw(self, s):
        self.body.append(s)

    def render(self):
        faces = []
        for (fam, wt), chars in sorted(self.chars.items()):
            chars = set(chars) | set(" ")
            opts = subset.Options()
            opts.flavor = "woff2"
            opts.layout_features = ["kern", "liga"]
            sub = subset.Subsetter(opts)
            font = TTFont(os.path.join(ROOT, FONT_FILES[(fam, wt)]))
            sub.populate(text="".join(chars))
            sub.subset(font)
            buf = io.BytesIO()
            font.flavor = "woff2"
            font.save(buf)
            b64 = base64.b64encode(buf.getvalue()).decode()
            faces.append(
                f"@font-face{{font-family:'{fam}';font-weight:{wt};"
                f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
        reduce = ("@media (prefers-reduced-motion: reduce){*{animation:none!important}"
                  ".no-rm{display:none}}")
        style = "\n".join(faces + self.css + [reduce])
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{escape(self.title)}">'
                f'<title>{escape(self.title)}</title>'
                f'<style>{style}</style><defs>{"".join(self.defs)}</defs>'
                f'{"".join(self.body)}</svg>')

    def save(self, name):
        path = os.path.join(OUT, name)
        with open(path, "w") as fh:
            fh.write(self.render())
        print(f"{name:24s} {os.path.getsize(path)/1024:6.1f} KB")


# ---------- piezas comunes ----------

def common_defs(d):
    d.defs.append(f"""
<linearGradient id="vidrio" x1="0" y1="0" x2="0.35" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity=".10"/>
  <stop offset="1" stop-color="#fff" stop-opacity=".025"/></linearGradient>
<linearGradient id="vidrioFuerte" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{CELESTE}" stop-opacity=".20"/>
  <stop offset=".6" stop-color="{CELESTE}" stop-opacity=".06"/>
  <stop offset="1" stop-color="#fff" stop-opacity=".04"/></linearGradient>
<linearGradient id="reflejo" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/>
  <stop offset=".5" stop-color="#fff" stop-opacity=".45"/>
  <stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="acento" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#5cc6f7"/><stop offset=".5" stop-color="{CELESTE}"/>
  <stop offset="1" stop-color="{CELESTE_CLARO}"/></linearGradient>
<linearGradient id="boton" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#6fd0fb"/><stop offset="1" stop-color="{CELESTE}"/></linearGradient>
<linearGradient id="destello" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{CELESTE_CLARO}" stop-opacity="0"/>
  <stop offset=".5" stop-color="{CELESTE_CLARO}" stop-opacity=".22"/>
  <stop offset="1" stop-color="{CELESTE_CLARO}" stop-opacity="0"/></linearGradient>
<filter id="difuso" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="55"/></filter>
<filter id="brillo" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2"/></filter>""")
    d.css.append(f"""
.entra{{animation:entra .9s {CURVA} backwards}}
@keyframes entra{{from{{opacity:0;transform:translateY(18px)}}to{{opacity:1;transform:none}}}}
.luz1{{animation:luz1 18s ease-in-out infinite alternate}}
.luz2{{animation:luz2 22s ease-in-out infinite alternate}}
.luz3{{animation:luz3 26s ease-in-out infinite alternate}}
@keyframes luz1{{to{{transform:translate(140px,40px)}}}}
@keyframes luz2{{to{{transform:translate(-160px,-30px)}}}}
@keyframes luz3{{to{{transform:translate(90px,-50px)}}}}
.chispa{{animation:chispa 4s ease-in-out infinite}}
@keyframes chispa{{0%,100%{{opacity:.15}}50%{{opacity:.9}}}}
.raya{{animation:raya 9s linear infinite}}
@keyframes raya{{0%{{transform:translateX(-400px);opacity:0}}15%{{opacity:.9}}60%{{opacity:.9}}100%{{transform:translateX(1300px);opacity:0}}}}
.cruza{{animation:cruza 7s {CURVA} infinite}}
@keyframes cruza{{0%,55%{{transform:translateX(-300px)}}100%{{transform:translateX(1300px)}}}}""")


def fondo_vivo(d, w, h, rx=28, seed=1, intensidad=1.0, particulas=12, rayas=True):
    """Fondo oscuro animado recortado a un rectángulo redondeado."""
    rnd = random.Random(seed)
    d.defs.append(f"""
<clipPath id="marco"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>
<radialGradient id="hondo" cx=".25" cy=".1" r="1">
  <stop offset="0" stop-color="{HONDO_BG}"/><stop offset=".7" stop-color="{NEGRO}"/></radialGradient>
<pattern id="rejilla" width="36" height="36" patternUnits="userSpaceOnUse">
  <path d="M36 0H0V36" fill="none" stroke="#fff" stroke-opacity=".045"/></pattern>
<radialGradient id="mascaraG" cx=".5" cy=".35" r=".7">
  <stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<mask id="mascara"><rect width="{w}" height="{h}" fill="url(#mascaraG)"/></mask>
<linearGradient id="rayaG" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{CELESTE}" stop-opacity="0"/>
  <stop offset=".5" stop-color="{CELESTE_CLARO}" stop-opacity=".55"/>
  <stop offset="1" stop-color="{CELESTE}" stop-opacity="0"/></linearGradient>""")
    k = intensidad
    # Luces difusas con degradados radiales (mucho más ligeras que un filtro de desenfoque animado)
    for i, col in enumerate([CELESTE, "#1f5fae", CELESTE_HONDO]):
        d.defs.append(f'<radialGradient id="luzG{i}"><stop offset="0" stop-color="{col}"/>'
                      f'<stop offset=".45" stop-color="{col}" stop-opacity=".45"/>'
                      f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>')
    r = min(h, 260) * 1.5
    s = [f'<g clip-path="url(#marco)">',
         f'<rect width="{w}" height="{h}" fill="url(#hondo)"/>',
         f'<circle class="luz1" cx="{w*.18:.0f}" cy="{h*.2:.0f}" r="{r*.8:.0f}" fill="url(#luzG0)" opacity="{.38*k:.2f}"/>',
         f'<circle class="luz2" cx="{w*.82:.0f}" cy="{h*.35:.0f}" r="{r*.9:.0f}" fill="url(#luzG1)" opacity="{.55*k:.2f}"/>',
         f'<circle class="luz3" cx="{w*.55:.0f}" cy="{h*.95:.0f}" r="{r*.75:.0f}" fill="url(#luzG2)" opacity="{.5*k:.2f}"/>',
         f'<rect width="{w}" height="{h}" fill="url(#rejilla)" mask="url(#mascara)"/>']
    if rayas:
        for i, (y, dl) in enumerate([(h * .28, 0), (h * .7, 4.5)]):
            s.append(f'<g transform="rotate(-14 {w/2} {y:.0f})"><rect class="raya no-rm" '
                     f'style="animation-delay:{dl}s" x="0" y="{y:.0f}" width="360" height="1.2" fill="url(#rayaG)"/></g>')
    for i in range(particulas):
        x, y = rnd.uniform(20, w - 20), rnd.uniform(16, h - 16)
        r = rnd.choice([1, 1.3, 1.6, 2])
        s.append(f'<circle class="chispa" style="animation-delay:{rnd.uniform(0,4):.2f}s" cx="{x:.0f}" '
                 f'cy="{y:.0f}" r="{r}" fill="{CELESTE_CLARO}"/>')
    s.append('</g>')
    s.append(f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{rx}" fill="none" stroke="#fff" stroke-opacity=".08"/>')
    d.raw("".join(s))


def vidrio(d, x, y, w, h, rx=20, fuerte=False, destello=True, delay=0.0, cid=None):
    cid = cid or f"v{len(d.defs)}"
    d.defs.append(f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></clipPath>')
    stroke = f'stroke="{CELESTE}" stroke-opacity=".45"' if fuerte else 'stroke="#fff" stroke-opacity=".14"'
    fill = "url(#vidrioFuerte)" if fuerte else "url(#vidrio)"
    s = [f'<g class="entra" style="animation-delay:{delay}s">',
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="#0b121a" fill-opacity=".45"/>',
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" {stroke}/>',
         f'<rect x="{x+rx}" y="{y}" width="{w-2*rx}" height="1" fill="url(#reflejo)"/>']
    if destello:
        s.append(f'<g clip-path="url(#{cid})"><g class="cruza no-rm" style="animation-delay:{delay+1.2}s">'
                 f'<rect x="{x-260}" y="{y-40}" width="160" height="{h+80}" fill="url(#destello)" '
                 f'transform="skewX(-18)"/></g></g>')
    s.append('</g>')
    d.raw("".join(s))


def eyebrow(d, x, y, text, delay=0.0, anchor="start", fill=CELESTE):
    d.raw(f'<g class="entra" style="animation-delay:{delay}s">')
    if anchor == "start":
        d.raw(f'<rect x="{x}" y="{y-5}" width="22" height="2" rx="1" fill="{fill}"/>')
        d.t(x + 32, y, text.upper(), "Outfit", 600, 13, fill, ls=.16)
    else:
        tw = width(text.upper(), "Outfit", 600, 13, .16) + 32
        d.raw(f'<rect x="{x-tw/2}" y="{y-5}" width="22" height="2" rx="1" fill="{fill}"/>')
        d.t(x - tw / 2 + 32, y, text.upper(), "Outfit", 600, 13, fill, ls=.16)
    d.raw('</g>')


def titulo(d, x, y, partes, size=34, delay=0.1, oscuro=True, anchor="start"):
    """partes: lista de (texto, es_acento)."""
    base = TEXTO_CLARO if oscuro else TINTA
    full = "".join(p for p, _ in partes)
    tw = width(full, "Sora", 700, size, -.03)
    cx = x if anchor == "start" else x - tw / 2
    d.raw(f'<g class="entra" style="animation-delay:{delay}s">')
    for texto, acento in partes:
        fill = ("url(#acento)" if oscuro else CELESTE_HONDO) if acento else base
        d.t(cx, y, texto, "Sora", 700, size, fill, ls=-.03)
        cx += width(texto, "Sora", 700, size, -.03) + (-.03 * size)
    d.raw('</g>')


ICONS = {}


def icon(slug):
    if slug not in ICONS:
        if slug == "_aws":  # simple-icons ya no incluye AWS: nube genérica dibujada a mano
            ICONS[slug] = ("M6.5 19a4.5 4.5 0 0 1-.6-8.96A6 6 0 0 1 17.6 8.6 4.7 4.7 0 0 1 18 18"
                           ".98V19H6.5z")
        else:
            src = open(os.path.join(ROOT, "node_modules/simple-icons/icons", slug + ".svg")).read()
            ICONS[slug] = re.search(r'd="([^"]+)"', src).group(1)
    return ICONS[slug]


def chip(d, x, y, text, slug=None, h=38, size=15, delay=0.0, claro=False, punto=False):
    tw = width(text, "Outfit", 500, size)
    pad = 14
    iw = 18 if slug else (7 if punto else 0)
    gap = 9 if (slug or punto) else 0
    w = pad * 2 + iw + gap + tw
    if claro:
        d.raw(f'<g class="entra" style="animation-delay:{delay}s"><rect x="{x}" y="{y}" width="{w:.1f}" height="{h}" '
              f'rx="{h/2}" fill="{NIEBLA}" stroke="{TINTA}" stroke-opacity=".08"/>')
        col = TINTA
    else:
        d.raw(f'<g class="entra" style="animation-delay:{delay}s"><rect x="{x}" y="{y}" width="{w:.1f}" height="{h}" '
              f'rx="{h/2}" fill="url(#vidrio)" stroke="#fff" stroke-opacity=".14"/>'
              f'<rect x="{x+h/2}" y="{y}" width="{max(w-h,0):.1f}" height="1" fill="url(#reflejo)" opacity=".7"/>')
        col = TEXTO_CLARO
    if punto:
        d.raw(f'<circle cx="{x+pad+3.5}" cy="{y+h/2}" r="3.5" fill="{CELESTE}"/>'
              f'<circle cx="{x+pad+3.5}" cy="{y+h/2}" r="3.5" fill="{CELESTE}" filter="url(#brillo)"/>')
    if slug:
        sc = iw / 24
        d.raw(f'<path transform="translate({x+pad} {y+(h-iw)/2}) scale({sc})" d="{icon(slug)}" '
              f'fill="{CELESTE_HONDO if claro else CELESTE}"/>')
    d.t(x + pad + iw + gap, y + h / 2 + size * .36, text, "Outfit", 500, size, col)
    d.raw('</g>')
    return w


# ---------- 1. Cabecera ----------

def cabecera():
    W, H = 900, 380
    d = Doc(W, H, "Dennys Vela — Desarrollador de Software Full-Stack")
    common_defs(d)
    fondo_vivo(d, W, H, rx=30, seed=7, particulas=16)
    vidrio(d, 36, 36, W - 72, H - 72, rx=26, delay=0)

    eyebrow(d, 76, 96, "Desarrollador de software full-stack", delay=.15)
    titulo(d, 74, 170, [("Dennys ", False), ("Vela", True)], size=64, delay=.25)

    # Línea rotativa (sustituye al typing SVG externo)
    lineas = ["React + Node.js + PostgreSQL", "Proyectos en producción para clientes reales",
              "Kotlin + Spring Boot"]
    n, per = len(lineas), 3.2
    total = n * per
    a, b = per / total * 100, 0.12 / total * 100 * 4
    d.css.append(f"""
.rota{{opacity:0;animation:rota {total}s {CURVA} infinite}}.rota.primera{{opacity:1}}
@keyframes rota{{0%{{opacity:0;transform:translateY(10px)}}{b:.1f}%{{opacity:1;transform:none}}
{a-b:.1f}%{{opacity:1;transform:none}}{a:.1f}%{{opacity:0;transform:translateY(-8px)}}100%{{opacity:0}}}}
.cursor{{animation:parpadeo 1.1s steps(1) infinite}}@keyframes parpadeo{{50%{{opacity:0}}}}""")
    d.raw('<g class="entra" style="animation-delay:.4s">')
    d.t(76, 218, "›", "Outfit", 600, 22, CELESTE)
    for i, l in enumerate(lineas):
        d.raw(f'<g class="rota{" primera" if i == 0 else ""}" style="animation-delay:{i*per+.6:.1f}s;animation-fill-mode:backwards">')
        d.t(98, 218, l, "Outfit", 400, 21, TEXTO_SUAVE)
        lw = width(l, "Outfit", 400, 21)
        d.raw(f'<rect class="cursor" x="{98+lw+5:.0f}" y="201" width="2" height="21" fill="{CELESTE}"/></g>')
    # Si el usuario pide menos movimiento, se ve la primera línea fija.
    d.raw('</g>')

    x = 76
    for i, (txt, sl) in enumerate([("Quito, Ecuador", None), ("Titulación: SSWAP", None),
                                   ("Pasantía en MINTEL", None)]):
        w = chip(d, x, 268, txt, delay=.55 + i * .08, punto=True)
        x += w + 12

    # Orbe decorativo flotante
    d.css.append("""
.orbe{animation:flota 7s ease-in-out infinite alternate}
@keyframes flota{to{transform:translateY(-12px)}}
.gira{transform-origin:745px 180px;animation:gira 30s linear infinite}
@keyframes gira{to{transform:rotate(360deg)}}""")
    d.raw(f"""<g class="entra" style="animation-delay:.5s"><g class="orbe">
<circle class="gira" cx="745" cy="180" r="92" fill="none" stroke="{CELESTE}" stroke-opacity=".35" stroke-dasharray="3 9"/>
<circle cx="745" cy="180" r="70" fill="url(#vidrioFuerte)" stroke="{CELESTE}" stroke-opacity=".5"/>
<circle cx="745" cy="180" r="70" fill="none" stroke="#fff" stroke-opacity=".08" stroke-width="10"/>
<path d="M727 163 L710 180 L727 197 M763 163 L780 180 L763 197 M752 156 L738 204" fill="none"
 stroke="url(#acento)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M727 163 L710 180 L727 197 M763 163 L780 180 L763 197 M752 156 L738 204" fill="none"
 stroke="{CELESTE}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" filter="url(#brillo)" opacity=".7"/>
</g></g>""")
    d.save("cabecera.svg")


# ---------- 2. Botones ----------

def botones():
    # Primario: degradado celeste, texto casi negro
    txt = "Escríbeme"
    tw = width(txt, "Outfit", 600, 17)
    W, H = int(tw + 92), 56
    d = Doc(W, H, "Escríbeme por correo")
    common_defs(d)
    d.defs.append(f'<clipPath id="bc"><rect width="{W}" height="{H}" rx="14"/></clipPath>')
    d.raw(f'<rect width="{W}" height="{H}" rx="14" fill="url(#boton)"/>'
          f'<rect x="14" y="0" width="{W-28}" height="1.2" fill="#fff" opacity=".6"/>'
          f'<g clip-path="url(#bc)"><g class="cruza no-rm"><rect x="-200" y="-20" width="70" height="{H+40}" '
          f'fill="#fff" opacity=".35" transform="skewX(-20)"/></g></g>')
    # sobre
    d.raw(f'<g transform="translate(24 19)" fill="none" stroke="{TINTA}" stroke-width="1.8" stroke-linejoin="round">'
          f'<rect x="0" y="0" width="20" height="16" rx="3"/><path d="M1 2l9 7 9-7"/></g>')
    d.t(56, 34.5, txt, "Outfit", 600, 17, TINTA)
    d.raw(f'<path d="M{56+tw+10} 28h12m-5-5 5 5-5 5" fill="none" stroke="{TINTA}" stroke-width="2" '
          f'stroke-linecap="round" stroke-linejoin="round"/>')
    d.save("boton-correo.svg")

    # Secundario: cristal con borde blanco (con base oscura para verse bien en tema claro de GitHub)
    txt = "Ver repositorios"
    tw = width(txt, "Outfit", 600, 17)
    W = int(tw + 92)
    d = Doc(W, H, "Ver repositorios en GitHub")
    common_defs(d)
    d.raw(f'<rect width="{W}" height="{H}" rx="14" fill="{TINTA}"/>'
          f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="13.5" fill="url(#vidrio)" stroke="#fff" stroke-opacity=".28"/>'
          f'<rect x="14" y=".5" width="{W-28}" height="1" fill="url(#reflejo)"/>')
    d.raw(f'<path transform="translate(24 18) scale(.83)" d="{icon("github")}" fill="{TEXTO_CLARO}"/>')
    d.t(56, 34.5, txt, "Outfit", 600, 17, TEXTO_CLARO)
    d.raw(f'<path d="M{56+tw+10} 28h12m-5-5 5 5-5 5" fill="none" stroke="{CELESTE}" stroke-width="2" '
          f'stroke-linecap="round" stroke-linejoin="round"/>')
    d.save("boton-repos.svg")


# ---------- 3. Sobre mí ----------

def sobre_mi():
    W = 900
    items = [
        ("Formación", "Tecnología Superior en Desarrollo de Software en la PUCE.", "M4 9l8-4 8 4-8 4-8-4zm3 2v4c0 1.5 2.2 3 5 3s5-1.5 5-3v-4"),
        ("Pasantía en MINTEL", "Dashboard de datos abiertos con React y la API de CKAN.", "M4 19V9m5 10V5m5 14v-7m5 7V8"),
        ("Cómo trabajo", "Aplicaciones completas: autenticación, pruebas, CI y despliegue.", "M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6l7-3zm-3 9l2 2 4-4"),
        ("Ahora mismo", "Puliendo SSWAP, mi proyecto de titulación.", "M12 7v5l3 2m6-2a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"),
    ]
    cw, gap = (W - 72 - 24) / 2, 24
    ch = 124
    H = 168 + 2 * ch + gap + 40
    d = Doc(W, H, "Sobre mí")
    common_defs(d)
    fondo_vivo(d, W, H, rx=30, seed=3, intensidad=.75, particulas=10, rayas=False)
    eyebrow(d, 52, 66, "Sobre mí")
    titulo(d, 50, 116, [("Construyo aplicaciones ", False), ("de punta a punta", True)], size=34)
    for i, (h, txt, ic) in enumerate(items):
        cx = 36 + (i % 2) * (cw + gap)
        cy = 152 + (i // 2) * (ch + gap)
        dl = .2 + i * .1
        vidrio(d, cx, cy, cw, ch, rx=20, delay=dl)
        d.raw(f'<g class="entra" style="animation-delay:{dl}s">'
              f'<rect x="{cx+22}" y="{cy+24}" width="44" height="44" rx="12" fill="{CELESTE}" fill-opacity=".14" '
              f'stroke="{CELESTE}" stroke-opacity=".4"/>'
              f'<path transform="translate({cx+32} {cy+34})" d="{ic}" fill="none" stroke="{CELESTE}" '
              f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')
        d.t(cx + 84, cy + 46, h, "Sora", 600, 19, TEXTO_CLARO, ls=-.02)
        for j, line in enumerate(wrap(txt, "Outfit", 400, 16.5, cw - 108)):
            d.t(cx + 84, cy + 74 + j * 23, line, "Outfit", 400, 16.5, TEXTO_SUAVE)
        d.raw('</g>')
    d.save("sobre-mi.svg")


# ---------- 4. Tecnologías ----------

def tecnologias():
    W = 900
    grupos = [
        ("Frontend", [("React", "react"), ("Vite", "vite"), ("JavaScript", "javascript"),
                      ("TypeScript", "typescript"), ("Ionic", "ionic")]),
        ("Backend", [("Node.js", "nodedotjs"), ("Express", "express"), ("Kotlin", "kotlin"),
                     ("Spring Boot", "springboot"), ("Python", "python")]),
        ("Bases de datos", [("PostgreSQL", "postgresql"), ("MongoDB", "mongodb"), ("Supabase", "supabase")]),
        ("DevOps y herramientas", [("Docker", "docker"), ("GitHub Actions", "githubactions"), ("Linux", "linux"),
                                   ("Jest", "jest"), ("AWS EC2 · Cognito", "_aws")]),
    ]
    # medir filas
    x0, xmax, rowh, ygap = 250, W - 60, 38, 12
    layout, y = [], 168
    for nombre, techs in grupos:
        x, filas, pos = x0, 1, []
        for t, sl in techs:
            w = width(t, "Outfit", 500, 15) + 14 * 2 + 18 + 9
            if x + w > xmax:
                x, filas = x0, filas + 1
            pos.append((x, y + (filas - 1) * (rowh + ygap), t, sl))
            x += w + 10
        layout.append((nombre, y, pos))
        y += filas * (rowh + ygap) + 22
    H = int(y + 26)
    d = Doc(W, H, "Tecnologías")
    common_defs(d)
    # banda grafito translúcida
    fondo_vivo(d, W, H, rx=30, seed=11, intensidad=.55, particulas=8, rayas=False)
    d.raw(f'<rect width="{W}" height="{H}" rx="30" fill="#1a2028" fill-opacity=".55"/>')
    eyebrow(d, 52, 66, "Tecnologías")
    titulo(d, 50, 116, [("Mi caja de ", False), ("herramientas", True)], size=34)
    for gi, (nombre, gy, pos) in enumerate(layout):
        d.raw(f'<line x1="52" x2="{W-52}" y1="{gy-11}" y2="{gy-11}" stroke="#fff" stroke-opacity=".06"/>')
        d.raw(f'<g class="entra" style="animation-delay:{.15+gi*.1}s">')
        d.t(52, gy + 25, nombre, "Sora", 600, 15.5, TEXTO_CLARO, ls=-.01)
        d.raw('</g>')
        for ci, (x, y, t, sl) in enumerate(pos):
            chip(d, x, y, t, sl, delay=.2 + gi * .1 + ci * .04)
    d.save("tecnologias.svg")


# ---------- 5. Proyectos ----------

def cabecera_seccion(nombre, eyeb, partes, archivo, sub=None):
    W, H = 900, 150 if not sub else 178
    d = Doc(W, H, nombre)
    common_defs(d)
    fondo_vivo(d, W, H, rx=26, seed=len(archivo), intensidad=.7, particulas=7, rayas=False)
    eyebrow(d, 52, 62, eyeb)
    titulo(d, 50, 110, partes, size=34)
    if sub:
        d.t(52, 146, sub, "Outfit", 400, 17, TEXTO_SUAVE, cls="entra", extra='style="animation-delay:.2s"')
    d.save(archivo)


def proyecto(num, nombre, desc, stack, archivo):
    W, H = 900, 236
    m = 14  # margen para la sombra
    d = Doc(W, H, f"Proyecto {nombre}")
    common_defs(d)
    d.defs.append('<filter id="sombra" x="-10%" y="-20%" width="120%" height="150%">'
                  '<feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="#06080b" flood-opacity=".22"/></filter>')
    cx, cy, cw, chh = m, m - 4, W - 2 * m, H - 2 * m
    d.defs.append(f'<clipPath id="tarj"><rect x="{cx}" y="{cy}" width="{cw}" height="{chh}" rx="24"/></clipPath>')
    d.raw(f'<g class="entra"><rect x="{cx}" y="{cy}" width="{cw}" height="{chh}" rx="24" fill="#fff" '
          f'filter="url(#sombra)"/><rect x="{cx}" y="{cy}" width="{cw}" height="{chh}" rx="24" fill="#fff" '
          f'stroke="{TINTA}" stroke-opacity=".08"/>'
          f'<g clip-path="url(#tarj)"><rect x="{cx}" y="{cy}" width="{cw}" height="4" fill="url(#acento)"/>'
          f'<circle cx="{cx+cw-40}" cy="{cy+20}" r="120" fill="{CELESTE}" opacity=".07"/></g></g>')
    d.t(cx + 36, cy + 62, num, "Sora", 700, 15, CELESTE_HONDO, ls=.08, cls="entra")
    d.raw('<g class="entra" style="animation-delay:.08s">')
    d.t(cx + 76, cy + 64, nombre, "Sora", 700, 30, TINTA, ls=-.03)
    d.raw('</g>')
    lines = wrap(desc, "Outfit", 400, 17, 600)
    for j, line in enumerate(lines):
        d.t(cx + 36, cy + 102 + j * 25, line, "Outfit", 400, 17, PLOMO, cls="entra",
            extra='style="animation-delay:.14s"')
    x = cx + 36
    ychip = cy + chh - 60
    for i, (t, sl) in enumerate(stack):
        x += chip(d, x, ychip, t, sl, h=34, size=14, claro=True, delay=.2 + i * .04) + 8
    # "botón" ver repositorio
    bt = "Ver repositorio"
    bw = width(bt, "Outfit", 600, 15) + 66
    bx, by = cx + cw - bw - 30, cy + 34
    d.raw(f'<g class="entra" style="animation-delay:.2s"><rect x="{bx:.1f}" y="{by}" width="{bw:.1f}" height="44" rx="13" '
          f'fill="url(#boton)"/><rect x="{bx+13:.1f}" y="{by}" width="{bw-26:.1f}" height="1" fill="#fff" opacity=".6"/>')
    d.t(bx + 20, by + 27.5, bt, "Outfit", 600, 15, TINTA)
    tx = bx + 20 + width(bt, "Outfit", 600, 15) + 9
    d.raw(f'<path d="M{tx:.1f} 0h11m-4.5-4.5 4.5 4.5-4.5 4.5" transform="translate(0 {by+22})" fill="none" '
          f'stroke="{TINTA}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g>')
    d.save(archivo)


def cta():
    W, H = 900, 250
    d = Doc(W, H, "¿Construimos algo juntos? Escríbeme a dennysvela@hotmail.com")
    common_defs(d)
    fondo_vivo(d, W, H, rx=30, seed=21, intensidad=1.0, particulas=12)
    vidrio(d, 36, 32, W - 72, H - 64, rx=24, fuerte=True)
    eyebrow(d, W / 2, 86, "Hablemos", anchor="middle", delay=.1)
    titulo(d, W / 2, 134, [("¿Construimos algo ", False), ("juntos", True), ("?", False)],
           size=36, anchor="middle", delay=.18)
    d.t(W / 2, 170, "dennysvela@hotmail.com", "Outfit", 500, 18, TEXTO_SUAVE, anchor="middle",
        cls="entra", extra='style="animation-delay:.26s"')
    d.save("cta.svg")


if __name__ == "__main__":
    cabecera()
    botones()
    sobre_mi()
    tecnologias()
    cabecera_seccion("Proyectos destacados", "Proyectos destacados",
                     [("Lo que he ", False), ("construido", True)], "titulo-proyectos.svg")
    proyecto("01", "SSWAP",
             "Gestión para taller automotriz: citas, órdenes, tienda y chatbot con IA (Gemini). "
             "JWT con 4 roles, pruebas y CI.",
             [("React", "react"), ("Express", "express"), ("PostgreSQL", "postgresql"), ("MongoDB", "mongodb")],
             "proyecto-sswap.svg")
    proyecto("02", "TattoolShop",
             "E-commerce para estudio de tatuajes con 3 sucursales: carrito, pagos con PayPhone "
             "y panel de administración.",
             [("React", "react"), ("Express", "express"), ("Supabase", "supabase")],
             "proyecto-tattoolshop.svg")
    proyecto("03", "API REST Estudiantes",
             "API por capas (controller, service, repository).",
             [("Kotlin", "kotlin"), ("Spring Boot", "springboot")],
             "proyecto-api-estudiantes.svg")
    cabecera_seccion("Actividad en GitHub", "Actividad", [("En ", False), ("GitHub", True)],
                     "titulo-actividad.svg")
    cta()
