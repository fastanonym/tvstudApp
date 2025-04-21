# build.spec
# Mit allen notwendigen Files und Packages eingebunden
from PyInstaller.utils.hooks import collect_submodules
from pathlib import Path

# Optional: vollständiger Pfad zur Icon-Datei
icon_file = str(Path("img") / "tvstud.ico")

a = Analysis(
    ["src/fragebogen.py"],
    pathex=["src"],  # Optional: Pfad zur src/ Ordnerstruktur
    binaries=[],
    datas=[
        ("img/tvstud.ico", "img")  # damit das Icon auch in der .exe eingebettet ist
    ],
    hiddenimports=[
        *collect_submodules("tkinterdnd2"),
        *collect_submodules("pywin32"),
        *collect_submodules("winshell"),
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="FragebogenApp",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=icon_file,
    single_file=True,  # Hier stellen wir sicher, dass die EXE als Einzeldatei gebaut wird
)

