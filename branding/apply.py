#!/usr/bin/env python3
"""Macht aus einem RustDesk-Checkout den Client „Cogswell-Now!".

Aufruf im Repo-Wurzelverzeichnis:  python3 branding/apply.py
Idempotent: bereits angewendete Änderungen werden erkannt und übersprungen.
Jede Ersetzung prüft, dass ihr Suchtext genau einmal vorkommt — ändert
RustDesk bei einem Update eine Stelle, bricht das Skript mit einer klaren
Meldung ab, statt still ein halb gebrandetes Programm zu bauen.

Getrennt gehalten:
  APP_NAME      „Cogswell-Now"  — technischer Name (Pfade, Dienst, Drucker,
                                  URL-Schema). RustDesk erlaubt hier nur
                                  Buchstaben, Ziffern und Bindestrich.
  DISPLAY_NAME  „Cogswell-Now!" — sichtbarer Name in Texten und Titeln.
"""
import os
import shutil
import sys

APP_NAME = 'Cogswell-Now'
DISPLAY_NAME = 'Cogswell-Now!'
SERVER = 'support-now.cogswell.net'
KEY = 'RT6pspgIeIhmHjfwE5PWFsIYUiBtryaQDacHULX1Ke8='
BUNDLE_ID = 'de.cogswell.now'
ORG = 'de.cogswell'
# Farben von cogswell.de
ACCENT = '0xFF4D90AD'      # --ca-accent
ACCENT_50 = '0x774D90AD'
ACCENT_80 = '0xAA4D90AD'
BUTTON = '0xFF276A87'      # --ca-accent-strong
ID_COLOR = '0xFF00B8FF'    # Logo-Cyan

ROOT = os.getcwd()
HIER = os.path.dirname(os.path.abspath(__file__))
fehler = []


def patch(pfad, alt, neu, anzahl=1):
    voll = os.path.join(ROOT, pfad)
    s = open(voll, encoding='utf-8').read()
    if neu in s and alt not in s:
        return  # schon angewendet
    c = s.count(alt)
    if c != anzahl:
        fehler.append(f'{pfad}: erwartet {anzahl}× »{alt[:70]}«, gefunden {c}×')
        return
    open(voll, 'w', encoding='utf-8').write(s.replace(alt, neu))


def assets():
    quelle = os.path.join(HIER, 'assets')
    if not os.path.isdir(quelle):
        sys.exit('branding/assets fehlt — erst branding/make_assets.py ausführen')
    for basis, _, dateien in os.walk(quelle):
        for d in dateien:
            q = os.path.join(basis, d)
            z = os.path.join(ROOT, os.path.relpath(q, quelle))
            os.makedirs(os.path.dirname(z), exist_ok=True)
            shutil.copyfile(q, z)


def main():
    assets()

    # ── Kern: Name, Organisation, fest eingebauter Server + Key ──
    cfg = 'libs/hbb_common/src/config.rs'
    patch(cfg, 'pub static ref APP_NAME: RwLock<String> = RwLock::new("RustDesk".to_owned());',
          f'pub static ref APP_NAME: RwLock<String> = RwLock::new("{APP_NAME}".to_owned());')
    patch(cfg, 'pub static ref ORG: RwLock<String> = RwLock::new("com.carriez".to_owned());',
          f'pub static ref ORG: RwLock<String> = RwLock::new("{ORG}".to_owned());')
    patch(cfg, 'pub const RENDEZVOUS_SERVERS: &[&str] = &["rs-ny.rustdesk.com"];',
          f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{SERVER}"];')
    patch(cfg, 'pub const RS_PUB_KEY: &str = "OeVuKk5nlHiXp+APNn0Y3pC1Iwpwn44JGqrQCsWqmBw=";',
          f'pub const RS_PUB_KEY: &str = "{KEY}";')

    # ── Sichtbarer Name in allen übersetzten Texten ──
    patch('src/lang.rs',
          '                let app_name = crate::get_app_name();\n                if !app_name.contains("RustDesk") {',
          f'                // Cogswell-Now!: sichtbarer Name (technischer Name ohne „!")\n'
          f'                let app_name = "{DISPLAY_NAME}".to_owned();\n                if !app_name.contains("RustDesk") {{')

    # ── Fenstertitel (Flutter) ──
    patch('flutter/lib/common.dart',
          'String getWindowName({WindowType? overrideType}) {\n  final name = bind.mainGetAppNameSync();',
          "String getWindowName({WindowType? overrideType}) {\n"
          f"  // Cogswell-Now!: sichtbarer Name im Fenstertitel\n  const name = '{DISPLAY_NAME}';")

    # ── Farben: cogswell.de statt RustDesk-Blau ──
    patch('flutter/lib/common.dart', 'static const Color accent = Color(0xFF0071FF);', f'static const Color accent = Color({ACCENT});')
    patch('flutter/lib/common.dart', 'static const Color accent50 = Color(0x770071FF);', f'static const Color accent50 = Color({ACCENT_50});')
    patch('flutter/lib/common.dart', 'static const Color accent80 = Color(0xAA0071FF);', f'static const Color accent80 = Color({ACCENT_80});')
    patch('flutter/lib/common.dart', 'static const Color idColor = Color(0xFF00B6F0);', f'static const Color idColor = Color({ID_COLOR});')
    patch('flutter/lib/common.dart', 'static const Color button = Color(0xFF2C8CFF);', f'static const Color button = Color({BUTTON});')
    patch('flutter/lib/common.dart', '  return Color(0xFF2C8CFF);', f'  return Color({BUTTON});')

    # ── Windows ──
    rc = 'flutter/windows/runner/Runner.rc'
    patch(rc, 'VALUE "FileDescription", "RustDesk Remote Desktop" "\\0"', f'VALUE "FileDescription", "{DISPLAY_NAME} Fernwartung" "\\0"')
    patch(rc, 'VALUE "ProductName", "RustDesk" "\\0"', f'VALUE "ProductName", "{DISPLAY_NAME}" "\\0"')
    patch('flutter/windows/runner/main.cpp', 'std::wstring app_name = L"RustDesk";', f'std::wstring app_name = L"{APP_NAME}";')

    # ── macOS ──
    patch('flutter/macos/Runner/Configs/AppInfo.xcconfig', 'PRODUCT_NAME = RustDesk', f'PRODUCT_NAME = {APP_NAME}')
    patch('flutter/macos/Runner/Configs/AppInfo.xcconfig', 'PRODUCT_BUNDLE_IDENTIFIER = com.carriez.flutterHbb', f'PRODUCT_BUNDLE_IDENTIFIER = {BUNDLE_ID}')
    patch('flutter/macos/Runner/Info.plist', '<string>com.carriez.rustdesk</string>', f'<string>{BUNDLE_ID}</string>')
    patch('flutter/macos/Runner/Info.plist', '<string>rustdesk</string>', f'<string>{APP_NAME.lower()}</string>')

    # ── Android ──
    man = 'flutter/android/app/src/main/AndroidManifest.xml'
    patch(man, 'android:label="RustDesk"', f'android:label="{DISPLAY_NAME}"')
    patch(man, 'android:label="RustDesk Input"', f'android:label="{DISPLAY_NAME} Eingabe"')
    patch(man, '<data android:scheme="rustdesk" />', f'<data android:scheme="{APP_NAME.lower()}" />')
    patch('flutter/android/app/build.gradle', 'applicationId "com.carriez.flutter_hbb"', f'applicationId "{BUNDLE_ID}"')

    # ── Linux: Fenstertitel ──
    patch('flutter/linux/my_application.cc', 'gtk_header_bar_set_title(header_bar, "rustdesk");', f'gtk_header_bar_set_title(header_bar, "{DISPLAY_NAME}");')
    patch('flutter/linux/my_application.cc', 'gtk_window_set_title(window, "rustdesk");', f'gtk_window_set_title(window, "{DISPLAY_NAME}");')

    if fehler:
        print('Branding NICHT vollständig angewendet:')
        for f in fehler:
            print('  -', f)
        sys.exit(1)
    print(f'Branding „{DISPLAY_NAME}" angewendet (Server {SERVER}).')


if __name__ == '__main__':
    main()
