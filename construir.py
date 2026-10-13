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
    # Etapas de la producción: ruta en la portada y un carrusel con un video por etapa (solo se reproduce si la persona lo pide)
    etapas_indice = "".join(
        f'<li style="--i: {i - 1}"><a href="#etapas" data-etapa="{i - 1}"><span class="n" aria-hidden="true">{i}</span><span class="txt">{e(x["titulo"])}</span>'
        f'<span class="play" aria-hidden="true"><svg viewBox="0 0 24 24" width="24" height="24"><circle cx="12" cy="12" r="10.5" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M10 8.2v7.6l6-3.8z" fill="currentColor"/></svg></span>'
        f'<span class="sr"> (ver el video)</span></a></li>' for i, x in enumerate(D["etapas"], 1))
    camino = "".join(
        f'<li><button type="button" data-etapa="{i - 1}" aria-label="Etapa {i}: {e(x["titulo"])}">{i}</button></li>' for i, x in enumerate(D["etapas"], 1))
    etapas = "\n".join(
        f'<div class="lamina-etapa" data-titulo="{e(x["titulo"])}" data-contexto="{e(x["contexto"])}"{"" if i == 1 else " hidden"}>'
        f'<button type="button" class="play-grande" aria-label="Reproducir el video de la etapa {i}"><svg viewBox="0 0 24 24" width="34" height="34" aria-hidden="true"><path d="M8.5 5.5v13l10.5-6.5z" fill="currentColor"/></svg></button>'
        f'<video controls controlslist="nodownload" muted playsinline preload="none" poster="etapas/etapa_{i}.jpg" data-src="etapas/etapa_{i}.mp4" width="1280" height="720" aria-label="{e(x["alt"])}"></video></div>'
        for i, x in enumerate(D["etapas"], 1))
    # Recomendaciones: solo se muestran las marcadas para publicar (cita comparada con el documento firmado)
    recos = [r for r in D.get("recomendaciones", []) if r.get("publicar")]
    recomendaciones = "".join(
        f'<figure class="reco"><blockquote><p>“{e(r["cita"])}”</p></blockquote><figcaption><b>{e(r["nombre"])}</b>'
        f'<span>{e(r["cargo"])}</span><small>{e(r["contexto"])}</small></figcaption></figure>' for r in recos)
    seccion_recos = (f'<section class="ancho bloque recomendaciones" id="recomendaciones" aria-labelledby="t-recos"><h2 id="t-recos">Recomendaciones</h2>'
                     f'<div class="recos">{recomendaciones}</div></section>') if recos else ""
    casos_linea = "".join(f'<li><a href="casos/{c["id"]}.html">{e(c["titulo"])}</a><span>{e(c["contexto"])}</span></li>' for c in LISTA_CASOS)
    carrusel = "\n".join(
        f'      <figure class="sl{"" if i else " activa"}"><img src="hero/hero_{i + 1}.jpg" data-fijo="hero/hero_{i + 1}.jpg" data-gif="hero/hero_{i + 1}.gif" width="960" height="540" alt="{e(x["alt"])}"><figcaption class="sr">{e(x["titulo"])}. {e(x["texto"])}</figcaption></figure>'
        for i, x in enumerate(D["carrusel"]))
    puntos = "".join(f'<button type="button" aria-label="Etapa {i + 1}: {e(x["titulo"])}"></button>' for i, x in enumerate(D["carrusel"]))
    filtros = "".join(f'<button type="button" data-f="{k}" aria-pressed="{"true" if k == "todas" else "false"}">{e(v)}</button>' for k, v in D["filtros"])
    piezas = "\n".join(tarjeta(p) for p in D["destacadas"])
    mas = "\n".join(fila_mas(p) for p in D["mas"])
    proyectos = "".join(f'<article class="caso"><h3>{e(c["titulo"])}</h3><p class="donde">{e(c["donde"])}</p><p>{e(c["texto"])}</p></article>' for c in D["proyectos"])
    pasos = "".join(f"<li>{e(x)}</li>" for x in D["pasos"])
    inst = "".join(f"<li>{e(x)}</li>" for x in D["instituciones"])
    # Franja de logos: la secuencia se repite para que el desfile no tenga cortes; las copias se ocultan a lectores de pantalla
    # Se usan los logos ya en gris de images/marcas/franja/ (herramientas/hornear_marcas.py), a doble resolución
    def logo_franja(src):
        ruta = "images/marcas/franja/" + Path(src).stem + ".png"; w, h = Image.open(RAIZ / ruta).size
        return ruta, round(w * 52 / h), 52
    marcas = "".join(
        f'<li{"" if k == 0 else " aria-hidden=" + chr(34) + "true" + chr(34)}><img src="{r}" alt="{e(alt) if k == 0 else ""}" width="{w}" height="{h}" decoding="async"></li>'
        for k in range(4) for src, alt in D["marcas"] for r, w, h in [logo_franja(src)])
    ld = json.dumps({"@context": "https://schema.org", "@type": "Person", "name": S["nombre"],
                     "jobTitle": "Diseñador instruccional", "email": "mailto:" + S["correo"], "telephone": S["telefono"], "url": S["url"],
                     "address": {"@type": "PostalAddress", "addressLocality": "Talca", "addressCountry": "CL"},
                     "sameAs": [S["linkedin"]]}, ensure_ascii=False)
    plantilla = (RAIZ / "plantilla.html").read_text(encoding="utf-8")
    reemplazos = {
        "{{TITULO_PAGINA}}": e(S["nombre"] + ", diseño instruccional"),
        "{{DESCRIPCION}}": e(S["descripcion"]), "{{URL}}": e(S["url"]), "{{NOMBRE}}": e(S["nombre"]),
        "{{TITULAR}}": e(S["titulo"]), "{{ROL}}": e(S["rol"]), "{{BAJADA}}": e(S["bajada"]), "{{CORREO}}": e(S["correo"]),
        "{{LINKEDIN}}": e(S["linkedin"]), "{{TELEFONO}}": e(S["telefono"]), "{{TELEFONO_TEXTO}}": e(S["telefono_texto"]), "{{PRINCIPIOS}}": e(S["principios"]), "{{FORMACION}}": e(D["formacion_calidad"]["texto"]), "{{FORMACION_ENLACE}}": e(D["formacion_calidad"]["enlace"]), "{{FORMACION_ENLACE_TEXTO}}": e(D["formacion_calidad"]["enlace_texto"]), "{{CV}}": e(S["cv"]), "{{FILTROS}}": filtros, "{{PIEZAS}}": piezas, "{{CIFRAS}}": cifras, "{{CARRUSEL}}": carrusel, "{{PUNTOS}}": puntos, "{{CASOS}}": tarjetas_casos(LISTA_CASOS), "{{ETAPAS_INDICE}}": etapas_indice, "{{ETAPAS}}": etapas, "{{CAMINO}}": camino, "{{RECOMENDACIONES}}": seccion_recos, "{{CASOS_LINEA}}": casos_linea,
        "{{MAS}}": mas, "{{MARCAS}}": marcas, "{{MARCAS_UCM}}": e(D["marcas_ucm"]), "{{PROYECTOS}}": proyectos, "{{PASOS}}": pasos, "{{INSTITUCIONES}}": inst, "{{LD}}": ld,
    }
    for k, v in reemplazos.items():
        plantilla = plantilla.replace(k, v)
    assert "{{" not in plantilla, "Quedó un marcador sin reemplazar"
    (RAIZ / "index.html").write_text(plantilla, encoding="utf-8")


# Estudios de caso: datos/casos/*.json → casos/<id>.html
def casos():
    carpeta = RAIZ / "datos/casos"
    lista = sorted((json.loads(f.read_text(encoding="utf-8")) for f in carpeta.glob("*.json")), key=lambda c: c["orden"])
    por_id = {c["id"]: c for c in lista}
    plantilla = (RAIZ / "plantilla_caso.html").read_text(encoding="utf-8")
    for c in lista:
        sig = por_id.get(c.get("siguiente"), lista[0])
        pasos = []
        for p in c["pasos"]:
            cuerpo = "".join(f"<p>{e(x)}</p>" for x in p.get("parrafos", []))
            if "etapas" in p:
                cuerpo += '<ol class="etapas">' + "".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in p["etapas"]) + "</ol>"
            if "recursos" in p:
                cuerpo += '<div class="recursos">' + "".join(recurso(r) for r in p["recursos"]) + "</div>"
            if "tarjeta" in p:
                t = p["tarjeta"]
                cuerpo += (f'<div class="tarjeta"><small>{e(t["encabezado"])}</small><p>{t["html"]}</p>'
                           f'<div class="leyenda">' + "".join(f'<span class="{k}">{e(v)}</span>' for k, v in t.get("leyenda", [])) + "</div></div>")
            if "cifras" in p:
                cuerpo += '<ul class="cifras">' + "".join(
                    f'<li><b data-cuenta="{n}" data-sufijo="{e(suf)}">{n}{e(suf)}</b><span class="barra" aria-hidden="true"></span><p>{e(txt)}</p></li>'
                    for n, suf, txt in p["cifras"]) + "</ul>"
                if p.get("fuente"): cuerpo += f'<p class="fuente">{e(p["fuente"])}</p>'
            pasos.append(f'<section class="ancho paso" aria-labelledby="p{p["num"]}"><h2 id="p{p["num"]}"><small>{e(p["num"])}</small>{e(p["titulo"])}</h2><div class="cuerpo">{cuerpo}</div></section>')
        logos = "".join(f'<img src="{e(src)}" alt="{e(alt)}" loading="lazy">' for src, alt in c.get("logos", []))
        ficha = "".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in c["ficha"])
        url = S["url"] + f"casos/{c['id']}.html"
        pista = f'<track kind="subtitles" srclang="es" label="Español" src="{e(c["pista"])}" default>' if c.get("pista") else ""
        html_ = plantilla
        for k, v in {
            "{{TITULO_PAGINA}}": e(c["titulo"] + ", caso de diseño instruccional"), "{{DESCRIPCION}}": e(c["descripcion"]), "{{URL}}": e(url),
            "{{OG}}": e(S["url"] + "casos/" + c["poster"]), "{{CONTEXTO}}": e(c["contexto"]), "{{TITULO}}": e(c["titulo"]), "{{RESUMEN}}": e(c["resumen"]),
            "{{LOGOS}}": logos, "{{FICHA}}": ficha, "{{POSTER}}": e(c["poster"]), "{{VIDEO}}": e(c["video"]), "{{PISTA}}": pista, "{{VIDEO_PIE}}": e(c["video_pie"]),
            "{{PASOS}}": "\n".join(pasos), "{{SIG_URL}}": e(sig["id"] + ".html"), "{{SIG_TITULO}}": e(sig["titulo"]),
        }.items():
            html_ = html_.replace(k, v)
        assert "{{" not in html_, f"Marcador sin reemplazar en {c['id']}"
        (RAIZ / "casos" / f"{c['id']}.html").write_text(html_, encoding="utf-8")
    return lista


def recurso(r):
    pie = f'<b>{e(r["titulo"])}</b><p>{e(r["texto"])}</p>'
    clase = "medio doc" if r.get("doc") else "medio"
    img = f'<img src="{e(r["portada"])}" alt="{e(r["titulo"])}" loading="lazy">'
    if r["tipo"] == "enlace":
        return f'<article class="recurso"><a class="{clase}" href="{e(r["fuente"])}" target="_blank" rel="noopener">{img}</a>{pie}<a class="accion" href="{e(r["fuente"])}" target="_blank" rel="noopener">{e(r["accion"])}</a></article>'
    if r["tipo"] == "video": attr = f'data-video="{e(r["fuente"])}"'
    elif r["tipo"] == "iframe": attr = f'data-iframe="{e(r["fuente"])}"'
    else: attr = 'data-galeria="' + e("|".join(f"{a}::{b}" for a, b in r["galeria"])) + '"'
    return f'<article class="recurso"><button class="{clase}" type="button" {attr} data-titulo="{e(r["titulo"])}">{img}</button>{pie}<button class="accion" type="button" {attr} data-titulo="{e(r["titulo"])}">{e(r["accion"])}</button></article>'


def tarjetas_casos(lista):
    return "".join(
        f'<a class="caso-tarjeta" href="casos/{c["id"]}.html"><img src="casos/{c["poster"]}" alt="" loading="lazy" width="1280" height="720">'
        f'<span class="donde">{e(c["contexto"])}</span><strong>{e(c["titulo"])}</strong><span class="ver">Ver el caso y su video de proceso</span></a>'
        for c in lista)


if __name__ == "__main__":
    portadas()
    LISTA_CASOS = casos()
    pagina()
    print(f"Listo: index.html, {len(LISTA_CASOS)} casos y portadas_v2/")
