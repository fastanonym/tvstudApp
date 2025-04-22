#!/bin/bash

# Schritt 1: Voraussetzungen installieren
echo "Installiere erforderliche Pakete..."

# Abhängig von der Distribution werden unterschiedliche Paketmanager verwendet.
if [ -f /etc/debian_version ]; then
    # Debian/Ubuntu/Mint
    sudo apt update
    sudo apt install -y python3 python3-pip python3-tk git
elif [ -f /etc/redhat-release ]; then
    # Fedora
    sudo dnf install -y python3 python3-pip python3-tkinter git
elif [ -f /etc/arch-release ]; then
    # Arch/Manjaro
    sudo pacman -Syu python python-pip tk git
else
    echo "Unbekannte Distribution! Bitte manuell die Voraussetzungen installieren."
    exit 1
fi

# Schritt 2: Projekt herunterladen oder klonen (falls nicht schon vorhanden)
echo "Klonen oder Download des Projekts..."
git clone https://github.com/fastanonym/tvstudApp.git
cd tvstudApp || exit

# Schritt 3: Virtuelle Umgebung erstellen (optional, aber empfohlen)
echo "Erstelle virtuelle Umgebung..."
python3 -m venv venv
source venv/bin/activate

# Schritt 4: Python-Abhängigkeiten installieren
echo "Installiere Python-Abhängigkeiten..."
pip install tkinterdnd2

# Schritt 5: App starten
echo "Starte die App..."
python3 fragebogen.py