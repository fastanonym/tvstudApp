import traceback

try:
    import tkinter as tk
    from tkinter import ttk
    from tkinterdnd2 import TkinterDnD, DND_FILES
    from pathlib import Path
    import csv
    import os
    import sys
    import platform
    import subprocess
    from collections import defaultdict

    # Tab-Fokus nur beim ersten Mal auf das Namensfeld setzen
    tab_erstes_mal = True

    def is_dark_mode():
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                result = subprocess.run(
                    ["defaults", "read", "-g", "AppleInterfaceStyle"],
                    capture_output=True,
                    text=True
                )
                return "Dark" in result.stdout
            elif system == "Windows":  # Windows
                import winreg
                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return value == 0  # 0 = Dark Mode
            else:
                # Für Linux (GTK, KDE etc.) ist’s komplizierter → hier einfach Default
                return False
        except Exception:
            return False

    # Name der CSV-Datei
    ergebnisse = os.path.join(os.path.expanduser("~"), "Desktop", "tv_stud_liste.csv")
    gesamtliste = os.path.join(os.path.expanduser("~"), "Desktop", "tv_stud_gesamtliste.csv")

    # Funktionen zum Speichern der Antwort
    def get_app_directory():
        """
        Gibt das Verzeichnis zurück, in dem die .app-Datei liegt.
        - Bei gepackter App → geht drei Ebenen hoch aus dem Binary
        - Bei normalem Skript → verwendet das Skriptverzeichnis
        """
        if getattr(sys, 'frozen', False):  # Wenn gepackt mit PyInstaller
            return Path(sys.executable).resolve().parents[3]  # <- 3x hoch: MacOS → Contents → .app-Verzeichnis
        else:
            return Path(__file__).resolve().parent

    def resolve_speicherpfad(eingabe):
        if eingabe == '' or eingabe == 'Speicherpfad ändern (Default: Desktop)':
            return Path.home() / "Desktop"
        
        eingabe_path = Path(os.path.expanduser(eingabe))

        if eingabe_path.is_absolute():
            return eingabe_path.resolve()
        else:
            return get_app_directory() / eingabe_path

    def speichern():
        # Antworten aus den Eingabefeldern holen
        autor = autor_entry.get()
        if autor == 'Autor:in': autor = ''
        
        name = name_entry.get()
        if name == 'Name': name = ''
        
        telefon = telefon_entry.get()
        if telefon == 'Telefonnummer': telefon = ''
        
        bereich = bereich_entry.get()
        if bereich == 'Bereich': bereich = ''
        
        tarifvertrag = tarifvertrag_var.get()
        mitbestimmen = mitbestimmen_var.get()
        aufbautreffen = aufbautreffen_var.get()
        gewerkschaft = gewerkschaft_var.get()
        
        weiteres = weiteres_entry.get()
        if weiteres == 'Weiteres': weiteres = ''
        speicherpfad = Speicherpfad_entry.get()
        zielverzeichnis = resolve_speicherpfad(speicherpfad)
        ergebnisse = zielverzeichnis / "tv_stud_liste.csv"

        row = [name, f'="{telefon}"', bereich, tarifvertrag, mitbestimmen, aufbautreffen, gewerkschaft, weiteres, autor]
        cleaned_row = [str(cell).replace('\n', ' ').replace('\r', ' ') for cell in row]

        # Header und Antworten in CSV speichern
        try:
            # Prüfen, ob die Datei bereits existiert
            datei_existiert = os.path.isfile(ergebnisse)
            
            # Öffnen der CSV-Datei zum Anhängen
            with open(ergebnisse, mode="a", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file, delimiter=';')
                
                # Wenn die Datei noch nicht existiert, den Header schreiben
                if not datei_existiert:
                    writer.writerow([
                        "Name",
                        "Telefonnummer",
                        "Bereich",
                        "Tarifvertrag?",
                        "Mitbestimmen?",
                        "Aufbautreffen?",
                        "Gewerkschaft?",
                        "Weiteres?",
                        "Autor:in"
                    ])
                

            # 🧼 CSV bereinigen und sortieren
            with open(ergebnisse, mode="r", encoding="utf-8-sig") as file:
                reader = csv.reader(file, delimiter=';')
                rows = list(reader)

            # Header und Daten trennen
            header, data = rows[0], rows[1:]

            # Neue Zeile anhängen
            data.append(cleaned_row)
            
            # Vorherige Länge merken
            length_before = len(data)

            # Duplikate entfernen
            unique_data = list({tuple(row) for row in data})
            length_after = len(unique_data)

            # Jetzt korrekt vergleichen
            if length_after < length_before:
                num_dubs = length_before - length_after
                status_label.config(text="Antwort gespeichert. {} Duplikat(e) gelöscht.".format(num_dubs), fg="red")                  
            else:
                status_label.config(text="Antwort gespeichert!", fg="green")
                # Antwortmeldung nach 3 Sekunden ausblenden
                root.after(2000, lambda: status_label.config(text="", fg="green"))

            # Sortieren und Schreiben
            sorted_data = sorted(unique_data, key=lambda x: (x[0] or "").lower())
            with open(ergebnisse, mode="w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(header)
                writer.writerows(sorted_data)

            # Eingabefelder zurücksetzen (außer für die Default-Boolean-Werte)
            name_entry.delete(0, 'end')
            telefon_entry.delete(0, 'end')
            bereich_entry.delete(0, 'end')
            weiteres_entry.delete(0, 'end')

            # Die Standardwerte zurücksetzen (Platzhaltertext)
            name_entry.insert(0, "Name")
            name_entry.config(fg="grey")
            telefon_entry.insert(0, "Telefonnummer")
            telefon_entry.config(fg="grey")
            bereich_entry.insert(0, "Bereich")
            bereich_entry.config(fg="grey")
            weiteres_entry.insert(0, "Weiteres")
            weiteres_entry.config(fg="grey")

            # Zurücksetzen der Radiobuttons auf den Standardwert "Ja"
            tarifvertrag_var.set("Ja")
            mitbestimmen_var.set("Ja")
            aufbautreffen_var.set("Ja")
            gewerkschaft_var.set("Ja")

            # Entfernen des Fokus von allen Feldern
            root.focus_set()
            global tab_erstes_mal
            tab_erstes_mal = True # bei "tab" wieder auf Name

        except Exception as e:
            status_label.config(text=f"Fehler: {e}", fg="red")


    # Funktion zum Mergen von CSV-Dateien
    def merge_list_of_files(list_of_files):
        all_data = []  # Alle Daten ohne Header
        header = None # Wird je überschrieben: neueste Datei kann aktualisieren

        try:
            for file in list_of_files:
                # CSV-Datei laden
                with open(file, mode='r', newline='', encoding='utf-8-sig') as file:
                    reader = csv.reader(file, delimiter=';')
                    data = list(reader)

                    # Header setzen (nur einmal, falls noch nicht gesetzt)
                    if header is None:
                        header = data[0]  # Den Header der ersten Datei verwenden

                    # Die restlichen Daten (ohne Header) zu all_data hinzufügen
                    all_data.extend(data[1:])  # Nur die Daten ohne Header

            speicherpfad = Speicherpfad_entry.get()
            zielverzeichnis = resolve_speicherpfad(speicherpfad)
            gesamtliste = zielverzeichnis / "tv_stud_gesamtliste.csv"
        
            # Wenn eine Gesamtliste existiert, laden und mergen
            if os.path.exists(gesamtliste):
                with open(gesamtliste, mode='r', newline='', encoding='utf-8-sig') as file:
                    reader = csv.reader(file, delimiter=';')
                    gesamtliste_data = list(reader)

                # Alle Daten kombinieren (Überschriften dürfen nicht nochmal hinzugefügt werden)
                all_data = gesamtliste_data[1:] + all_data  # Den Header der Gesamtliste ignorieren

            lenght_before = len(all_data)
            
            # Duplikate entfernen
            unique_data = [list(item) for item in {tuple(item) for item in all_data}]

            if len(unique_data) < lenght_before:
                num_dubs = lenght_before - len(unique_data)
                status_label.config(text="{} Duplikate gelöscht.".format(num_dubs), fg="red")

            # Dann sortieren
            unique_data = sorted(unique_data, key=lambda x: x[0].lower())

            # Gesamtliste speichern
            with open(gesamtliste, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(header)  # Header nur einmal schreiben
                writer.writerows(unique_data)  # Alle Daten

                # Status anzeigen, dass das Mergen erfolgreich war
                # if dubs == 0:
                status_label.config(text="Schon {} gesammelt!".format(len(unique_data)), fg="green")
                # else:
                #     status_label.config(text="{} Dublikate entfernt. Schon {} gesammelt!".format(dubs, len(all_data)), fg="green")

                root.after(2000, lambda: status_label.config(text="", fg="green"))

        except Exception as e:
            status_label.config(text=f"Fehler beim Mergen: {e}", fg="red")


    # Funktion für das Drag-and-Drop
    def on_drop(event):
        dropped_files = event.data.split()  # Hier trennen wir die einzelnen Dateipfade durch Leerzeichen
        # Stelle sicher, dass die Dateien eine CSV-Endung haben
        csv_files = [file for file in dropped_files if file.endswith('.csv')]
        if csv_files:
            merge_list_of_files(csv_files)  # Übergibt die CSV-Dateien als Liste

    # Funktion für Platzhaltertext (Placeholder) in den Textfeldern
    def on_entry_click(event, default_text):
        """Löscht den Standardtext, wenn das Feld angeklickt wird."""
        if event.widget.get() == default_text:
            event.widget.delete(0, "end")  # Löscht den Standardtext
            event.widget.config(fg=COLORS["fg_type"])  # Textfarbe ändern, wenn der Benutzer tippt

    def on_entry_click_info(event, default_text):
        """Löscht den Standardtext, wenn das Feld angeklickt wird."""
        if event.widget.get() == default_text:
            event.widget.delete(0, "end")  # Löscht den Standardtext
            event.widget.config(fg="#043869")  # Textfarbe ändern, wenn der Benutzer tippt

    def on_focusout(event, default_text):
        """Setzt den Standardtext zurück, wenn das Feld leer ist und verlassen wird."""
        if event.widget.get() == "":
            event.widget.insert(0, default_text)
            event.widget.config(fg="grey")  # Standardtextfarbe zurücksetzen

    def on_focusout_info(event, default_text):
        """Setzt den Standardtext zurück, wenn das Feld leer ist und verlassen wird."""
        if event.widget.get() == "":
            event.widget.insert(0, default_text)
            event.widget.config(fg="#043869")  # Standardtextfarbe zurücksetzen

    def fokus_auf_name(event):
        global tab_erstes_mal
        if tab_erstes_mal:
            tab_erstes_mal = False
            name_entry.focus_set()
            return "break"  # Verhindert den normalen Tab
        # danach: ganz normales Verhalten

    # Speichern-Button mit Hover-Effekt
    def on_hover(event):
        speicher_button.config(bg="#043869")

    def on_leave(event):
        speicher_button.config(bg="#e4004e")
        
    darkmode = is_dark_mode()
    
    COLORS = {
        "fg_type": "grey" if darkmode else "black"
    }
    
    # GUI erstellen
    root = TkinterDnD.Tk()
    root.title("Antworten sammeln")
    root.geometry("750x670")
    root.option_add("*Font", "Montserrat 10")
    # root.overrideredirect(True)  # Fensterleiste entfernen

    # FRAMES

    info_frame = tk.Frame(root, background="#e4004e", height= 150)
    info_frame.pack(fill="both", expand=True)

    # Frame für die Aufteilung
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # Left Frame (Fragebogen)
    left_frame = tk.Frame(main_frame, width=300)
    left_frame.pack(side="left", fill="both", expand=True)

    # Right Frame (Drag-and-Drop)
    right_frame = tk.Frame(main_frame, width=200)
    right_frame.pack(side="right", fill="both", expand=True)


    # ENTRIES

    # Info: Autor
    autor_entry = tk.Entry(info_frame, bg="#f0f0f0", fg="#043869", width=75)  # Breite festgelegt
    autor_entry.insert(0, "Autor:in")  # Defaulttext
    autor_entry.pack(pady=(20, 5))  # Mehr Platz vor dem ersten Feld
    # autor_entry.grid(sticky="nsew")
    autor_entry.bind("<FocusIn>", lambda event: on_entry_click_info(event, "Autor:in"))
    autor_entry.bind("<FocusOut>", lambda event: on_focusout_info(event, "Autor:in"))

    # Speicherpfad ändern
    Speicherpfad_entry = tk.Entry(info_frame, bg="#f0f0f0", fg="#043869", width=75)
    Speicherpfad_entry.insert(0, "Speicherpfad ändern (Default: Desktop)")  # Defaulttext
    Speicherpfad_entry.pack(pady=(5, 20))
    # Speicherpfad_entry.grid(sticky="nsew")
    Speicherpfad_entry.bind("<FocusIn>", lambda event: on_entry_click_info(event, "Speicherpfad ändern (Default: Desktop)"))
    Speicherpfad_entry.bind("<FocusOut>", lambda event: on_focusout_info(event, "Speicherpfad ändern (Default: Desktop)"))

    # Frage 1: Name
    name_entry = tk.Entry(left_frame, fg="grey", width=40)
    name_entry.insert(0, "Name")  # Defaulttext
    name_entry.pack(pady=(20, 5))  # Mehr Platz vor dem ersten Feld
    name_entry.bind("<FocusIn>", lambda event: on_entry_click(event, "Name"))
    name_entry.bind("<FocusOut>", lambda event: on_focusout(event, "Name"))

    # Frage 2: Telefonnummer
    telefon_entry = tk.Entry(left_frame, fg="grey", width=40)
    telefon_entry.insert(0, "Telefonnummer")
    telefon_entry.pack(pady=5)
    telefon_entry.bind("<FocusIn>", lambda event: on_entry_click(event, "Telefonnummer"))
    telefon_entry.bind("<FocusOut>", lambda event: on_focusout(event, "Telefonnummer"))

    # Frage 3: Bereich
    bereich_entry = tk.Entry(left_frame, fg="grey", width=40)
    bereich_entry.insert(0, "Bereich")
    bereich_entry.pack(pady=5)
    bereich_entry.bind("<FocusIn>", lambda event: on_entry_click(event, "Bereich"))
    bereich_entry.bind("<FocusOut>", lambda event: on_focusout(event, "Bereich"))

    # Frage 4: Tarifvertrag (Einzelauswahl als Radiobutton)
    tarifvertrag_label = tk.Label(left_frame, text="Ist für Tarifvertrag?")
    tarifvertrag_label.pack(pady=5)
    tarifvertrag_var = tk.StringVar(value="Ja")
    tarifvertrag_frame = tk.Frame(left_frame)
    tarifvertrag_ja = tk.Radiobutton(tarifvertrag_frame, text="Ja", variable=tarifvertrag_var, value="Ja")
    tarifvertrag_nein = tk.Radiobutton(tarifvertrag_frame, text="Nein", variable=tarifvertrag_var, value="Nein")
    tarifvertrag_ja.pack(side=tk.LEFT)
    tarifvertrag_nein.pack(side=tk.LEFT)
    tarifvertrag_frame.pack(pady=5)

    # Frage 5: Mitbestimmen (Einzelauswahl als Radiobutton)
    mitbestimmen_label = tk.Label(left_frame, text="Will mitbestimmen?")
    mitbestimmen_label.pack(pady=5)
    mitbestimmen_var = tk.StringVar(value="Ja")
    mitbestimmen_frame = tk.Frame(left_frame)
    mitbestimmen_ja = tk.Radiobutton(mitbestimmen_frame, text="Ja", variable=mitbestimmen_var, value="Ja")
    mitbestimmen_nein = tk.Radiobutton(mitbestimmen_frame, text="Nein", variable=mitbestimmen_var, value="Nein")
    mitbestimmen_ja.pack(side=tk.LEFT)
    mitbestimmen_nein.pack(side=tk.LEFT)
    mitbestimmen_frame.pack(pady=5)

    # Frage 6: Aufbautreffen (Einzelauswahl als Radiobutton)
    aufbautreffen_label = tk.Label(left_frame, text="Plant zum Aufbautreffen zu kommen?")
    aufbautreffen_label.pack(pady=5)
    aufbautreffen_var = tk.StringVar(value="Ja")
    aufbautreffen_frame = tk.Frame(left_frame)
    aufbautreffen_ja = tk.Radiobutton(aufbautreffen_frame, text="Ja", variable=aufbautreffen_var, value="Ja")
    aufbautreffen_nein = tk.Radiobutton(aufbautreffen_frame, text="Nein", variable=aufbautreffen_var, value="Nein")
    aufbautreffen_ja.pack(side=tk.LEFT)
    aufbautreffen_nein.pack(side=tk.LEFT)
    aufbautreffen_frame.pack(pady=5)

    # Frage 7: Gewerkschaft (Einzelauswahl als Radiobutton)
    gewerkschaft_label = tk.Label(left_frame, text="Will Gewerkschaftsmitglied werden?")
    gewerkschaft_label.pack(pady=5)
    gewerkschaft_var = tk.StringVar(value="Ja")
    gewerkschaft_frame = tk.Frame(left_frame)
    gewerkschaft_ja = tk.Radiobutton(gewerkschaft_frame, text="Ja", variable=gewerkschaft_var, value="Ja")
    gewerkschaft_nein = tk.Radiobutton(gewerkschaft_frame, text="Nein", variable=gewerkschaft_var, value="Nein")
    gewerkschaft_ja.pack(side=tk.LEFT)
    gewerkschaft_nein.pack(side=tk.LEFT)
    gewerkschaft_frame.pack(pady=5)

    # Frage 8: Weiteres
    weiteres_entry = tk.Entry(left_frame, fg="grey", width=40)
    weiteres_entry.insert(0, "Weiteres")  # Defaulttext
    weiteres_entry.pack(pady=5)
    weiteres_entry.bind("<FocusIn>", lambda event: on_entry_click(event, "Weiteres"))
    weiteres_entry.bind("<FocusOut>", lambda event: on_focusout(event, "Weiteres"))

    # Drag-and-Drop Bereich (Margins anpassbar über padx und pady)
    drop_label = tk.Label(
        right_frame, 
        text="CSV(s) hier ablegen, \num in Gesamtliste zu mergen", 
        relief="flat", 
        width=45, 
        height=30,
        # bg="#f0f0f0",  # Hintergrundfarbe des Labels
        fg=COLORS["fg_type"]  # Textfarbe
    )
    drop_label.pack(pady=25)  # Hier können die Margins angepasst werden
    drop_label.drop_target_register(DND_FILES)
    drop_label.dnd_bind('<<Drop>>', on_drop)

    speicher_button = tk.Button(root, text="Speichern", command=speichern, width=12, height=2, relief="flat", bg="#e4004e", fg="#e4004e", font=("Montserrat 10", 12))
    speicher_button.pack(pady=(20, 10))
    speicher_button.bind("<Enter>", on_hover)
    speicher_button.bind("<Leave>", on_leave)

    # Status Label
    status_label = tk.Label(root, text="", fg="green")
    status_label.pack()

    # Speichern durch Drücken der Enter-Taste ermöglichen
    root.bind('<Return>', lambda event: speichern())
    root.bind("<Tab>", fokus_auf_name)

    root.mainloop()

except Exception:
    with open("error.log", "w") as f:
        traceback.print_exc(file=f)
    input("Es ist ein Fehler aufgetreten. Siehe error.log. Drücke Enter...")
