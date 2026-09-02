import json
import os
import streamlit as st

PAIRINGS_FILE = "pairings.json"
TIPS_FILE = "tips.json"
QUESTIONS_FILE = "questions.json"
SETTINGS_FILE = "settings.json"


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
questions = load_data(QUESTIONS_FILE, [])
settings = load_data(
    SETTINGS_FILE,
    {
        "admin_pw": "schwingen2026",
        "points_pairing": 1,
        "points_question": 2,
        "gang_locked": {},
    },
)

menu = st.sidebar.selectbox(
    "Navigation", ["Tippen & Rangliste", "Admin-Bereich"]
)

if menu == "Tippen & Rangliste":
  st.subheader("📲 Tipps abgeben")
  participant_name = st.text_input("Dein Name / Nickname:")

  if participant_name:
    st.write(f"Grüezi **{participant_name}**!")

    # Spieler direkt in die Tipps-Datenbank eintragen (damit er sofort in der Admin-Liste auftaucht)
    clean_name = participant_name.strip()
    if clean_name and clean_name not in tips:
      tips[clean_name] = {"pairings": {}, "questions": {}}
      save_data(TIPS_FILE, tips)

    user_data = tips.get(clean_name, {"pairings": {}, "questions": {}})

    tab_pairings, tab_questions = st.tabs(
        ["Gänge / Paarungen", "Zusatzfragen"]
    )

    with tab_pairings:
      if not pairings:
        st.info("Noch keine Paarungen erfasst.")
      else:
        with st.form("tipping_form_pairings"):
          new_user_pairings = user_data.get("pairings", {})
          locked_dict = settings.get("gang_locked", {})

          from itertools import groupby

          sorted_pairings = sorted(pairings, key=lambda x: x["gang"])

          for gang_nr, gang_pairings in groupby(
              sorted_pairings, key=lambda x: x["gang"]
          ):
            gang_str = str(gang_nr)
            is_locked = locked_dict.get(gang_str, False)

            with st.container(border=True):
              gang_header = f"### Gang {gang_nr}"
              if is_locked:
                gang_header += " 🔒 (Gesperrt)"
              st.markdown(gang_header)

              for p in gang_pairings:
                p_id = p["id"]
                s1 = p["schwinget_1"]
                s2 = p["schwinget_2"]

                default_tip = new_user_pairings.get(p_id, s1)
                options = [s1, "Gestellt", s2]
                default_idx = (
                    options.index(default_tip) if default_tip in options else 0
                )

                label = f"{s1} vs. {s2}"
                tip = st.selectbox(
                    label,
                    options,
                    index=default_idx,
                    key=f"tip_{p_id}",
                    disabled=is_locked,
                )
                new_user_pairings[p_id] = tip

          submit_p = st.form_submit_button("Paarung-Tipps speichern")
          if submit_p:
            user_data["pairings"] = new_user_pairings
            tips[clean_name] = user_data
            save_data(TIPS_FILE, tips)
            st.success("Paarungs-Tipps gespeichert!")

    with tab_questions:
      if not questions:
        st.info("Keine Zusatzfragen vorhanden.")
      else:
        with st.form("tipping_form_questions"):
          new_user_questions = user_data.get("questions", {})

          for q in questions:
            q_id = q["id"]
            q_text = q["question"]
            default_ans = new_user_questions.get(q_id, "")

            ans = st.text_input(
                q_text, value=default_ans, key=f"q_input_{q_id}"
            )
            new_user_questions[q_id] = ans

          submit_q = st.form_submit_button("Zusatzfragen speichern")
          if submit_q:
            user_data["questions"] = new_user_questions
            tips[clean_name] = user_data
            save_data(TIPS_FILE, tips)
            st.success("Zusatzfragen gespeichert!")

    # Live-Rangliste
    st.divider()
    st.subheader("📊 Live-Rangliste")
    if not tips:
      st.write("Noch keine Tipps abgegeben.")
    else:
      scores = []
      pts_p = settings.get("points_pairing", 1)
      pts_q = settings.get("points_question", 2)

      for name, data in tips.items():
        points = 0
        user_p = data.get("pairings", {})
        user_q = data.get("questions", {})

        for p in pairings:
          if p.get("result"):
            if user_p.get(p["id"]) == p["result"]:
              points += pts_p

        for q in questions:
          if q.get("result"):
            user_ans = str(user_q.get(q["id"], "")).strip().lower()
            correct_ans = str(q.get("result", "")).strip().lower()
            if user_ans and user_ans == correct_ans:
              points += pts_q

        scores.append({"Name": name, "Punkte": points})

      scores = sorted(scores, key=lambda x: x["Punkte"], reverse=True)
      st.table(scores)

  else:
    st.warning("Bitte gib deinen Namen ein, um deine Tipps abzugeben.")

elif menu == "Admin-Bereich":
  st.subheader("⚙️ Admin-Verwaltung")
  admin_pw = st.text_input("Admin-Passwort:", type="password")

  if admin_pw == settings.get("admin_pw", "schwingen2026"):
    st.success("Admin-Zugriff aktiv.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Paarungen & Gänge sperren",
        "Resultate Eintragen",
        "Zusatzfragen",
        "Teilnehmer & Übersicht",
        "Einstellungen & Punkte",
    ])

    with tab1:
      st.write("### 1. Neue Paarung erfassen")
      with st.form("add_pairing"):
        gang_nr = st.number_input(
            "Gang-Nummer", min_value=1, max_value=8, value=1
        )
        s1 = st.text_input("1. Schwinger")
        s2 = st.text_input("2. Schwinger")
        if st.form_submit_button("Paarung hinzufügen") and s1 and s2:
          new_id = str(len(pairings) + 1)
          pairings.append({
              "id": new_id,
              "gang": int(gang_nr),
              "schwinget_1": s1,
              "schwinget_2": s2,
              "result": None,
          })
          save_data(PAIRINGS_FILE, pairings)
          st.success("Hinzugefügt!")
          st.rerun()

      st.divider()
      st.write("### 2. Gänge manuell sperren / entsperren")
      existing_gangs = sorted(list(set([p["gang"] for p in pairings])))
      if not existing_gangs:
        st.info("Erstelle zuerst Paarungen, um Gänge zu sperren.")
      else:
        locked_dict = settings.get("gang_locked", {})
        with st.form("lock_gangs_form"):
          new_locked_dict = {}
          for g in existing_gangs:
            current_state = locked_dict.get(str(g), False)
            new_locked_dict[str(g)] = st.checkbox(
                f"Gang {g} für Tippabgabe sperren 🔒",
                value=current_state,
                key=f"lock_g_{g}",
            )

          if st.form_submit_button("Sperr-Status speichern"):
            settings["gang_locked"] = new_locked_dict
            save_data(SETTINGS_FILE, settings)
            st.success("Sperrungen aktualisiert!")
            st.rerun()

    with tab2:
      st.write("### Resultate für Paarungen eintragen")
      if not pairings:
        st.info("Keine Paarungen vorhanden.")
      else:
        with st.form("result_form"):
          for p in pairings:
            p_id = p["id"]
            s1 = p["schwinget_1"]
            s2 = p["schwinget_2"]
            p_title = f"Gang {p['gang']}: {s1} vs. {s2}"
            current_res = p.get("result")
            res_options = ["Noch offen", s1, "Gestellt", s2]
            default_idx = (
                res_options.index(current_res)
                if current_res in res_options
                else 0
            )

            selected_res = st.selectbox(
                p_title, res_options, index=default_idx, key=f"res_{p_id}"
            )
            p["result"] = None if selected_res == "Noch offen" else selected_res

          if st.form_submit_button("Resultate speichern"):
            save_data(PAIRINGS_FILE, pairings)
            st.success("Resultate aktualisiert!")
            st.rerun()

    with tab3:
      st.write("### Zusatzfragen verwalten")
      with st.form("add_question"):
        q_text = st.text_input("Zusatzfrage (z.B. Wer gewinnt das Schwingfest?)")
        if st.form_submit_button("Frage hinzufügen") and q_text:
          q_id = str(len(questions) + 1)
          questions.append({"id": q_id, "question": q_text, "result": None})
          save_data(QUESTIONS_FILE, questions)
          st.success("Frage hinzugefügt!")
          st.rerun()

      st.divider()
      st.write("### Richtige Antworten für Zusatzfragen eintragen")
      if not questions:
        st.info("Noch keine Zusatzfragen erfasst.")
      else:
        with st.form("q_result_form"):
          for q in questions:
            q_id = q["id"]
            current_res = q.get("result", "")
            q["result"] = st.text_input(
                f"Antwort für: '{q['question']}'",
                value=current_res if current_res else "",
                key=f"q_res_{q_id}",
            )

          if st.form_submit_button("Antworten speichern"):
            save_data(QUESTIONS_FILE, questions)
            st.success("Zusatzfragen-Resultate gespeichert!")
            st.rerun()

    with tab4:
      st.write("### 👥 Wer hat gespielt & Vollständigkeit")
      if not tips:
        st.info("Bisher haben sich noch keine Teilnehmer registriert.")
      else:
        participant_overview = []
        total_pairings = len(pairings)
        total_questions = len(questions)

        for name, data in tips.items():
          user_p = data.get("pairings", {})
          user_q = data.get("questions", {})

          filled_pairings = sum(
              1 for p in pairings if user_p.get(p["id"]) is not None
          )
          filled_questions = sum(
              1
              for q in questions
              if str(user_q.get(q["id"], "")).strip() != ""
          )

          p_status = (
              f"✅ Alle ({filled_pairings}/{total_pairings})"
              if total_pairings > 0 and filled_pairings == total_pairings
              else f"⚠️ Noch offen ({filled_pairings}/{total_pairings})"
          )
          q_status = (
              f"✅ Alle ({filled_questions}/{total_questions})"
              if total_questions > 0 and filled_questions == total_questions
              else f"⚠️ Noch offen ({filled_questions}/{total_questions})"
          )

          if total_pairings == 0:
            p_status = "Keine Paarungen da"
          if total_questions == 0:
            q_status = "Keine Fragen da"

          participant_overview.append({
              "Name": name,
              "Paarungs-Tipps": p_status,
              "Zusatzfragen": q_status,
          })

        st.table(participant_overview)

    with tab5:
      st.write("### Einstellungen & Punkte")
      with st.form("settings_form"):
        p_p = st.number_input(
            "Punkte pro richtigem Paarungs-Tipp",
            min_value=1,
            max_value=10,
            value=settings.get("points_pairing", 1),
        )
        p_q = st.number_input(
            "Punkte pro richtiger Zusatzfrage",
            min_value=1,
            max_value=20,
            value=settings.get("points_question", 2),
        )
        new_pw = st.text_input(
            "Admin-Passwort ändern", value=settings.get("admin_pw", "")
        )

        submit_settings = st.form_submit_button("Einstellungen speichern")
        if submit_settings:
          settings["points_pairing"] = int(p_p)
          settings["points_question"] = int(p_q)
          if new_pw:
            settings["admin_pw"] = new_pw
          save_data(SETTINGS_FILE, settings)
          st.success("Einstellungen erfolgreich aktualisiert!")
          st.rerun()

      st.divider()
      st.write("### ⚠️ Reset / Testdaten löschen")
      st.warning(
          "Achtung: Dies löscht alle Paarungen, Tipps, Zusatzfragen und"
          " Resultate unwiderruflich!"
      )

      if st.button("🔄 Alles zurücksetzen (Reset)"):
        for f in [PAIRINGS_FILE, TIPS_FILE, QUESTIONS_FILE]:
          if os.path.exists(f):
            os.remove(f)
        settings["gang_locked"] = {}
        save_data(SETTINGS_FILE, settings)
        st.success(
            "Alles erfolgreich zurückgesetzt! Die App ist wieder leer."
        )
        st.rerun()

  elif admin_pw:
    st.error("Falsches Passwort.")
