def eingabe_zeit():
    while True:
        try:
            zeit = float(input("Zeit in Sekunden eingeben: "))
            if zeit <= 0:
                print("Bitte eine positive Zahl eingeben.")
                continue
            return zeit
        except ValueError:
            print("Ungültige Eingabe. Bitte eine Zahl eingeben.")

def name_suchen(bestenliste, vorname, nachname):
    for idx, (name, zeit) in enumerate(bestenliste):
        if name == (vorname, nachname):
            return idx + 1, zeit  # Platz ist Index +1
    return None, None

def bestenliste_anzeigen(bestenliste, top=10):
    print(f"\nTop {top} Ergebnisse:")
    for i, ((vorname, nachname), zeit) in enumerate(bestenliste[:top], start=1):
        print(f"{i}. {vorname} {nachname} - {zeit:.2f} Sekunden")

def main():
    bestenliste = []  # Liste von ((vorname, nachname), zeit)
    verlaufs_undo_stack = []  # Stapel für Undo (Liste mit ganzen Listen-Ständen)
    
    print("Willkommen zur Bestenliste fürs Schulfest!")
    print("Gib Vor- und Nachname ein, um Zeiten hinzuzufügen bzw. zu aktualisieren.")
    print('Gib "Such Name" zum Suchen ein (z.B. "Such Max Mustermann").')
    print('Gib "Top 10" ein, um die 10 besten Zeiten anzuzeigen.')
    print('Gib "Undo" ein, um die letzte Änderung rückgängig zu machen.')
    print('Gib "Ende" ein, um das Programm zu beenden.')
    
    while True:
        eingabe = input("\nEingabe: ").strip()
        if eingabe.lower() == "ende":
            print("Programm wird beendet.")
            break
        elif eingabe.lower() == "top 10":
            if not bestenliste:
                print("Die Bestenliste ist noch leer.")
            else:
                bestenliste.sort(key=lambda x: x[1])
                bestenliste_anzeigen(bestenliste, top=10)
            continue
        elif eingabe.lower() == "undo":
            if verlaufs_undo_stack:
                bestenliste = verlaufs_undo_stack.pop()
                print("Letzte Änderung wurde rückgängig gemacht.")
            else:
                print("Nichts zum Rückgängig machen.")
            continue
        elif eingabe.lower().startswith("such "):
            parts = eingabe.split(maxsplit=2)
            if len(parts) < 3:
                print("Bitte den Befehl richtig eingeben: z.B. 'Such Max Mustermann'")
                continue
            vorname, nachname = parts[1], parts[2]
            platz, zeit = name_suchen(bestenliste, vorname, nachname)
            if platz is not None:
                print(f"{vorname} {nachname} ist auf Platz {platz} mit {zeit:.2f} Sekunden.")
            else:
                print(f"{vorname} {nachname} ist nicht in der Bestenliste.")
            continue
        else:
            namen = eingabe.split()
            if len(namen) < 2:
                print("Bitte Vor- und Nachnamen eingeben.")
                continue
            vorname, nachname = namen[0], " ".join(namen[1:])
            zeit = eingabe_zeit()
            
            # Zustand vor der Änderung sichern für Undo (tiefe Kopie)
            import copy
            verlaufs_undo_stack.append(copy.deepcopy(bestenliste))
            
            gefunden = False
            for idx, (name, alte_zeit) in enumerate(bestenliste):
                if name == (vorname, nachname):
                    gefunden = True
                    if zeit < alte_zeit:
                        bestenliste[idx] = ((vorname, nachname), zeit)
                        print(f"Zeit für {vorname} {nachname} aktualisiert auf {zeit:.2f} Sekunden.")
                    else:
                        print(f"Die vorhandene Zeit {alte_zeit:.2f} Sekunden ist besser. Keine Änderung.")
                        verlaufs_undo_stack.pop()  # Da es keine Änderung gab, Undo-Eintrag entfernen
                    break
            if not gefunden:
                bestenliste.append(((vorname, nachname), zeit))
                print(f"{vorname} {nachname} mit Zeit {zeit:.2f} Sekunden hinzugefügt.")
            
            bestenliste.sort(key=lambda x: x[1])

if __name__ == "__main__":
    main()
