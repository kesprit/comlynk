#!/usr/bin/env python3
"""Génère les visuels de la landing page, en français et en anglais.

    python3 tools/visuels.py

Écrit `assets/img/fr/` et `assets/img/en/`, plus les deux images de partage.
Seul Pillow est nécessaire : `python3 -m pip install Pillow`.

Pourquoi un script plutôt que des captures : les écrans doivent exister dans
les deux langues, et aucune donnée réelle ne doit figurer sur la page. Tout
ce qui est affiché ici — personnes, cartes, numéros, domaines, adresse — est
inventé. Les numéros utilisent la plage 06 39 98 xx xx que l'ARCEP réserve à
la fiction.

Deux techniques coexistent :

  * les écrans d'interface (liste, fiches) sont redessinés avec SF Pro, à
    partir des mesures relevées sur les captures d'origine ;
  * les écrans de scan partent de `tools/source/scene.jpg`, la photo réelle de
    la table vidée de sa carte et de ses textes ; on y projette une carte en
    perspective, rééclairée d'après la luminance de la scène, puis on écrit
    les textes de l'appareil photo dans la langue voulue.

Les polices utilisées sont celles de macOS (SF Pro, Didot, Baskerville,
Avenir Next). Sur un autre système, adapter les chemins ci-dessous.
"""

import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageStat

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(RACINE, "tools", "source", "scene.jpg")
IMG = os.path.join(RACINE, "assets", "img")

# ---------------------------------------------------------------------------
# Polices
# ---------------------------------------------------------------------------

LIB, SUP, SYS = "/Library/Fonts/", "/System/Library/Fonts/Supplemental/", "/System/Library/Fonts/"

TXT_R = lambda s: ImageFont.truetype(LIB + "SF-Pro-Text-Regular.otf", s)
TXT_M = lambda s: ImageFont.truetype(LIB + "SF-Pro-Text-Medium.otf", s)
TXT_SB = lambda s: ImageFont.truetype(LIB + "SF-Pro-Text-Semibold.otf", s)
TXT_B = lambda s: ImageFont.truetype(LIB + "SF-Pro-Text-Bold.otf", s)
DIS_B = lambda s: ImageFont.truetype(LIB + "SF-Pro-Display-Bold.otf", s)
DIDOT = lambda s: ImageFont.truetype(SUP + "Didot.ttc", s, index=0)
DIDOT_B = lambda s: ImageFont.truetype(SUP + "Didot.ttc", s, index=2)
BASK_I = lambda s: ImageFont.truetype(SUP + "Baskerville.ttc", s, index=2)
AV_R = lambda s: ImageFont.truetype(SYS + "Avenir Next.ttc", s, index=7)
AV_M = lambda s: ImageFont.truetype(SYS + "Avenir Next.ttc", s, index=5)
AV_D = lambda s: ImageFont.truetype(SYS + "Avenir Next.ttc", s, index=2)

# ---------------------------------------------------------------------------
# Couleurs
# ---------------------------------------------------------------------------

CREME = (252, 247, 243)
ENCRE = (28, 28, 30)
GRIS = (152, 148, 145)
GRIS_V = (160, 156, 153)
BLANC = (255, 255, 255)
CORAIL = (226, 61, 31)
CORAIL_VIF = (238, 75, 34)
SEPARATEUR = (238, 233, 229)

W = 601

# ---------------------------------------------------------------------------
# Textes — tout ce qui change d'une langue à l'autre
# ---------------------------------------------------------------------------

T = {
    "fr": {
        "scan_pret": "Prêt pour le scan suivant.",
        "flash": "Flash", "filtres": "Filtres", "obturateur": "Obturateur",
        "titre_liste": "Cartes de visite",
        "fermer": "Fermer",
        "nom": "Nom", "fonction": "Fonction", "telephone": "Téléphone",
        "email": "Email", "site": "Site web", "reseau": "Réseau",
        "adresse": "Adresse", "texte_reconnu": "Texte reconnu",
        "plans": "Plans", "mentions": "Mentions légales",
        "voie_1": "ROUTE DES PEUPLIERS", "voie_2": "CHEMIN DES AULNES",
        "etang": "Étang\ndu Breuil",
        "metier_a": "Illustratrice · Muraliste",
        "metier_b": "Fondateur",
        "bas_b": "Identité & direction artistique",
        "og_titre_1": "Vos cartes de visite,", "og_titre_2": "enfin ", "og_accent": "rangées.",
        "og_badge": "Gratuit sur iPhone · iOS 26",
        "og_bouton": "Télécharger dans l’App Store",
    },
    "en": {
        "scan_pret": "Ready for the next scan.",
        "flash": "Flash", "filtres": "Filters", "obturateur": "Shutter",
        "titre_liste": "Business cards",
        "fermer": "Close",
        "nom": "Name", "fonction": "Title", "telephone": "Phone",
        "email": "Email", "site": "Website", "reseau": "Social",
        "adresse": "Address", "texte_reconnu": "Recognised text",
        "plans": "Maps", "mentions": "Legal",
        "voie_1": "ROUTE DES PEUPLIERS", "voie_2": "CHEMIN DES AULNES",
        "etang": "Étang\ndu Breuil",
        "metier_a": "Illustrator · Muralist",
        "metier_b": "Founder",
        "bas_b": "Brand & art direction",
        "og_titre_1": "Your business cards,", "og_titre_2": "finally ", "og_accent": "filed.",
        "og_badge": "Free on iPhone · iOS 26",
        "og_bouton": "Download on the App Store",
    },
}

# Les personnes et leurs coordonnées : identiques dans les deux langues.
LEA = {"nom": "Léa Vasseur", "tel": "06 39 98 21 04",
       "mail": "contact@leavasseur.fr", "site": "leavasseur.fr", "reseau": "lea.vsr"}
THOMAS = {"nom": "Thomas Garnier", "tel": "+33 6 39 98 14 78",
          "mail": "thomas@orva-studio.fr", "site": "orva-studio.fr"}
CAMILLE = {"nom": "Camille BERTHIER", "tel": "06 39 98 47 12",
           "mail": "camille@orva-studio.fr",
           "adresse": ["24 Route des Peupliers, 01400", "Châtillon-sur-Chalaronne"]}


# ---------------------------------------------------------------------------
# Outils de dessin
# ---------------------------------------------------------------------------

def tracked(d, xy, texte, fnt, fill, tr=0, droite=False):
    """Texte avec interlettrage — Pillow ne le gère pas nativement."""
    x, y = xy
    if droite:
        x -= sum(fnt.getlength(c) + tr for c in texte) - tr
    for c in texte:
        d.text((x, y), c, font=fnt, fill=fill)
        x += fnt.getlength(c) + tr
    return x


def centre(d, y, texte, fnt, fill, largeur=W):
    d.text(((largeur - d.textlength(texte, font=fnt)) / 2, y), texte, font=fnt, fill=fill)


def grain(im, force=5, graine=1):
    rnd = random.Random(graine)
    bruit = Image.new("L", im.size)
    bruit.putdata([128 + rnd.randint(-force, force) for _ in range(im.width * im.height)])
    return Image.merge("RGB", [Image.blend(ch, bruit, 0.055) for ch in im.split()[:3]])


# ---------------------------------------------------------------------------
# Les trois cartes de visite
# ---------------------------------------------------------------------------

def carte_a(t):
    """Portrait 55 x 85 mm, claire et colorée."""
    im = Image.new("RGB", (880, 1360), (246, 223, 224))
    d = ImageDraw.Draw(im)

    cx, cy, r = 600, 268, 142
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(106, 162, 173))
    f = DIDOT_B(205)
    bb = d.textbbox((0, 0), "L.", font=f)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]),
           "L.", font=f, fill=(234, 242, 243))

    x = 98
    d.text((x, 540), LEA["nom"], font=DIDOT_B(84), fill=(29, 26, 46))
    tracked(d, (x + 2, 668), t["metier_a"], AV_M(45), (58, 51, 80), 0.6)
    d.rectangle([x, 742, 666, 751], fill=(92, 42, 99))
    d.rectangle([684, 742, 730, 751], fill=(232, 96, 47))
    d.text((x, 812), LEA["tel"], font=AV_R(41), fill=(64, 56, 79))
    d.text((x, 874), LEA["mail"], font=AV_R(41), fill=(64, 56, 79))

    d.rectangle([0, 1132, 880, 1360], fill=(240, 160, 42))

    def globe(gx, gy, s=17):
        d.ellipse([gx - s, gy - s, gx + s, gy + s], outline=BLANC, width=3)
        d.line([gx - s, gy, gx + s, gy], fill=BLANC, width=3)
        d.arc([gx - s * 0.52, gy - s, gx + s * 0.52, gy + s], 0, 360, fill=BLANC, width=3)

    def insta(gx, gy, s=17):
        d.rounded_rectangle([gx - s, gy - s, gx + s, gy + s], radius=9, outline=BLANC, width=3)
        d.ellipse([gx - s * 0.45, gy - s * 0.45, gx + s * 0.45, gy + s * 0.45], outline=BLANC, width=3)
        d.ellipse([gx + s * 0.42, gy - s * 0.72, gx + s * 0.72, gy - s * 0.42], fill=BLANC)

    fb = AV_D(35)
    globe(118, 1246)
    d.text((152, 1228), LEA["site"], font=fb, fill=BLANC)
    insta(502, 1246)
    d.text((536, 1228), LEA["reseau"], font=fb, fill=BLANC)

    return grain(im, 5, 11)


def degrade_texte(base, xy, texte, fnt, couleurs, tr=0, angle=150):
    """Texte rempli par un dégradé — la dorure de la carte noire."""
    w, h = base.size
    masque = Image.new("L", (w, h), 0)
    tracked(ImageDraw.Draw(masque), xy, texte, fnt, 255, tr)

    grad = Image.new("RGB", (w, h))
    gd = ImageDraw.Draw(grad)
    rad = math.radians(angle)
    dx, dy = math.cos(rad), math.sin(rad)
    span = abs(w * dx) + abs(h * dy)
    for i in range(int(span)):
        u = i / max(span - 1, 1)
        if u < 0.45:
            k = u / 0.45
            c = tuple(int(couleurs[0][j] + (couleurs[1][j] - couleurs[0][j]) * k) for j in range(3))
        else:
            k = (u - 0.45) / 0.55
            c = tuple(int(couleurs[1][j] + (couleurs[2][j] - couleurs[1][j]) * k) for j in range(3))
        if abs(dx) > abs(dy):
            px = i if dx > 0 else w - i
            gd.line([(px, 0), (px, h)], fill=c)
        else:
            py = i if dy > 0 else h - i
            gd.line([(0, py), (w, py)], fill=c)
    base.paste(grad, (0, 0), masque)


def carte_b(t):
    """Paysage 85 x 55 mm, fond noir et dorure."""
    im = Image.new("RGB", (1360, 880), (10, 11, 16))
    d = ImageDraw.Draw(im)
    for y in range(880):
        v = int(21 - 9 * abs(y / 880 - 0.35) * 2)
        d.line([(0, y), (1360, y)], fill=(max(v, 8), max(v - 1, 8), max(v + 5, 13)))

    OR = [(246, 229, 174), (176, 141, 62), (242, 223, 164)]
    degrade_texte(im, (100, 118), THOMAS["nom"].upper(), AV_D(56), OR, tr=4.5)
    d = ImageDraw.Draw(im)
    tracked(d, (102, 206), t["metier_b"], AV_R(38), (156, 138, 94), 1.6)
    d.text((100, 318), THOMAS["mail"], font=AV_R(36), fill=(200, 184, 135))
    d.text((100, 378), THOMAS["tel"], font=AV_R(36), fill=(200, 184, 135))

    degrade_texte(im, (990, 90), "O", DIDOT(360), OR, angle=140)
    d = ImageDraw.Draw(im)
    d.line([(100, 700), (1260, 700)], fill=(233, 216, 166), width=2)
    tracked(d, (100, 730), t["bas_b"], AV_R(31), (168, 151, 106), 1.4)
    tracked(d, (1260, 712), "ORVA", DIDOT(58), (228, 210, 160), 13, droite=True)

    return grain(im, 4, 23)


def carte_c(t):
    """Paysage 85 x 55 mm, illustrée, portant une adresse."""
    W_, H_ = 1360, 880
    lavis = Image.new("RGB", (W_, H_), BLANC)
    wd = ImageDraw.Draw(lavis, "RGBA")
    teintes = [(228, 85, 107), (240, 160, 42), (217, 79, 138), (242, 193, 78),
               (201, 63, 92), (240, 138, 60)]
    rnd = random.Random(12)
    for _ in range(90):
        s = rnd.randint(30, 250)
        px, py = rnd.randint(600, 1340), rnd.randint(30, 820)
        wd.ellipse([px, py, px + s, py + int(s * rnd.uniform(0.6, 1.3))],
                   fill=rnd.choice(teintes) + (rnd.randint(28, 105),))
    for _ in range(140):
        s = rnd.randint(4, 26)
        px, py = rnd.randint(520, 1350), rnd.randint(10, 860)
        wd.ellipse([px, py, px + s, py + s], fill=rnd.choice(teintes) + (rnd.randint(40, 150),))
    lavis = lavis.filter(ImageFilter.GaussianBlur(3))
    im = ImageChops.multiply(Image.new("RGB", (W_, H_), (253, 251, 247)), lavis)

    d = ImageDraw.Draw(im)
    x = 92
    prenom, nom = CAMILLE["nom"].split(" ", 1)
    f1, f2 = DIDOT(76), DIDOT_B(76)
    d.text((x, 108), prenom + " ", font=f1, fill=(181, 72, 90))
    tracked(d, (x + d.textlength(prenom + " ", font=f1), 108), nom, f2, (142, 47, 64), 3)

    fa = BASK_I(37)
    lignes = [CAMILLE["adresse"][0].replace(", 01400", ""), "01400 " + CAMILLE["adresse"][1],
              CAMILLE["tel"], CAMILLE["mail"]]
    for i, ligne in enumerate(lignes):
        d.text((x, 548 + i * 62), ligne, font=fa, fill=(87, 69, 69))

    return grain(im, 4, 5)


# ---------------------------------------------------------------------------
# Écrans de scan : incrustation d'une carte dans la photo
# ---------------------------------------------------------------------------

PAPIER = [(94, 331), (482, 328), (485, 934), (89, 942)]
LISERE = [(99, 337), (477, 334), (480, 929), (94, 936)]
QUAD_B = [(72, 455), (527, 441), (534, 760), (66, 777)]
LISERE_B = [(78, 461), (521, 447), (528, 754), (72, 771)]
VIGNETTE = (68, 1127, 134, 1220)


def coefficients(dest, source):
    """Homographie pour Image.transform(PERSPECTIVE) : sortie -> entrée."""
    m, b = [], []
    for (x, y), (u, v) in zip(dest, source):
        m.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        m.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        b.extend([u, v])
    n = 8
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(m[r][i]))
        m[i], m[p] = m[p], m[i]
        b[i], b[p] = b[p], b[i]
        piv = m[i][i]
        for j in range(i, n):
            m[i][j] /= piv
        b[i] /= piv
        for r in range(n):
            if r != i and m[r][i]:
                f = m[r][i]
                for j in range(i, n):
                    m[r][j] -= f * m[i][j]
                b[r] -= f * b[i]
    return b


def projette(carte, quad, taille):
    w, h = carte.size
    out = carte.convert("RGBA").transform(
        taille, Image.PERSPECTIVE, coefficients(quad, [(0, 0), (w, 0), (w, h), (0, h)]),
        Image.BICUBIC)
    masque = Image.new("L", taille, 0)
    ImageDraw.Draw(masque).polygon(quad, fill=255)
    out.putalpha(masque.filter(ImageFilter.GaussianBlur(0.6)))
    return out


def reeclaire(carte, scene, quad):
    """Recale l'exposition de la carte sur la scène et lui rend son modelé."""
    masque = Image.new("L", scene.size, 0)
    ImageDraw.Draw(masque).polygon(quad, fill=255)
    dedans = [m > 128 for m in masque.getdata()]

    lum = scene.convert("L")
    vals = [v for v, m in zip(lum.getdata(), dedans) if m]
    moy = sum(vals) / len(vals)

    plat = Image.new("L", scene.size, int(moy))
    plat.paste(lum, (0, 0), masque)
    modele = plat.filter(ImageFilter.GaussianBlur(22))
    table = [max(0.55, min(1.45, 1 + (i - moy) / moy * 0.55)) for i in range(256)]
    mult = modele.point(lambda i: int(table[i] * 128))

    vc = [v for v, m in zip(carte.convert("L").getdata(), dedans) if m]
    gain = min(1.3, max(0.7, moy / max(sum(vc) / max(len(vc), 1), 1)))

    r, g, b, a = carte.split()
    return Image.merge("RGBA", [
        ImageChops.multiply(ch, mult).point(lambda v: min(255, int(v * 2 * gain)))
        for ch in (r, g, b)] + [a])


def pose(scene, carte, quad, lisere):
    c = projette(carte, quad, scene.size)
    c = reeclaire(c, scene, quad)
    rgb = Image.merge("RGB", c.split()[:3]).filter(ImageFilter.GaussianBlur(0.85))
    c = Image.merge("RGBA", list(rgb.split()) + [c.split()[3]])

    out = scene.convert("RGB").copy()
    out.paste(c, (0, 0), c)
    couche = Image.new("RGBA", scene.size, (0, 0, 0, 0))
    ImageDraw.Draw(couche).polygon(lisere, outline=(232, 80, 42, 205), width=3)
    return Image.alpha_composite(out.convert("RGBA"), couche).convert("RGB")


def vignette(scene, carte):
    x0, y0, x1, y1 = VIGNETTE
    w, h = x1 - x0, y1 - y0
    mini = carte.convert("RGB").resize((w, h), Image.LANCZOS)
    mini = Image.eval(mini, lambda v: min(255, int(v * 1.14 + 14))).filter(ImageFilter.GaussianBlur(0.3))
    coins = Image.new("L", (w, h), 0)
    ImageDraw.Draw(coins).rounded_rectangle([0, 0, w - 1, h - 1], radius=3, fill=255)
    out = scene.copy()
    out.paste(mini, (x0, y0), coins)
    return out


def textes_appareil(im, t):
    """Écrit les textes de l'appareil photo : la pastille et les trois libellés."""
    couche = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(couche)

    f = TXT_SB(28)
    tw = d.textlength(t["scan_pret"], font=f)
    x0, x1 = (W - tw) / 2 - 24, (W + tw) / 2 + 24
    d.rounded_rectangle([x0, 149, x1, 193], radius=22, fill=(12, 10, 8, 178))
    d.text(((W - tw) / 2, 157), t["scan_pret"], font=f, fill=(255, 255, 255, 240))

    # Les trois libellés sont centrés sous leur bouton ; on réduit la police
    # tant que deux voisins se touchent (« Obturateur » est long).
    centres = (190, 301, 412)
    mots = (t["flash"], t["filtres"], t["obturateur"])
    taille = 25
    while taille > 17:
        fl = TXT_M(taille)
        larg = [d.textlength(m, font=fl) for m in mots]
        if all(centres[i] + larg[i] / 2 + 7 <= centres[i + 1] - larg[i + 1] / 2
               for i in range(len(mots) - 1)):
            break
        taille -= 1
    fl = TXT_M(taille)
    for cx, mot in zip(centres, mots):
        lw = d.textlength(mot, font=fl)
        d.text((cx - lw / 2 + 1, 1091), mot, font=fl, fill=(0, 0, 0, 70))
        d.text((cx - lw / 2, 1090), mot, font=fl, fill=(255, 255, 255, 236))

    return Image.alpha_composite(im.convert("RGBA"), couche).convert("RGB")


# ---------------------------------------------------------------------------
# Écrans d'interface
# ---------------------------------------------------------------------------

def barre_etat(d):
    c = (0, 0, 0)
    d.text((70, 27), "17:17", font=TXT_SB(31), fill=c)
    fx, fy = 162, 30
    d.polygon([(fx + 19, fy), (fx - 1, fy + 9), (fx + 7, fy + 12), (fx + 9, fy + 21)], fill=c)
    for i in range(4):
        h = 8 + i * 5
        d.rounded_rectangle([429 + i * 12, 52 - h, 437 + i * 12, 52], radius=2,
                            fill=c if i < 2 else (189, 187, 185))
    for r in (21, 13):
        d.arc([494 - r, 53 - r, 494 + r, 53 + r], 213, 327, fill=c, width=6)
    d.ellipse([490, 45, 498, 53], fill=c)
    d.rounded_rectangle([521, 31, 562, 53], radius=7, fill=(26, 26, 26))
    d.rounded_rectangle([564, 38, 568, 46], radius=2, fill=(158, 156, 154))
    fb = TXT_B(17)
    d.text((521 + (41 - d.textlength("61", font=fb)) / 2, 33), "61", font=fb, fill=BLANC)


def feuille(img, y0=86):
    f = Image.new("RGB", (W, img.height - y0), CREME)
    m = Image.new("L", f.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, W - 1, f.height + 60], radius=38, fill=255)
    img.paste(f, (0, y0), m)


def photo_carte(img, carte, boite, rayon=16, decalage=0):
    x0, y0, x1, y1 = boite
    bw, bh = x1 - x0, y1 - y0
    c = carte.convert("RGB")
    k = max(bw / c.width, bh / c.height)
    c = c.resize((max(1, int(c.width * k)), max(1, int(c.height * k))), Image.LANCZOS)
    gx = (c.width - bw) // 2
    gy = max(0, c.height - bh + decalage)
    c = c.crop((gx, gy, gx + bw, gy + bh))

    lum = Image.new("L", (bw, bh))
    ld = ImageDraw.Draw(lum)
    for y in range(bh):
        ld.line([(0, y), (bw, y)], fill=int(132 - 16 * (y / bh)))
    c = Image.merge("RGB", [ImageChops.multiply(ch, lum).point(lambda v: min(255, int(v * 2)))
                            for ch in c.split()])

    ombre = Image.new("L", img.size, 0)
    ImageDraw.Draw(ombre).rounded_rectangle([x0 + 4, y0 + 8, x1 - 4, y1 + 6], radius=rayon, fill=64)
    img.paste(Image.new("RGB", img.size, (120, 108, 100)), (0, 0), ombre.filter(ImageFilter.GaussianBlur(10)))

    m = Image.new("L", (bw, bh), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=rayon, fill=255)
    img.paste(c, (x0, y0), m)


def bloc_champs(d, boite, lignes):
    x0, y0, x1, y1 = boite
    d.rounded_rectangle([x0, y0, x1, y1], radius=22, fill=BLANC)
    PAD, fl = 27, TXT_R(29)
    y = y0 + 26
    for i, (label, valeur, pleine) in enumerate(lignes):
        if i:
            d.line([(x0 + PAD, y - 17), (x1 - PAD, y - 17)], fill=SEPARATEUR, width=2)
        d.text((x0 + PAD, y), label, font=fl, fill=ENCRE)
        if pleine:
            yy = y + 44
            for ligne in valeur:
                d.text((x0 + PAD, yy), ligne, font=TXT_R(29), fill=GRIS_V)
                yy += 40
            y = yy + 22
        else:
            dispo = (x1 - PAD) - (x0 + PAD + d.textlength(label, font=fl) + 26)
            taille = 29
            fv = TXT_R(taille)
            while d.textlength(valeur, font=fv) > dispo and taille > 21:
                taille -= 1
                fv = TXT_R(taille)
            d.text((x1 - PAD - d.textlength(valeur, font=fv), y + (29 - taille) * 0.45),
                   valeur, font=fv, fill=GRIS_V)
            y += 72
    return y - 16


def plan(taille, etiquette, t):
    w, h = taille
    im = Image.new("RGB", (w, h), (242, 239, 232))
    d = ImageDraw.Draw(im, "RGBA")
    rnd = random.Random(4)
    for _ in range(9):
        x, y = rnd.randint(-60, w), rnd.randint(-40, h)
        d.ellipse([x, y, x + rnd.randint(150, 330), y + rnd.randint(90, 200)],
                  fill=(206, 224, 180, 220))
    d.ellipse([w * 0.72, h * 0.44, w * 1.06, h * 1.02], fill=(166, 213, 236, 255))
    d.ellipse([w * 0.66, h * 0.72, w * 0.94, h * 1.1], fill=(166, 213, 236, 255))

    routes = [[(-20, h * 0.28), (w * 0.34, h * 0.36), (w * 0.62, h * 0.2), (w + 20, h * 0.1)],
              [(w * 0.46, -20), (w * 0.5, h * 0.42), (w * 0.38, h * 0.74), (w * 0.44, h + 20)],
              [(-20, h * 0.86), (w * 0.3, h * 0.78), (w * 0.58, h * 0.9), (w + 20, h * 0.8)]]
    for pts in routes:
        d.line(pts, fill=(214, 210, 203, 255), width=15, joint="curve")
    for pts in routes:
        d.line(pts, fill=(255, 255, 255, 255), width=10, joint="curve")

    f = TXT_M(15)
    d.text((w * 0.08, h * 0.22), t["voie_1"], font=f, fill=(150, 146, 140))
    d.text((w * 0.62, h * 0.24), t["voie_2"], font=f, fill=(150, 146, 140))
    d.text((w * 0.80, h * 0.86), t["etang"], font=TXT_M(16), fill=(92, 134, 160))

    px, py = w * 0.5, h * 0.44
    d.ellipse([px - 19, py - 19, px + 19, py + 19], fill=(201, 58, 46, 255))
    d.ellipse([px - 19, py - 19, px + 19, py + 19], outline=(255, 255, 255, 255), width=4)
    d.polygon([(px - 7, py + 15), (px + 7, py + 15), (px, py + 27)], fill=(201, 58, 46, 255))
    d.ellipse([px - 5, py - 7, px + 5, py + 9], fill=(255, 255, 255, 190))
    fe = TXT_SB(19)
    d.text((px - d.textlength(etiquette, font=fe) / 2, py + 34), etiquette, font=fe, fill=(44, 42, 40))

    d.text((12, h - 30), " " + t["plans"], font=TXT_M(19), fill=(70, 68, 66))
    d.text((12 + d.textlength(" " + t["plans"], font=TXT_M(19)) + 14, h - 26),
           t["mentions"], font=TXT_M(15), fill=(120, 118, 114))
    return im


def ecran_liste(t, carte):
    img = Image.new("RGB", (W, 974), CREME)
    d = ImageDraw.Draw(img)
    barre_etat(d)

    cx, cy = 545, 114
    halo = Image.new("L", img.size, 0)
    ImageDraw.Draw(halo).ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=70)
    img.paste(Image.new("RGB", img.size, BLANC), (0, 0), halo.filter(ImageFilter.GaussianBlur(9)))
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 27, cy - 27, cx + 27, cy + 27], fill=CORAIL)
    d.rounded_rectangle([cx - 16, cy - 9, cx + 16, cy + 13], radius=6, outline=BLANC, width=4)
    d.line([(cx - 7, cy - 9), (cx - 4, cy - 15)], fill=BLANC, width=4)
    d.line([(cx - 4, cy - 15), (cx + 4, cy - 15)], fill=BLANC, width=4)
    d.line([(cx + 4, cy - 15), (cx + 7, cy - 9)], fill=BLANC, width=4)
    d.ellipse([cx - 7, cy - 3, cx + 7, cy + 11], outline=BLANC, width=4)

    d.text((30, 160), t["titre_liste"], font=DIS_B(50), fill=(15, 13, 12))
    d.rounded_rectangle([30, 240, 571, 356], radius=24, fill=BLANC)
    d.text((55, 258), LEA["nom"], font=TXT_SB(30), fill=ENCRE)
    d.text((55, 294), t["metier_a"], font=TXT_R(28), fill=GRIS)
    d.text((55, 326), LEA["mail"], font=TXT_R(28), fill=GRIS)
    return img


def ecran_fiche(t, titre, carte, lignes, hauteur=974, boite=(28, 92, 573, 632),
                rayon=16, decalage=0, avec_plan=False, etiquette=""):
    HV = 150
    voile = Image.new("L", (W, HV), 0)
    vd = ImageDraw.Draw(voile)
    for y in range(HV):
        vd.line([(0, y), (W, y)], fill=int(255 * (1 - y / HV) ** 0.9))

    def dessine(fin=None):
        img = Image.new("RGB", (W, hauteur), CREME)
        ImageDraw.Draw(img).rectangle([0, 0, W, 86], fill=(202, 197, 194))
        feuille(img)
        photo_carte(img, carte, boite, rayon=rayon, decalage=decalage)
        img.paste(Image.new("RGB", (W, HV), CREME), (0, 86), voile)
        d = ImageDraw.Draw(img)
        barre_etat(d)
        ft = TXT_B(29)
        centre(d, 128, titre, ft, ENCRE)
        d.rounded_rectangle([455, 112, 578, 174], radius=31, fill=BLANC)
        ff = TXT_SB(28)
        d.text((455 + (123 - d.textlength(t["fermer"], font=ff)) / 2, 130),
               t["fermer"], font=ff, fill=ENCRE)
        y0 = boite[3] + 46
        bas = bloc_champs(d, (28, y0, 573, fin if fin else y0 + 1), lignes)
        return img, d, y0, bas

    _, _, y0, bas = dessine()
    img, d, _, _ = dessine(bas)

    if avec_plan:
        py = bas + 24
        p = plan((545, min(300, hauteur - py - 20)), etiquette, t)
        m = Image.new("L", p.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, p.width - 1, p.height - 1], radius=22, fill=255)
        img.paste(p, (28, py), m)
    else:
        d.rounded_rectangle([28, bas + 24, 573, bas + 104], radius=22, fill=BLANC)
        d.text((55, bas + 48), t["texte_reconnu"], font=TXT_R(29), fill=ENCRE)
        cx, cy = 535, bas + 64
        d.line([(cx - 6, cy - 10), (cx + 4, cy)], fill=(176, 172, 169), width=4)
        d.line([(cx + 4, cy), (cx - 6, cy + 10)], fill=(176, 172, 169), width=4)
    return img


# ---------------------------------------------------------------------------
# Image de partage
# ---------------------------------------------------------------------------

def marque(d, x, y, taille=48):
    t = taille
    d.rounded_rectangle([x, y, x + t, y + t], radius=t * 0.29, fill=CORAIL_VIF)
    b, e, lw = x + t * 0.19, y + t * 0.19, max(2, int(t * 0.065))
    c, g = t * 0.62, t * 0.17
    for dx, dy in ((0, 0), (1, 0), (1, 1), (0, 1)):
        px, py = b + dx * c, e + dy * c
        sx, sy = (1 if dx == 0 else -1), (1 if dy == 0 else -1)
        d.line([(px, py + sy * g), (px, py)], fill=BLANC, width=lw)
        d.line([(px, py), (px + sx * g, py)], fill=BLANC, width=lw)
    d.rounded_rectangle([x + t * 0.30, y + t * 0.37, x + t * 0.70, y + t * 0.63],
                        radius=t * 0.07, fill=BLANC)
    for yy, xx in ((0.46, 0.57), (0.545, 0.50)):
        d.line([(x + t * 0.37, y + t * yy), (x + t * xx, y + t * yy)],
               fill=CORAIL_VIF, width=max(1, int(t * 0.045)))


def partage(t, telephone, sortie):
    LARG, HAUT = 1200, 630
    im = Image.new("RGB", (LARG, HAUT), (253, 246, 240))
    halo = Image.new("RGB", (LARG, HAUT), (255, 150, 105))
    m = Image.new("L", (LARG, HAUT), 0)
    ImageDraw.Draw(m).ellipse([LARG * 0.52, -HAUT * 0.5, LARG * 1.25, HAUT * 0.95], fill=56)
    im.paste(halo, (0, 0), m.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(im)

    marque(d, 64, 54)
    d.text((126, 60), "Comlynk", font=DIS_B(34), fill=(15, 13, 12))

    fb = TXT_SB(21)
    bw = d.textlength(t["og_badge"], font=fb) + 66
    d.rounded_rectangle([64, 176, 64 + bw, 226], radius=25, fill=BLANC)
    d.ellipse([88, 195, 100, 207], fill=CORAIL_VIF)
    d.text((112, 190), t["og_badge"], font=fb, fill=(193, 58, 20))

    ft = DIS_B(68)
    tracked(d, (64, 268), t["og_titre_1"], ft, (15, 13, 12), -2.6)
    x = tracked(d, (64, 352), t["og_titre_2"], ft, (15, 13, 12), -2.6)
    tracked(d, (x, 352), t["og_accent"], ft, CORAIL_VIF, -2.6)

    fbt = TXT_SB(23)
    lw = d.textlength(t["og_bouton"], font=fbt)
    d.rounded_rectangle([64, 476, 64 + lw + 80, 552], radius=38, fill=CORAIL_VIF)
    d.text((104, 502), t["og_bouton"], font=fbt, fill=BLANC)

    hh = 540
    ww = int(telephone.width * hh / telephone.height)
    tel = telephone.resize((ww, hh), Image.LANCZOS)
    pad = int(ww * 0.032)
    chassis = Image.new("RGB", (ww + pad * 2, hh + pad * 2), (12, 11, 10))
    chassis.paste(tel, (pad, pad))
    rayon = int(chassis.width * 0.15)
    cm = Image.new("L", chassis.size, 0)
    ImageDraw.Draw(cm).rounded_rectangle([0, 0, chassis.width - 1, chassis.height - 1],
                                         radius=rayon, fill=255)
    ombre = Image.new("L", (LARG, HAUT), 0)
    ImageDraw.Draw(ombre).rounded_rectangle(
        [LARG - 400, 96, LARG - 400 + chassis.width, 96 + chassis.height], radius=rayon, fill=90)
    im.paste(Image.new("RGB", (LARG, HAUT), (120, 95, 80)), (0, 0),
             ombre.filter(ImageFilter.GaussianBlur(26)))
    im.paste(chassis, (LARG - 400, 90), cm)
    im.save(sortie, "PNG", optimize=True)


# ---------------------------------------------------------------------------
# Production
# ---------------------------------------------------------------------------

def jpeg(im, chemin, qualite=90):
    im.save(chemin, "JPEG", quality=qualite, optimize=True, progressive=True)
    return chemin


def produire(langue):
    t = T[langue]
    dossier = os.path.join(IMG, langue)
    os.makedirs(dossier, exist_ok=True)
    scene = Image.open(SOURCE).convert("RGB")

    a, b, c = carte_a(t), carte_b(t), carte_c(t)

    # Scans
    hero = textes_appareil(vignette(pose(scene, a, PAPIER, LISERE), a), t)
    jpeg(hero, os.path.join(dossier, "hero-scan.jpg"))
    jpeg(hero.crop((0, 100, 601, 1039)), os.path.join(dossier, "step-scan.jpg"))

    noir = textes_appareil(vignette(pose(scene, b, QUAD_B, LISERE_B), b), t)
    jpeg(noir.crop((0, 100, 601, 1085)), os.path.join(dossier, "hard-scan.jpg"))

    # Interface
    ecran_liste(t, a).save(os.path.join(dossier, "step-list.png"), optimize=True)

    jpeg(ecran_fiche(t, LEA["nom"], a, [
        (t["nom"], LEA["nom"], False), (t["fonction"], t["metier_a"], False),
        (t["telephone"], LEA["tel"], False), (t["email"], LEA["mail"], False),
        (t["site"], LEA["site"], False), (t["reseau"], LEA["reseau"], False),
    ], decalage=22), os.path.join(dossier, "record-lea.jpg"), 92)

    jpeg(ecran_fiche(t, THOMAS["nom"], b, [
        (t["nom"], THOMAS["nom"], False), (t["fonction"], t["metier_b"], False),
        (t["telephone"], THOMAS["tel"], False), (t["email"], THOMAS["mail"], False),
        (t["site"], THOMAS["site"], False),
    ], boite=(28, 200, 573, 552), rayon=14), os.path.join(dossier, "hard-record.jpg"), 92)

    jpeg(ecran_fiche(t, CAMILLE["nom"], c, [
        (t["nom"], CAMILLE["nom"], False), (t["telephone"], CAMILLE["tel"], False),
        (t["email"], CAMILLE["mail"], False), (t["adresse"], CAMILLE["adresse"], True),
    ], hauteur=1306, boite=(28, 228, 573, 590), rayon=14,
       avec_plan=True, etiquette=CAMILLE["nom"]), os.path.join(dossier, "record-map.jpg"), 92)

    partage(t, hero, os.path.join(IMG, f"og-{langue}.png"))

    for f in sorted(os.listdir(dossier)):
        p = os.path.join(dossier, f)
        print(f"  {f:<18} {Image.open(p).size}  {os.path.getsize(p) // 1024} Ko")


if __name__ == "__main__":
    for langue in ("fr", "en"):
        print(langue)
        produire(langue)
