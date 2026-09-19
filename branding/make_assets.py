#!/usr/bin/env python3
"""Erzeugt alle Icons und Logos für Support.me aus dem Cogswell-Logo.

Aufruf:  python3 branding/make_assets.py [pfad/zum/logo.png] [schriftdatei]
Ergebnis: branding/assets/<zielpfad im Repo> — apply.py kopiert von dort.

Das Logo muss ein quadratisches PNG mit transparentem Hintergrund sein.
"""
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

HIER = os.path.dirname(os.path.abspath(__file__))
LOGO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HIER, 'source', 'supportme-mark.png')
FONT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HIER, 'source', 'wordmark-font.ttf')
OUT = os.path.join(HIER, 'assets')

NAME = 'Support.me'
INK = (25, 28, 31, 255)          # #191c1f — cogswell.de
TILE = (43, 100, 121, 255)       # Petrol #2B6479 — Support.me-App-Icon
PETROL = TILE
WEISS = (255, 255, 255, 255)


def ziel(pfad):
    voll = os.path.join(OUT, pfad)
    os.makedirs(os.path.dirname(voll), exist_ok=True)
    return voll


def mark():
    """Logo auf den sichtbaren Bereich zuschneiden und quadratisch machen."""
    img = Image.open(LOGO).convert('RGBA')
    box = img.getbbox()
    img = img.crop(box)
    seite = max(img.size)
    quad = Image.new('RGBA', (seite, seite), (0, 0, 0, 0))
    quad.paste(img, ((seite - img.width) // 2, (seite - img.height) // 2))
    return quad


def silhouette(img, farbe):
    """Einfarbige Fassung (Tray-/Benachrichtigungs-Icons)."""
    alpha = img.split()[3]
    out = Image.new('RGBA', img.size, farbe)
    out.putalpha(alpha)
    return out


def mark_auf(canvas, groesse, anteil, m, farbe=None):
    """Logo zentriert mit gegebenem Größenanteil auf transparentem Quadrat."""
    bild = Image.new('RGBA', (groesse, groesse), (0, 0, 0, 0))
    s = max(1, int(groesse * anteil))
    logo = (silhouette(m, farbe) if farbe else m).resize((s, s), Image.LANCZOS)
    bild.paste(logo, ((groesse - s) // 2, (groesse - s) // 2), logo)
    return bild


def kachel(groesse, m, rand=0.0, radius=0.225, form='rund'):
    """Heller, abgerundeter App-Icon-Grund mit Logo (macOS/Linux/Windows)."""
    bild = Image.new('RGBA', (groesse, groesse), (0, 0, 0, 0))
    innen = int(groesse * (1 - 2 * rand))
    off = (groesse - innen) // 2
    maske = Image.new('L', (innen * 4, innen * 4), 0)
    d = ImageDraw.Draw(maske)
    if form == 'kreis':
        d.ellipse([0, 0, innen * 4 - 1, innen * 4 - 1], fill=255)
    else:
        d.rounded_rectangle([0, 0, innen * 4 - 1, innen * 4 - 1], radius=int(innen * 4 * radius), fill=255)
    maske = maske.resize((innen, innen), Image.LANCZOS)
    grund = Image.new('RGBA', (innen, innen), TILE)
    grund.putalpha(maske)
    bild.paste(grund, (off, off), grund)
    logo = mark_auf(None, innen, 0.70, m, farbe=WEISS)   # weiße Marke auf Petrol
    bild.paste(logo, (off, off), logo)
    return bild


def wortmarke(m, text_farbe, hoehe=120, breite=600):
    """Logo + Schriftzug für den Kopf der App (max. 300 × 60 @2x)."""
    bild = Image.new('RGBA', (breite, hoehe), (0, 0, 0, 0))
    s = int(hoehe * 0.82)
    logo = m.resize((s, s), Image.LANCZOS)
    bild.paste(logo, (0, (hoehe - s) // 2), logo)
    schrift = ImageFont.truetype(FONT, int(hoehe * 0.40))
    d = ImageDraw.Draw(bild)
    x = s + int(hoehe * 0.18)
    _, oben, _, unten = d.textbbox((0, 0), NAME, font=schrift)
    y = (hoehe - (unten - oben)) // 2 - oben
    d.text((x, y), NAME, font=schrift, fill=text_farbe)
    rechts = x + d.textbbox((0, 0), NAME, font=schrift)[2]
    return bild.crop((0, 0, min(breite, rechts + 4), hoehe))


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    m = silhouette(mark(), PETROL)   # Quelle ist weiß; frei stehend in Petrol

    # ── Allgemeine App-Icons (res/) ──
    kachel(1024, m).save(ziel('res/icon.png'))
    # macOS: Kachel mit dem von Apple vorgesehenen Rand (ca. 10 %)
    mac = kachel(1024, m, rand=0.098, radius=0.2237)
    mac.save(ziel('res/mac-icon.png'))
    for g, n in [(32, '32x32'), (64, '64x64'), (128, '128x128'), (256, '128x128@2x')]:
        kachel(g, m).save(ziel(f'res/{n}.png'))
    ico = kachel(256, m)
    ico.save(ziel('res/icon.ico'), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    ico.save(ziel('flutter/windows/runner/resources/app_icon.ico'), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

    # ── Tray / Menüleiste ──
    mark_auf(None, 64, 0.9, m).save(ziel('res/tray-icon.ico'), sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64)])
    mark_auf(None, 48, 0.9, m, farbe=(0, 0, 0, 255)).save(ziel('res/mac-tray-light-x2.png'))
    mark_auf(None, 48, 0.9, m, farbe=(255, 255, 255, 255)).save(ziel('res/mac-tray-dark-x2.png'))

    # ── macOS .icns ──
    with tempfile.TemporaryDirectory() as tmp:
        iconset = os.path.join(tmp, 'AppIcon.iconset')
        os.makedirs(iconset)
        for g in (16, 32, 128, 256, 512):
            mac.resize((g, g), Image.LANCZOS).save(os.path.join(iconset, f'icon_{g}x{g}.png'))
            mac.resize((g * 2, g * 2), Image.LANCZOS).save(os.path.join(iconset, f'icon_{g}x{g}@2x.png'))
        subprocess.run(['iconutil', '-c', 'icns', iconset, '-o', ziel('flutter/macos/Runner/AppIcon.icns')], check=True)

    # ── Flutter-Assets: Icon + Logo im Kopf der App ──
    mark_auf(None, 512, 1.0, m).save(ziel('flutter/assets/icon.png'))
    wortmarke(m, INK).save(ziel('flutter/assets/logo_light.png'))
    wortmarke(silhouette(m, WEISS), WEISS).save(ziel('flutter/assets/logo_dark.png'))
    wortmarke(m, INK).save(ziel('flutter/assets/logo.png'))

    # ── Android ──
    dichten = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
    for d, f in dichten.items():
        basis = f'flutter/android/app/src/main/res/mipmap-{d}'
        kachel(int(48 * f), m, radius=0.2).save(ziel(f'{basis}/ic_launcher.png'))
        kachel(int(48 * f), m, form='kreis').save(ziel(f'{basis}/ic_launcher_round.png'))
        # Adaptive Icon: 108 dp, sichtbare Zone 66 dp → Logo ca. 46 %
        mark_auf(None, int(108 * f), 0.50, m, farbe=WEISS).save(ziel(f'{basis}/ic_launcher_foreground.png'))
        # Benachrichtigungs-Icon: weiße Silhouette
        mark_auf(None, int(24 * f), 0.92, m, farbe=(255, 255, 255, 255)).save(ziel(f'{basis}/ic_stat_logo.png'))

    print('Assets erzeugt in', OUT)


if __name__ == '__main__':
    main()
