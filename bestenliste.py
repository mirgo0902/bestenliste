import streamlit as st

# Session State nutzen, um Daten zu speichern
if "bestenliste" not in st.session_state:
    st.session_state.bestenliste = []
if "undo_stack" not in st.session_state:
    st.session_state.undo_stack = []

st.title("🏃‍♂️ Bestenliste fürs Schulfest")

# Eingabe von Namen
vorname = st.text_input("Vorname")
nachname = st.text_input("Nachname")

# Eingabe der Zeit
zeit = st.number_input("Zeit in Sekunden", min_value=0.0, format="%.2f", step=0.01)

# Zeit hinzufügen oder aktualisieren
if st.button("➕ Zeit hinzufügen / aktualisieren"):
    if vorname and nachname and zeit > 0:
        import copy
        st.session_state.undo_stack.append(copy.deepcopy(st.session_state.bestenliste))

        gefunden = False
        for idx, (name, alte_zeit) in enumerate(st.session_state.bestenliste):
            if name == (vorname, nachname):
                gefunden = True
                if zeit < alte_zeit:
                    st.session_state.bestenliste[idx] = ((vorname, nachname), zeit)
                    st.success(f"Aktualisiert: {vorname} {nachname} mit {zeit:.2f} Sekunden")
                else:
                    st.warning(f"Vorherige Zeit ({alte_zeit:.2f}s) ist besser. Keine Änderung.")
                    st.session_state.undo_stack.pop()
                break
        if not gefunden:
            st.session_state.bestenliste.append(((vorname, nachname), zeit))
            st.success(f"Hinzugefügt: {vorname} {nachname} mit {zeit:.2f} Sekunden")

        st.session_state.bestenliste.sort(key=lambda x: x[1])

# Sucheingabe
such_name = st.text_input("🔍 Suche nach Name (Vorname Nachname)")
if such_name:
    teile = such_name.strip().split(maxsplit=1)
    if len(teile) == 2:
        vor, nach = teile
        for i, ((v, n), z) in enumerate(st.session_state.bestenliste, 1):
            if (v, n) == (vor, nach):
                st.info(f"{v} {n} ist auf Platz {i} mit {z:.2f} Sekunden.")
                break
        else:
            st.warning(f"{vor} {nach} nicht gefunden.")

# Bestenliste anzeigen
if st.button("🏆 Top 10 anzeigen"):
    if st.session_state.bestenliste:
        st.subheader("Top 10")
        for i, ((v, n), z) in enumerate(st.session_state.bestenliste[:10], 1):
            st.write(f"{i}. {v} {n} – {z:.2f} Sekunden")
    else:
        st.info("Die Bestenliste ist leer.")

# Undo-Funktion
if st.button("↩️ Letzte Änderung rückgängig machen"):
    if st.session_state.undo_stack:
        st.session_state.bestenliste = st.session_state.undo_stack.pop()
        st.success("Letzte Änderung wurde rückgängig gemacht.")
    else:
        st.warning("Nichts zum Rückgängig machen.")
