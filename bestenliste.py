import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import copy

# --- Google Sheets Setup ---
SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# Pfad zu deinem Google Service Account JSON Schlüssel
CREDENTIALS_PATH = r"C:\Users\User\Documents\bestenliste\.streamlit\bestenliste-462113-0ac9883ad436.json"

# ID oder URL deines Google Sheets
SPREADSHEET_ID = "1xsWpzujwS-v1PirBnOxg4LOVs1gbsoSEP4FtVWhPSnc"

def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    return sheet

def load_bestenliste_from_sheet(sheet):
    records = sheet.get_all_records()
    # Erwartet Spalten: Vorname, Nachname, Zeit (Sekunden)
    bestenliste = []
    for r in records:
        try:
            zeit = float(r['Zeit'])
            vorname = r['Vorname'].strip()
            nachname = r['Nachname'].strip()
            bestenliste.append(((vorname, nachname), zeit))
        except (KeyError, ValueError):
            pass
    bestenliste.sort(key=lambda x: x[1])
    return bestenliste

def save_bestenliste_to_sheet(sheet, bestenliste):
    # Überschreibt die gesamte Tabelle (außer Kopfzeile)
    data = [["Vorname", "Nachname", "Zeit"]]
    for (vorname, nachname), zeit in bestenliste:
        data.append([vorname, nachname, zeit])
    sheet.clear()
    sheet.update(data)

# --- Bestenliste Logik ---

def find_position(bestenliste, vorname, nachname):
    for idx, ((vn, nn), zeit) in enumerate(bestenliste):
        if vn == vorname and nn == nachname:
            return idx+1, zeit
    return None, None

def main():
    st.title("Bestenliste Schulfest")

    sheet = get_sheet()
    if 'bestenliste' not in st.session_state:
        st.session_state.bestenliste = load_bestenliste_from_sheet(sheet)
        st.session_state.undo_stack = []

    neuen_eintrag = st.text_input("Vor- und Nachname eingeben (z.B. Max Mustermann):")
    if neuen_eintrag:
        namen = neuen_eintrag.strip().split()
        if len(namen) >= 2:
            vorname = namen[0]
            nachname = " ".join(namen[1:])
            zeit_input = st.text_input("Zeit in Sekunden eingeben:")
            if zeit_input:
                try:
                    zeit = float(zeit_input)
                    if zeit <= 0:
                        st.error("Bitte eine positive Zahl eingeben.")
                    else:
                        # Undo speichern
                        st.session_state.undo_stack.append(copy.deepcopy(st.session_state.bestenliste))

                        # Existierendes Update prüfen
                        found = False
                        for i, (name, alte_zeit) in enumerate(st.session_state.bestenliste):
                            if name == (vorname, nachname):
                                found = True
                                if zeit < alte_zeit:
                                    st.session_state.bestenliste[i] = ((vorname, nachname), zeit)
                                    st.success(f"Zeit für {vorname} {nachname} aktualisiert auf {zeit:.2f} Sekunden.")
                                else:
                                    st.warning(f"Die vorhandene Zeit {alte_zeit:.2f} Sekunden ist besser. Keine Änderung.")
                                    st.session_state.undo_stack.pop()  # Undo entfernen, da keine Änderung
                                break
                        if not found:
                            st.session_state.bestenliste.append(((vorname, nachname), zeit))
                            st.success(f"{vorname} {nachname} mit Zeit {zeit:.2f} Sekunden hinzugefügt.")

                        st.session_state.bestenliste.sort(key=lambda x: x[1])
                        save_bestenliste_to_sheet(sheet, st.session_state.bestenliste)
                        
                        # Formular zurücksetzen
                        st.experimental_rerun()
                except ValueError:
                    st.error("Ungültige Eingabe für Zeit.")
        else:
            st.warning("Bitte Vor- und Nachnamen eingeben.")

    st.write("### Top 10 Bestenliste")
    top10 = st.session_state.bestenliste[:10]
    if top10:
        df = pd.DataFrame(
            [{"Platz": i+1, "Vorname": vn, "Nachname": nn, "Zeit": zeit} for i, ((vn, nn), zeit) in enumerate(top10)]
        )
        st.table(df)
    else:
        st.write("Noch keine Einträge vorhanden.")

    st.write("---")
    st.write("### Nach Namen suchen")
    such_name = st.text_input("Vor- und Nachnamen zum Suchen eingeben:")
    if such_name:
        namen = such_name.strip().split()
        if len(namen) >= 2:
            vorname = namen[0]
            nachname = " ".join(namen[1:])
            pos, zeit = find_position(st.session_state.bestenliste, vorname, nachname)
            if pos:
                st.success(f"{vorname} {nachname} ist auf Platz {pos} mit {zeit:.2f} Sekunden.")
            else:
                st.warning(f"{vorname} {nachname} ist nicht in der Bestenliste.")
        else:
            st.warning("Bitte Vor- und Nachnamen zum Suchen eingeben.")

    if st.button("Undo letzte Änderung"):
        if st.session_state.undo_stack:
            st.session_state.bestenliste = st.session_state.undo_stack.pop()
            save_bestenliste_to_sheet(sheet, st.session_state.bestenliste)
            st.success("Letzte Änderung rückgängig gemacht.")
            st.experimental_rerun()
        else:
            st.warning("Keine Änderung zum Rückgängig machen.")

if __name__ == "__main__":
    main()
