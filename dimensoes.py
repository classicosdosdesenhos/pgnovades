# -*- coding: utf-8 -*-
"""Le as dimensoes reais de cada imagem e cruza com o tamanho de exibicao."""
import io
import os
import re
import struct

DIR = "assets/img"


def dim_png(f):
    f.seek(16)
    return struct.unpack(">II", f.read(8))


def dim_jpg(f):
    f.seek(2)
    while True:
        b = f.read(1)
        while b and b != b"\xff":
            b = f.read(1)
        while b == b"\xff":
            b = f.read(1)
        if not b:
            return None
        m = b[0]
        if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7:
            continue
        tam = struct.unpack(">H", f.read(2))[0]
        if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            f.read(1)
            h, w = struct.unpack(">HH", f.read(4))
            return w, h
        f.seek(tam - 2, 1)


def dim_webp(f):
    f.seek(12)
    cab = f.read(4)
    if cab == b"VP8 ":
        f.seek(26)
        return struct.unpack("<HH", f.read(4))
    if cab == b"VP8L":
        f.seek(21)
        b = struct.unpack("<I", f.read(4))[0]
        return (b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1
    if cab == b"VP8X":
        f.seek(24)
        d = f.read(6)
        return (d[0] | d[1] << 8 | d[2] << 16) + 1, (d[3] | d[4] << 8 | d[5] << 16) + 1
    return None


def dimensoes(caminho):
    with open(caminho, "rb") as f:
        cab = f.read(4)
        f.seek(0)
        if cab[:4] == b"\x89PNG":
            return dim_png(f)
        if cab[:2] == b"\xff\xd8":
            return dim_jpg(f)
        if cab[:4] == b"RIFF":
            return dim_webp(f)
    return None


# ---- tamanho de exibicao, tirado do CSS e dos styles inline ----
EXIBICAO = {
    "carousel":  (220, 320, "desktop 220x320 / mobile 130x180, object-fit: cover"),
    "badge":     (70,  70,  "70px de largura, altura automatica"),
    "badge-mp4": (70,  70,  "70x70 fixo, object-fit: contain"),
    "bonus":     (250, 0,   "largura 100%, teto de 250px, altura livre"),
    "avatar":    (75,  75,  "75x75 circular, object-fit: cover"),
    "selo":      (280, 0,   "280px de largura, altura livre"),
    "poster":    (0,   0,   "fundo borrado do player, nao e visivel"),
}

html = io.open("index.html", encoding="utf-8").read()


def papel(arq):
    tag = re.search(r'<img[^>]*src="assets/img/%s"[^>]*>' % re.escape(arq), html)
    if not tag:
        return "poster" if "vsl-poster" in arq else None
    t = tag.group(0)
    if "carousel-item" in t:
        return "carousel"
    if "badge-image" in t:
        return "badge-mp4" if "height:70px" in t.replace(" ", "") else "badge"
    if "testi-avatar" in t:
        return "avatar"
    if "guarantee-badge" in t:
        return "selo"
    if "max-width: 250px" in t:
        return "bonus"
    return None


grupos = {}
for arq in sorted(os.listdir(DIR)):
    caminho = os.path.join(DIR, arq)
    d = dimensoes(caminho)
    p = papel(arq) or "?"
    grupos.setdefault(p, []).append(
        (arq, d, os.path.getsize(caminho)))

ORDEM = ["carousel", "bonus", "badge", "badge-mp4", "avatar", "selo", "poster", "?"]
TITULO = {
    "carousel": "CARROSSEL (topo da pagina)",
    "bonus": "MOCKUPS DOS BONUS",
    "badge": "ICONES DE FORMATO/ENTREGA",
    "badge-mp4": "ICONE MP4 (tem altura travada)",
    "avatar": "FOTOS DOS DEPOIMENTOS",
    "selo": "SELO DE GARANTIA",
    "poster": "POSTER DA VSL (gerado pelo Wistia)",
    "?": "SEM USO IDENTIFICADO",
}

for g in ORDEM:
    if g not in grupos:
        continue
    ex = EXIBICAO.get(g)
    print("\n" + "=" * 78)
    print(TITULO[g])
    if ex and ex[2]:
        print("exibido em: %s" % ex[2])
        if ex[0]:
            print("EXPORTAR EM 2x: %s" % (
                "%dx%d px" % (ex[0] * 2, ex[1] * 2) if ex[1]
                else "%d px de largura" % (ex[0] * 2)))
    print("-" * 78)
    print("%-42s %11s %9s %8s" % ("arquivo", "real", "proporcao", "peso"))
    for arq, d, tam in grupos[g]:
        if d:
            w, h = d
            r = w / float(h)
            prop = "%.2f:1" % r
            if abs(r - 0.6875) < 0.02:
                prop += " (11:16)"
            elif abs(r - 1) < 0.02:
                prop += " (1:1)"
            elif abs(r - 0.75) < 0.02:
                prop += " (3:4)"
            elif abs(r - 1.3333) < 0.02:
                prop += " (4:3)"
            print("%-42s %5dx%-5d %9s %6.0fKB" % (arq, w, h, prop, tam / 1024.0))
        else:
            print("%-42s %11s" % (arq, "?"))
