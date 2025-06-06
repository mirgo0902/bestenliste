import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json

st.set_page_config(page_title="🏅 Bestenliste mit Google Sheets", page_icon="🏅")

# GOOGLE SHEETS: Zugang aus st.secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_dict), scope)
client = gspread.authorize(creds)
sheet = client.open("bestenliste").sheet1

def zeit_zu_sekunden(zeit_str):
    try:
        if ":" in zeit_str:
            minuten, sekunden = zeit_str.split(":")
            return int(minuten) * 60 + float(sekunden)
        else:
            return float(zeit_str)
    except:
        return None

def laden_bestenliste():
    data = sheet.get_all_records()
    if not data:
        return pd.DataFrame(columns=["Vorname", "Nachname", "Zeit"])
    df = pd.DataFrame(data)
    df.columns = df.columns.str.strip().str.lower()
    return df

def speichern_eintrag(vorname, nachname, zeit):
    records = sheet.get_all_records()
    for i, record in enumerate(records, start=2):
        if record.get("Vorname") == vorname and record.get("Nachname") == nachname:
            sheet.update_cell(i, 3, zeit)
            return
    sheet.append_row([vorname, nachname, zeit])

def bestenliste_anzeigen(df, top=10):
    if df.empty:
        st.info("Noch keine Einträge vorhanden.")
        return
    df.columns = df.columns.str.strip().str.lower()
    if "zeit" not in df.columns:
        st.error("Spalte 'zeit' nicht gefunden. Gefundene Spalten: " + ", ".join(df.columns))
        return
    df["zeit_in_sek"] = df["zeit"].apply(zeit_zu_sekunden)
    df = df.dropna(subset=["zeit_in_sek"])
    df_sorted = df.sort_values("zeit_in_sek").head(top).reset_index(drop=True)
    df_sorted.index += 1
    st.dataframe(df_sorted[["vorname", "nachname", "zeit"]])

def name_suchen(df, vorname, nachname):
    df.columns = df.columns.str.strip().str.lower()
    df["name_kombi"] = df["vorname"].str.lower() + " " + df["nachname"].str.lower()
    such_name = f"{vorname.lower()} {nachname.lower()}"
    if such_name in df["name_kombi"].values:
        df["zeit_in_sek"] = df["zeit"].apply(zeit_zu_sekunden)
        df_sorted = df.sort_values("zeit_in_sek").reset_index(drop=True)
        df_sorted["platz"] = df_sorted.index + 1
        platz = df_sorted[df_sorted["name_kombi"] == such_name]["platz"].values[0]
        zeit = df_sorted[df_sorted["name_kombi"] == such_name]["zeit"].values[0]
        return platz, zeit
    return None, None

st.title("🏅 Bestenliste fürs Schulfest (mit Google Sheets)")

with st.form("eintrag_form"):
    vorname = st.text_input("Vorname")
    nachname = st.text_input("Nachname")
    zeit_str = st.text_input("Zeit (mm:ss oder Sekunden, z.B. 01:32 oder 92)")
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
        platz, zeit = name_suchen(df, such_vorname, such_nachname)
        if platz is None:
            st.info(f"{such_vorname} {such_nachname} ist nicht in der Bestenliste.")
        else:
            st.success(f"{such_vorname} {such_nachname} ist auf Platz {platz} mit Zeit {zeit}.")
