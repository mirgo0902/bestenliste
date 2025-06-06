import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Zugriff auf Google Sheet
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("dein_google_api_schlüssel.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Bestenliste").sheet1

# Daten lesen
data = sheet.get_all_records()

# Daten schreiben
sheet.append_row(["Name", "Zeit"])
