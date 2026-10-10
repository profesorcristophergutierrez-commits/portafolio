"""Genera index.html y las portadas optimizadas a partir de datos/piezas.json.

Uso: python3 construir.py
Las escenas originales están en fuentes_portadas/ (una por pieza destacada, con el id como nombre).
"""
import json
from html import escape
from pathlib import Path
from PIL import Image

RAIZ = Path(__file__).resolve().parent
D = json.loads((RAIZ / "datos/piezas.json").read_text(encoding="utf-8"))
S = D["sitio"]
e = lambda t: escape(str(t), quote=True)


# Portadas: WebP en dos tamaños y JPG de respaldo
def portadas():
    salida = RAIZ / "portadas_v2"; salida.mkdir(exist_ok=True)
    for p in D["destacadas"]:
        im = Image.open(RAIZ / "fuentes_portadas" / f"{p['id']}.jpg").convert("RGB")
        im = im.resize((928, round(928 * im.height / im.width)), Image.LANCZOS)
        im.save(salida / f"{p['id']}-928.webp", quality=80, method=6)
        im.save(salida / f"{p['id']}-928.jpg", quality=82, optimize=True, progressive=True)
        im.resize((464, round(464 * im.height / im.width)), Image.LANCZOS).save(salida / f"{p['id']}-464.webp", quality=80, method=6)


# Atributos que abren cada pieza en el visor
def accion(p):
    t = p["tipo"]
    if t == "video": return f'data-video="{e(p["fuente"])}"'
    if t == "iframe": return f'data-iframe="{e(p["fuente"])}"'
    if t == "galeria": return 'data-galeria="' + e("|".join(f"{a}::{b}" for a, b in p["galeria"])) + '"'
    if t == "juego": return 'data-juego'
    return ""


def tarjeta(p):
    img = (f'<picture><source type="image/webp" srcset="portadas_v2/{p["id"]}-464.webp 464w, portadas_v2/{p["id"]}-928.webp 928w" '
           f'sizes="(min-width: 1000px) 31vw, (min-width: 640px) 46vw, 92vw">'
           f'<img src="portadas_v2/{p["id"]}-928.jpg" width="928" height="1152" alt="{e(p["alt"])}" loading="lazy" decoding="async"></picture>')
    rotulo = f'<span class="rotulo"><span class="cat">{e(p["categoria"])}</span><span class="tit">{e(p["titulo"])}</span></span>'
    pie = f'<p class="detalle">{e(p["detalle"])}</p>'
    if p["tipo"] == "enlace":
        abrir = f'<a class="lamina" href="{e(p["fuente"])}" target="_blank" rel="noopener">{img}{rotulo}</a>'
        act = f'<a class="accion" href="{e(p["fuente"])}" target="_blank" rel="noopener">{e(p["accion"])}<span class="sr"> (se abre en otra pestaña)</span></a>'
    else:
        abrir = f'<button class="lamina" type="button" {accion(p)} data-titulo="{e(p["titulo"])}">{img}{rotulo}</button>'
        act = f'<button class="accion" type="button" {accion(p)} data-titulo="{e(p["titulo"])}">{e(p["accion"])}</button>'
    return f'<article class="pieza" data-filtro="{e(p["filtro"])}">{abrir}{pie}{act}</article>'


def fila_mas(p):
    return (f'<li><span><strong>{e(p["titulo"])}</strong>{e(p["detalle"])}</span>'
            f'<button class="accion" type="button" {accion(p)} data-titulo="{e(p["titulo"])}">{e(p["accion"])}</button></li>')


def pagina():
    cifras = "\n".join(
        f'<li><b data-cuenta="{c["valor"]}" data-sufijo="{e(c.get("sufijo", ""))}">{c["valor"]}{e(c.get("sufijo", ""))}</b><span class="barra" aria-hidden="true"></span><p>{e(c["texto"])}</p></li>'
        for c in D["cifras"])
    filtros = "".join(f'<button type="button" data-f="{k}" aria-pressed="{"true" if k == "todas" else "false"}">{e(v)}</button>' for k, v in D["filtros"])
    piezas = "\n".join(tarjeta(p) for p in D["destacadas"])
    mas = "\n".join(fila_mas(p) for p in D["mas"])
    proyectos = "".join(f'<article class="caso"><h3>{e(c["titulo"])}</h3><p class="donde">{e(c["donde"])}</p><p>{e(c["texto"])}</p></article>' for c in D["proyectos"])
    pasos = "".join(f"<li>{e(x)}</li>" for x in D["pasos"])
    inst = "".join(f"<li>{e(x)}</li>" for x in D["instituciones"])
    ld = json.dumps({"@context": "https://schema.org", "@type": "Person", "name": S["nombre"],
                     "jobTitle": "Diseñador instruccional", "email": "mailto:" + S["correo"], "url": S["url"],
                     "address": {"@type": "PostalAddress", "addressLocality": "Talca", "addressCountry": "CL"},
                     "sameAs": [S["linkedin"]]}, ensure_ascii=False)
    plantilla = (RAIZ / "plantilla.html").read_text(encoding="utf-8")
    reemplazos = {
        "{{TITULO_PAGINA}}": e(S["nombre"] + ", diseño instruccional"),
        "{{DESCRIPCION}}": e(S["descripcion"]), "{{URL}}": e(S["url"]), "{{NOMBRE}}": e(S["nombre"]),
        "{{TITULAR}}": e(S["titulo"]), "{{BAJADA}}": e(S["bajada"]), "{{CORREO}}": e(S["correo"]),
        "{{LINKEDIN}}": e(S["linkedin"]), "{{CV}}": e(S["cv"]), "{{FILTROS}}": filtros, "{{PIEZAS}}": piezas, "{{CIFRAS}}": cifras,
        "{{MAS}}": mas, "{{PROYECTOS}}": proyectos, "{{PASOS}}": pasos, "{{INSTITUCIONES}}": inst, "{{LD}}": ld,
    }
    for k, v in reemplazos.items():
        plantilla = plantilla.replace(k, v)
    assert "{{" not in plantilla, "Quedó un marcador sin reemplazar"
    (RAIZ / "index.html").write_text(plantilla, encoding="utf-8")


if __name__ == "__main__":
    portadas()
    pagina()
    print("Listo: index.html y portadas_v2/")
