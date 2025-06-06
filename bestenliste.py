import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("bestenliste-462113-0ac9883ad436.json", scope)
client = gspread.authorize(creds)
sheet = client.open("bestenliste").sheet1

# Load data into DataFrame
data = sheet.get_all_records()
df = pd.DataFrame(data)

st.title("🏅 Bestenliste")

# Neue Einträge hinzufügen
with st.form("add_entry"):
    name = st.text_input("Name")
    zeit = st.text_input("Zeit (z. B. 01:32)")
    submit = st.form_submit_button("Eintragen")

    if submit and name and zeit:
        sheet.append_row([name, zeit])
        st.success(f"{name} mit Zeit {zeit} eingetragen! Bitte Seite neu laden.")
        st.stop()

# Sortierte Bestenliste anzeigen
st.subheader("🥇 Aktuelle Bestenliste")
if not df.empty:
    df_sorted = df.sort_values(by="Zeit")  # ggf. Zeit zuerst in Sekunden umwandeln
    df_sorted.reset_index(drop=True, inplace=True)
    df_sorted.index += 1  # Platzierung 1-basiert
    st.dataframe(df_sorted)
else:
    st.info("Noch keine Einträge vorhanden.")

# Platzierung suchen
st.subheader("🔍 Platz suchen")
search_name = st.text_input("Nach Namen suchen")
if search_name:
    result = df[df["Name"].str.lower() == search_name.lower()]
    if not result.empty:
        rank = df.sort_values("Zeit").reset_index(drop=True)
        rank["Platz"] = rank.index + 1
        platz = rank[rank["Name"].str.lower() == search_name.lower()]["Platz"].values[0]
        st.success(f"{search_name} ist auf Platz {platz}!")
    else:
        st.warning(f"{search_name} nicht gefunden.")
