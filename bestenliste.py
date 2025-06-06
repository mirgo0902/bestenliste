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

def Zeit_zu_sekunden(Zeit_str):
    try:
        if ":" in Zeit_str:
            minuten, sekunden = Zeit_str.split(":")
            return int(minuten)*60 + float(sekunden)
        else:
            return float(Zeit_str)
    except:
        return None

def laden_bestenliste():
    data = sheet.get_all_records()
    if not data:
        return pd.DataFrame(columns=["Vorname", "Nachname", "Zeit"])
    df = pd.DataFrame(data)
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.lower()
    return df
def speichern_eintrag(vorname, nachname, Zeit):
    records = sheet.get_all_records()
    for i, record in enumerate(records, start=2):  # 1. Zeile = Header
        if record.get("Vorname") == vorname and record.get("Nachname") == nachname:
            sheet.update_cell(i, 3, Zeit)
            return
    sheet.append_row([vorname, nachname, Zeit])

def bestenliste_anzeigen(df, top=10):
    if df.empty:
        st.info("Noch keine Einträge vorhanden.")
        return

    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.lower()

    st.write("Spaltennamen in DataFrame:", df.columns.tolist())  # Zum Debuggen

    if "zeit" not in df.columns:
        st.error("Spalte 'zeit' nicht gefunden. Gefundene Spalten: " + ", ".join(df.columns))
        return

    df["zeit_in_sek"] = df["zeit"].apply(Zeit_zu_sekunden)
    df = df.dropna(subset=["zeit_in_sek"])
    df_sorted = df.sort_values("zeit_in_sek").head(top).reset_index(drop=True)
    df_sorted.index += 1
    st.dataframe(df_sorted[["vorname", "nachname", "zeit"]])

def name_suchen(df, vorname, nachname):
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.lower()

    df["name_kombi"] = df["vorname"].str.lower() + " " + df["nachname"].str.lower()
    such_name = f"{vorname.lower()} {nachname.lower()}"
    if such_name in df["name_kombi"].values:
        df["zeit_in_sek"] = df["zeit"].apply(Zeit_zu_sekunden)
        df_sorted = df.sort_values("zeit_in_sek").reset_index(drop=True)
        df_sorted["platz"] = df_sorted.index + 1
        platz = df_sorted[df_sorted["name_kombi"] == such_name]["platz"].values[0]
        zeit = df_sorted[df_sorted["name_kombi"] == such_name]["zeit"].values[0]
        return platz, zeit
    else:
        return None, None
st.title("🏅 Bestenliste fürs Schulfest (mit Google Sheets)")

with st.form("eintrag_form"):
    vorname = st.text_input("Vorname")
    nachname = st.text_input("Nachname")
    Zeit_str = st.text_input("Zeit (mm:ss oder Sekunden, z.B. 01:32 oder 92)")
    submit = st.form_submit_button("Eintragen")

if submit:
    if not vorname or not nachname:
        st.error("Bitte Vor- und Nachnamen eingeben.")
    else:
        Zeit_sek = Zeit_zu_sekunden(Zeit_str)
        if Zeit_sek is None or Zeit_sek <= 0:
            st.error("Bitte eine gültige Zeit eingeben (mm:ss oder Sekunden).")
        else:
            speichern_eintrag(vorname, nachname, Zeit_str)
            st.success(f"{vorname} {nachname} mit Zeit {Zeit_str} eingetragen! Bitte Seite neu laden.")

st.subheader("🥇 Aktuelle Bestenliste (Top 10)")
df = laden_bestenliste()
bestenliste_anzeigen(df)

st.subheader("🔍 Platz suchen")
such_vorname = st.text_input("Vorname zum Suchen", key="such_vorname")
such_nachname = st.text_input("Nachname zum Suchen", key="such_nachname")
such_button = st.button("Suchen")

if such_button:
    if not such_vorname or not such_nachname:
        st.warning("Bitte Vor- und Nachnamen zum Suchen eingeben.")
    else:
        platz, Zeit = name_suchen(df, such_vorname, such_nachname)
        if platz is None:
            st.info(f"{such_vorname} {such_nachname} ist nicht in der Bestenliste.")
        else:
            st.success(f"{such_vorname} {such_nachname} ist auf Platz {platz} mit Zeit {Zeit}.")
