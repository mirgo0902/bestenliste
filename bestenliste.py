import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

st.set_page_config(page_title="🏅 Bestenliste mit Google Sheets", page_icon="🏅")

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("bestenliste-462113-0ac9883ad436.json", scope)
client = gspread.authorize(creds)
sheet = client.open("bestenliste").sheet1

def zeit_zu_sekunden(zeit_str):
    """
    Wandelt eine Zeit im Format mm:ss oder ss (Sekunden als Zahl) in Sekunden (float) um.
    Beispiel: "01:32" -> 92.0, "45" -> 45.0
    """
    try:
        if ":" in zeit_str:
            minuten, sekunden = zeit_str.split(":")
            return int(minuten)*60 + float(sekunden)
        else:
            return float(zeit_str)
    except:
        return None

def laden_bestenliste():
    data = sheet.get_all_records()
    if not data:
        return pd.DataFrame(columns=["Vorname", "Nachname", "Zeit"])
    df = pd.DataFrame(data)
    df.columns = df.columns.str.strip()
    return df

def speichern_eintrag(vorname, nachname, zeit):
    # Anhängen neuer Zeile in Google Sheets
    sheet.append_row([vorname, nachname, zeit])

def bestenliste_anzeigen(df, top=10):
    if df.empty:
        st.info("Noch keine Einträge vorhanden.")
        return
    # Zeit in Sekunden umwandeln für Sortierung
    df["Zeit_in_Sek"] = df["Zeit"].apply(zeit_zu_sekunden)
    df = df.dropna(subset=["Zeit_in_Sek"])
    df_sorted = df.sort_values("Zeit_in_Sek").head(top).reset_index(drop=True)
    df_sorted.index += 1
    st.dataframe(df_sorted[["Vorname", "Nachname", "Zeit"]])

def name_suchen(df, vorname, nachname):
    df["Name_Kombi"] = df["Vorname"].str.lower() + " " + df["Nachname"].str.lower()
    such_name = f"{vorname.lower()} {nachname.lower()}"
    if such_name in df["Name_Kombi"].values:
        df_sorted = df.sort_values("Zeit_in_Sek").reset_index(drop=True)
        df_sorted["Platz"] = df_sorted.index + 1
        platz = df_sorted[df_sorted["Name_Kombi"] == such_name]["Platz"].values[0]
        zeit = df_sorted[df_sorted["Name_Kombi"] == such_name]["Zeit"].values[0]
        return platz, zeit
    else:
        return None, None


st.title("🏅 Bestenliste fürs Schulfest (mit Google Sheets)")

# Eingabeformular
with st.form("eintrag_form"):
    vorname = st.text_input("Vorname")
    nachname = st.text_input("Nachname")
    zeit_str = st.text_input("Zeit (mm:ss oder Sekunden z.B. 01:32 oder 92)")
    submit = st.form_submit_button("Eintragen")

if submit:
    if not vorname or not nachname:
        st.error("Bitte Vor- und Nachnamen eingeben.")
    else:
        zeit_sek = zeit_zu_sekunden(zeit_str)
        if zeit_sek is None or zeit_sek <= 0:
            st.error("Bitte eine gültige Zeit eingeben (mm:ss oder Sekunden).")
        else:
            speichern_eintrag(vorname, nachname, zeit_str)
            st.success(f"{vorname} {nachname} mit Zeit {zeit_str} eingetragen! Bitte Seite neu laden.")

# Bestenliste anzeigen
st.subheader("🥇 Aktuelle Bestenliste (Top 10)")
df = laden_bestenliste()
bestenliste_anzeigen(df)

# Name suchen
st.subheader("🔍 Platz suchen")
such_vorname = st.text_input("Vorname zum Suchen", key="such_vorname")
such_nachname = st.text_input("Nachname zum Suchen", key="such_nachname")
such_button = st.button("Suchen")

if such_button:
    if not such_vorname or not such_nachname:
        st.warning("Bitte Vor- und Nachnamen zum Suchen eingeben.")
    else:
        platz, zeit = name_suchen(df, such_vorname, such_nachname)
        if platz is None:
            st.info(f"{such_vorname} {such_nachname} ist nicht in der Bestenliste.")
        else:
            st.success(f"{such_vorname} {such_nachname} ist auf Platz {platz} mit Zeit {zeit}.")
