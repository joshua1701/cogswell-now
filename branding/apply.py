#!/usr/bin/env python3
"""Macht aus einem RustDesk-Checkout den Client „Support.me" (Cogswell IT).

Aufruf im Repo-Wurzelverzeichnis:  python3 branding/apply.py
Idempotent: bereits angewendete Änderungen werden erkannt und übersprungen.
Jede Ersetzung prüft, dass ihr Suchtext genau einmal vorkommt — ändert
RustDesk bei einem Update eine Stelle, bricht das Skript mit einer klaren
Meldung ab, statt still ein halb gebrandetes Programm zu bauen.

Getrennt gehalten:
  APP_NAME      „SupportMe"     — technischer Name (Pfade, Dienst, Drucker,
                                  URL-Schema). RustDesk erlaubt hier nur
                                  Buchstaben, Ziffern und Bindestrich.
  DISPLAY_NAME  „Support.me"    — sichtbarer Name in Texten und Titeln.
"""
import os
import shutil
import sys

APP_NAME = 'SupportMe'
DISPLAY_NAME = 'Support.me'
SERVER = 'support.cogswell.net'
KEY = 'RT6pspgIeIhmHjfwE5PWFsIYUiBtryaQDacHULX1Ke8='
BUNDLE_ID = 'de.cogswell.supportme'
ORG = 'de.cogswell'
# Farben von cogswell.de
ACCENT = '0xFF4D90AD'      # --ca-accent
ACCENT_50 = '0x774D90AD'
ACCENT_80 = '0xAA4D90AD'
BUTTON = '0xFF276A87'      # --ca-accent-strong
ID_COLOR = '0xFF00B8FF'    # Logo-Cyan
API_SERVER = 'https://support.cogswell.net'
WEBSITE = 'https://www.cogswell.de'
DATENSCHUTZ = 'https://www.cogswell.de/datenschutz'
DOWNLOAD = 'https://www.cogswell.de/support-me'

ROOT = os.getcwd()
HIER = os.path.dirname(os.path.abspath(__file__))
fehler = []


def patch(pfad, alt, neu, anzahl=1):
    voll = os.path.join(ROOT, pfad)
    s = open(voll, encoding='utf-8').read()
    # Schon angewendet? Nur am Ersatztext erkennen — er kann den Suchtext
    # enthalten (Einfügung am Funktionsanfang), sonst würde doppelt gepatcht.
    if neu in s:
        return
    c = s.count(alt)
    if anzahl is None:          # alle Vorkommen, mindestens eines
        if c == 0:
            fehler.append(f'{pfad}: »{alt[:70]}« nicht gefunden')
            return
    elif c != anzahl:
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
          f'                // Support.me: sichtbarer Name (technischer Name ohne „!")\n'
          f'                let app_name = "{DISPLAY_NAME}".to_owned();\n                if !app_name.contains("RustDesk") {{')

    # ── Fenstertitel (Flutter) ──
    patch('flutter/lib/common.dart',
          'String getWindowName({WindowType? overrideType}) {\n  final name = bind.mainGetAppNameSync();',
          "String getWindowName({WindowType? overrideType}) {\n"
          f"  // Support.me: sichtbarer Name im Fenstertitel\n  const name = '{DISPLAY_NAME}';")

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

    # macOS: Bundle heißt jetzt wie APP_NAME — Build-Skript und Workflow
    # hatten „RustDesk.app" fest verdrahtet (u. a. Kopieren des Dienstes).
    patch('build.py', "./build/macos/Build/Products/Release/RustDesk.app/Contents/MacOS/')",
          f"./build/macos/Build/Products/Release/{APP_NAME}.app/Contents/MacOS/')")
    patch('build.py', '--volname \\"RustDesk Installer\\"', f'--volname \\"{DISPLAY_NAME} Installer\\"')
    patch('build.py', '--icon RustDesk.app 200 190 --hide-extension RustDesk.app rustdesk.dmg ./build/macos/Build/Products/Release/RustDesk.app',
          f'--icon {APP_NAME}.app 200 190 --hide-extension {APP_NAME}.app rustdesk.dmg ./build/macos/Build/Products/Release/{APP_NAME}.app')
    patch('.github/workflows/flutter-build.yml', 'RustDesk.app', f'{APP_NAME}.app', anzahl=None)

    # ── Linux: Menüeintrag ──
    patch('res/rustdesk.desktop', 'Name=RustDesk\n', f'Name={DISPLAY_NAME}\n')
    patch('res/rustdesk.desktop', 'Comment=Remote Desktop\n', 'Comment=Cogswell Fernwartung\n')
    patch('res/rustdesk-link.desktop', 'Name=RustDesk\n', f'Name={DISPLAY_NAME}\n')

    # ── Android ──
    man = 'flutter/android/app/src/main/AndroidManifest.xml'
    patch(man, 'android:label="RustDesk"', f'android:label="{DISPLAY_NAME}"')
    patch(man, 'android:label="RustDesk Input"', f'android:label="{DISPLAY_NAME} Eingabe"')
    patch(man, '<data android:scheme="rustdesk" />', f'<data android:scheme="{APP_NAME.lower()}" />')
    patch('flutter/android/app/build.gradle', 'applicationId "com.carriez.flutter_hbb"', f'applicationId "{BUNDLE_ID}"')

    # ── Linux: Fenstertitel ──
    patch('flutter/linux/my_application.cc', 'gtk_header_bar_set_title(header_bar, "rustdesk");', f'gtk_header_bar_set_title(header_bar, "{DISPLAY_NAME}");')
    patch('flutter/linux/my_application.cc', 'gtk_window_set_title(window, "rustdesk");', f'gtk_window_set_title(window, "{DISPLAY_NAME}");')

    # ── Konten-API: eigener Server (RustDesk Server Pro) statt admin.rustdesk.com ──
    # Ohne gesetzte Option fiel der Client auf den RustDesk-Dienst zurück —
    # Anmeldung, Adressbuch und Heartbeat wären dorthin gegangen.
    patch('src/common.rs', '    "https://admin.rustdesk.com".to_owned()\n}',
          f'    // Support.me: eigene Konsole (HTTPS über nginx)\n    "{API_SERVER}".to_owned()\n}}')
    # Keine Update-Prüfung gegen api.rustdesk.com — Updates kommen von uns.
    patch('src/common.rs',
          'pub async fn do_check_software_update() -> hbb_common::ResultType<()> {\n',
          'pub async fn do_check_software_update() -> hbb_common::ResultType<()> {\n'
          '    // Support.me: keine Update-Hinweise auf RustDesk-Downloads\n'
          '    if is_custom_client() {\n        return Ok(());\n    }\n')

    # ── Links: cogswell.de statt rustdesk.com ──
    for datei in ('flutter/lib/desktop/pages/desktop_setting_page.dart',
                  'flutter/lib/desktop/pages/install_page.dart',
                  'flutter/lib/mobile/pages/settings_page.dart'):
        patch(datei, 'https://rustdesk.com/privacy.html', DATENSCHUTZ, anzahl=None)
    for datei in ('flutter/lib/desktop/pages/desktop_home_page.dart',
                  'flutter/lib/mobile/pages/connection_page.dart'):
        patch(datei, 'https://rustdesk.com/download', DOWNLOAD, anzahl=None)
    patch('flutter/lib/desktop/pages/desktop_setting_page.dart',
          "launchUrlString('https://rustdesk.com');", f"launchUrlString('{WEBSITE}');")
    # „Powered by RustDesk" auf der Startseite ausblenden
    patch('flutter/lib/common.dart',
          'if (bind.mainGetBuildinOption(key: "hide-powered-by-me") == \'Y\') {',
          'if (true) { // Support.me: kein „Powered by"-Hinweis')

    # ── CI: 32-Bit-Windows (Sciter) ──
    # Neueres rustup verweigert die i686-Toolchain auf dem 64-Bit-Runner ohne
    # --force-non-host; dtolnay/rust-toolchain kann das Flag nicht setzen,
    # und `rustup default` prüft den Host erneut → RUSTUP_TOOLCHAIN setzen.
    patch('.github/workflows/flutter-build.yml',
          """      - name: Install Rust toolchain
        uses: dtolnay/rust-toolchain@e97e2d8cc328f1b50210efc529dca0028893a2d9 # v1
        with:
          toolchain: nightly-2023-10-13-${{ matrix.job.target }} # must use nightly here, because of abi_thiscall feature required
          targets: ${{ matrix.job.target }}
          components: "rustfmt"
""",
          """      - name: Install Rust toolchain
        shell: bash
        run: |
          TC=nightly-2023-10-13-${{ matrix.job.target }} # must use nightly here, because of abi_thiscall feature required
          rustup toolchain install "$TC" --target ${{ matrix.job.target }} --component rustfmt --profile minimal --no-self-update --force-non-host
          echo "RUSTUP_TOOLCHAIN=$TC" >> "$GITHUB_ENV"
          rustc +"$TC" --version --verbose
""")

    if fehler:
        print('Branding NICHT vollständig angewendet:')
        for f in fehler:
            print('  -', f)
        sys.exit(1)
    print(f'Branding „{DISPLAY_NAME}" angewendet (Server {SERVER}).')


if __name__ == '__main__':
    main()
