import os
import sys
import shutil
import traceback
from pathlib import Path

def create_shortcut(target, script, working_dir, shortcut_path, icon_path=None):
    from win32com.client import Dispatch
    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(str(shortcut_path))
    shortcut.TargetPath = str(target)
    shortcut.Arguments = f'"{script}"'
    shortcut.WorkingDirectory = str(working_dir)
    shortcut.IconLocation = str(icon_path) if icon_path else str(target)
    shortcut.Save()

def install():
    home = Path.home()
    install_path = home / "FragebogenApp"
    desktop_path = home / "Desktop"
    script_name = "fragebogen.exe"  # Wichtig: Deine gepackte EXE!

    if install_path.exists():
        print("FragebogenApp scheint bereits installiert zu sein.")
        sys.exit(0)

    install_path.mkdir(parents=True, exist_ok=True)

    # Bestimme Quelle der gepackten EXE
    if getattr(sys, 'frozen', False):
        script_source = Path(sys.executable)
    else:
        script_source = Path(os.getcwd()) / script_name

    script_target = install_path / script_name

    try:
        shutil.copy(script_source, script_target)
    except Exception as e:
        print(f"Fehler beim Kopieren: {e}")
        traceback.print_exc()
        sys.exit(1)

    # Verknüpfung auf Desktop erstellen
    shortcut_path = desktop_path / "FragebogenApp.lnk"
    icon_path = install_path / "img" / "tvstud.ico"  # Optional
    create_shortcut(script_target, "", install_path, shortcut_path, icon_path)

    print("Installation abgeschlossen! Du findest die App auf dem Desktop.")

if __name__ == "__main__":
    install()
