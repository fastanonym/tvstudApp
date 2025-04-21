import os
import sys
import shutil
import subprocess
import traceback
from pathlib import Path

def run_subprocess(command):
    # Sichere Ausgabe und Fehlerweiterleitung im EXE
    result = subprocess.run(command, stdout=sys.stdout, stderr=sys.stderr, text=True, check=True)
    return result

def get_real_python_executable():
    if getattr(sys, 'frozen', False):
        # In PyInstaller-Exe: versuche python.exe im Systempfad oder dem gleichen Verzeichnis
        possible = ["python.exe", "C:\\Python39\\python.exe", "C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Python\\Python39\\python.exe"]
        for path in possible:
            try:
                result = subprocess.run([path, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if result.returncode == 0:
                    return path
            except Exception:
                continue
        print("Kein funktionierender Python-Interpreter gefunden.")
        sys.exit(1)
    else:
        return sys.executable

def create_virtualenv(venv_path):
    print(f"Prüfe auf Existenz von virtueller Umgebung: {venv_path}")
    # Prüfe, ob der Ordner für die virtuelle Umgebung existiert
    if not venv_path.exists():
        print("Virtuelle Umgebung wird erstellt...")
        try:
            python_path = get_real_python_executable()
            result = run_subprocess([python_path, "-m", "venv", str(venv_path)])
            print("Virtuelle Umgebung wurde erfolgreich erstellt.")
            # print("Standard Ausgabe:", result.stdout)
            # print("Fehler Ausgabe:", result.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Fehler bei der Erstellung der virtuellen Umgebung: {e}")
            print("Fehlercode:", e.returncode)
            print("Ausgabe:", e.output)
            print("Fehlerausgabe:", e.stderr)
            input("Drücke Enter, um das Programm zu beenden...")
            sys.exit(1)
    else:
        print("Virtuelle Umgebung bereits vorhanden.")

def install_requirements_in_venv(pip_executable, modules):
    print("Installiere Abhängigkeiten in virtueller Umgebung...")
    run_subprocess([str(pip_executable), "install", *modules])

def install_pywin32_postinstall(python_executable, venv_path):
    postinstall_script = venv_path / "Scripts" / "pywin32_postinstall.py"
    if postinstall_script.exists():
        print("Führe pywin32_postinstall.py direkt aus...")
        run_subprocess([str(python_executable), str(postinstall_script), "-install"])
    else:
        print("Warnung: pywin32_postinstall.py nicht gefunden. pywin32 funktioniert eventuell nicht korrekt.")

def create_shortcut(target, script, working_dir, shortcut_path, icon_path=None):
    from win32com.client import Dispatch
    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(str(shortcut_path))
    shortcut.TargetPath = str(target)
    shortcut.Arguments = f'"{script}"'
    shortcut.WorkingDirectory = str(working_dir)
    if icon_path:
        shortcut.IconLocation = str(icon_path)
    else:
        shortcut.IconLocation = str(target)
    shortcut.Save()

def install():
    # Grundpfade
    home = Path.home()
    install_path = home / "FragebogenApp"
    desktop_path = home / "Desktop"
    script_name = "fragebogen.py"
    venv_path = install_path / "venv"

    # Wenn das Installationsverzeichnis schon existiert, gehen wir davon aus, dass die Installation bereits erfolgt ist.
    if install_path.exists():
        if venv_path.exists():
            print("Installation bereits vorhanden. Beende Setup.")
            sys.exit(0)

    # Installationsverzeichnis anlegen
    install_path.mkdir(parents=True, exist_ok=True)

    # Virtuelle Umgebung und Pip
    create_virtualenv(venv_path)
    pip_executable = venv_path / "Scripts" / "pip.exe"
    # Verwende pythonw.exe; falls nicht vorhanden, Standard-Python
    pythonw_path = venv_path / "Scripts" / "pythonw.exe"
    if not pythonw_path.exists():
        pythonw_path = sys.executable
    python_executable = pythonw_path  # Verwenden als Ziel

    # Installiere die benötigten Module in der virtuellen Umgebung
    required_modules = ["pandas", "tkinterdnd2", "pywin32", "winshell"]
    install_requirements_in_venv(pip_executable, required_modules)
    install_pywin32_postinstall(python_executable, venv_path)

    # Bestimme Pfade für Skript
    # Wenn die EXE gepackt wurde, nehme _MEIPASS; ansonsten im aktuellen Arbeitsverzeichnis:
    if getattr(sys, 'frozen', False):
        script_source = os.path.join(sys._MEIPASS, 'fragebogen.py')
        icon_path = os.path.join(sys._MEIPASS, 'img/tvstud.ico')
    else:
        script_source = os.path.join(os.getcwd(), 'fragebogen.py')
        icon_path = os.path.join(os.getcwd(), 'img/tvstud.ico')

    script_target = install_path / script_name

    # Kopiere das Hauptprogramm in das Installationsverzeichnis
    try:
        shutil.copy(script_source, script_target)
    except Exception as e:
        print(f"Fehler beim Kopieren: {e}")
        traceback.print_exc()
        sys.exit(1)

    # Erstelle eine Desktop-Verknüpfung (Windows .lnk-Datei)
    shortcut_path = desktop_path / "FragebogenApp.lnk"
    # Damit sich kein Terminal öffnet, muss target auf pythonw.exe zeigen
    target_executable = python_executable
    create_shortcut(target_executable, script_target, install_path, shortcut_path, icon_path)

    print("Installation abgeschlossen! Programm kann über das Icon auf dem Desktop gestartet werden.")

if __name__ == "__main__":
    install()