import json
import os
import streamlit as st

# Dateien für die persistente Speicherung auf dem Server
PAIRINGS_FILE = "pairings.json"
TIPS_FILE = "tips.json"


def load_data(file_path, default):
  if os.path.exists(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
      try:
        return json.load(f)
      except:
        return default
  return default


def save_data(file_path, data):
  with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


st.set_page_config(
    page_title="Schwingfest Tippspiel", page_icon="🇨🇭", layout="centered"
)

st.title("🏆 Schwingfest Tippspiel")

# Daten laden
pairings = load_data(PAIRINGS_FILE, [])
tips = load_data(TIPS_FILE, {})

# Navigation über Seitenleiste
menu = st.sidebar.selectbox(
    "Navigation", ["Tippen & Rangliste", "Admin-Bereich"]
)

if menu == "Tippen & Rangliste":
  st.subheader("📲 Tipps abgeben")
  participant_name = st.text_input("Dein Name / Nickname:")

  if participant_name:
    st.write(
        f"Grüezi **{participant_name}**! Tippe hier die laufenden und"
        " kommenden Paarungen."
    )

    if not pairings:
      st.info(
          "Noch keine Paarungen erfasst. Der Admin schaltet sie in Kürze frei!"
      )
    else:
      user_tips = tips.get(participant_name, {})

      with st.form("tipping_form"):
        new_user_tips = {}
        for p in pairings:
          p_id = p["id"]
          p_title = (
              f"Gang {p['gang']}: {p['schwinget_1']} vs. {p['schwinget_2']}"
          )
          default_tip = user_tips.get(p_id, "Sieg Schwinger 1")

          options = [
              "Sieg Schwinger 1",
              "Unentschieden (Gangluepf)",
              "Sieg Schwinger 2",
          ]
          default_idx = (
              options.index(default_tip) if default_tip in options else 0
          )

          tip = st.selectbox(p_title, options, index=default_idx, key=f"tip_{p_id}")
          new_user_tips[p_id] = tip

        submit_tips = st.form_submit_button("Tipps speichern")
        if submit_tips:
          tips[participant_name] = new_user_tips
          save_data(TIPS_FILE, tips)
          st.success("Tipps erfolgreich gespeichert!")

    # Live-Rangliste
    st.divider()
    st.subheader("📊 Live-Rangliste")
    if not tips:
      st.write("Noch keine Tipps abgegeben.")
    else:
      scores = []
      for name, user_tips in tips.items():
        points = 0
        for p in pairings:
          if p.get("result"):  # Wenn Resultat vom Admin eingetragen wurde
            if user_tips.get(p["id"]) == p["result"]:
              points += 1  # 1 Punkt pro richtigem Tipp
        scores.append({"Name": name, "Punkte": points})

      # Sortieren nach Punkten absteigend
      scores = sorted(scores, key=lambda x: x["Punkte"], reverse=True)
      st.table(scores)

  else:
    st.warning("Bitte gib deinen Namen ein, um deine Tipps abzugeben.")

elif menu == "Admin-Bereich":
  st.subheader("⚙️ Admin-Verwaltung")
  admin_pw = st.text_input("Admin-Passwort:", type="password")

  # Ändere das Passwort nach Wunsch
  if admin_pw == "schwingen2026":
    st.success("Admin-Zugriff aktiv.")

    tab1, tab2 = st.tabs(["Paarungen hinzufügen", "Resultate eintragen"])

    with tab1:
      st.write("Neue Paarung erfassen (laufend während des Tages):")
      with st.form("add_pairing"):
        gang_nr = st.number_input("Gang-Nummer", min_value=1, max_value=8, value=1)
        s1 = st.text_input("1. Schwinger (Name)")
        s2 = st.text_input("2. Schwinger (Name)")
        add_btn = st.form_submit_button("Paarung hinzufügen")

        if add_btn and s1 and s2:
          new_id = str(len(pairings) + 1)
          pairings.append({
              "id": new_id,
              "gang": int(gang_nr),
              "schwinget_1": s1,
              "schwinget_2": s2,
              "result": None,
          })
          save_data(PAIRINGS_FILE, pairings)
          st.success(
              f"Paarung Gang {gang_nr}: {s1} vs {s2} erfolgreich hinzugefügt!"
          )
          st.rerun()

    with tab2:
      st.write("Resultate für abgeschlossene Gänge eintragen:")
      if not pairings:
        st.info("Keine Paarungen vorhanden.")
      else:
        with st.form("result_form"):
          for p in pairings:
            p_id = p["id"]
            p_title = (
                f"Gang {p['gang']}: {p['schwinget_1']} vs. {p['schwinget_2']}"
            )
            current_res = p.get("result")

            res_options = [
                "Noch offen",
                "Sieg Schwinger 1",
                "Unentschieden (Gangluepf)",
                "Sieg Schwinger 2",
            ]
            default_idx = (
                res_options.index(current_res)
                if current_res in res_options
                else 0
            )

            selected_res = st.selectbox(
                p_title, res_options, index=default_idx, key=f"res_{p_id}"
            )

            if selected_res != "Noch offen":
              p["result"] = selected_res
            else:
              p["result"] = None

          save_results_btn = st.form_submit_button("Resultate speichern")
          if save_results_btn:
            save_data(PAIRINGS_FILE, pairings)
            st.success("Resultate aktualisiert und Rangliste berechnet!")
            st.rerun()

  elif admin_pw:
    st.error("Falsches Passwort.")