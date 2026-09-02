import json
import os
import streamlit as st

PAIRINGS_FILE = "pairings.json"
TIPS_FILE = "tips.json"
QUESTIONS_FILE = "questions.json"
SETTINGS_FILE = "settings.json"
PARTICIPANTS_FILE = "participants.json"


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
participants_list = load_data(PARTICIPANTS_FILE, [])
settings = load_data(
    SETTINGS_FILE,
    {
        "admin_pw": "schwingen2026",
        "points_pairing": 1,
        "points_question": 2,
        "bonus_pairing_round": 2,
        "bonus_question_round": 2,
        "gang_locked": {},
    },
)

menu = st.sidebar.selectbox(
    "Navigation", ["Tippen & Rangliste", "Admin-Bereich"]
)

if menu == "Tippen & Rangliste":
  # --- 1. LIVE-RANGLISTE OBEN AUF DER SEITE (MODERNISIERT) ---
  st.subheader("📊 Live-Rangliste")
  if not tips:
    st.info(
        "Bisher hat noch niemand getippt. Wähle deinen Namen aus und starte!"
    )
  else:
    pts_p = settings.get("points_pairing", 1)
    pts_q = settings.get("points_question", 2)
    bonus_p_val = settings.get("bonus_pairing_round", 2)
    bonus_q_val = settings.get("bonus_question_round", 2)

    user_stats = {}
    for name, data in tips.items():
      user_p_tips = data.get("pairings", {})
      user_q_tips = data.get("questions", {})

      p_points_total = 0
      q_points_total = 0
      gang_points_map = {}
      q_points_val = 0

      from itertools import groupby

      sorted_pairings = sorted(pairings, key=lambda x: x["gang"])
      for gang_nr, gang_pairings in groupby(
          sorted_pairings, key=lambda x: x["gang"]
      ):
        g_pts = 0
        for p in gang_pairings:
          if p.get("result"):
            if user_p_tips.get(p["id"]) == p["result"]:
              g_pts += pts_p
        gang_points_map[gang_nr] = g_pts
        p_points_total += g_pts

      for q in questions:
        if q.get("result"):
          user_ans = str(user_q_tips.get(q["id"], "")).strip().lower()
          correct_ans = str(q.get("result", "")).strip().lower()
          if user_ans and user_ans == correct_ans:
            q_points_val += pts_q
      q_points_total = q_points_val

      user_stats[name] = {
          "gang_points_map": gang_points_map,
          "q_points": q_points_total,
          "p_points": p_points_total,
          "bonus_p": 0,
          "bonus_q": 0,
      }

    existing_gangs = set(p["gang"] for p in pairings)
    for g in existing_gangs:
      gang_has_results = any(
          p.get("result") for p in pairings if p["gang"] == g
      )
      if gang_has_results:
        max_g_pts = -1
        leaders = []
        for name, stats in user_stats.items():
          pts = stats["gang_points_map"].get(g, 0)
          if pts > max_g_pts:
            max_g_pts = pts
            leaders = [name]
          elif pts == max_g_pts:
            leaders.append(name)

        if max_g_pts > 0:
          for leader in leaders:
            user_stats[leader]["bonus_p"] += bonus_p_val

    questions_has_results = any(q.get("result") for q in questions)
    if questions_has_results and questions:
      max_q_pts = -1
      q_leaders = []
      for name, stats in user_stats.items():
        pts = stats["q_points"]
        if pts > max_q_pts:
          max_q_pts = pts
          q_leaders = [name]
        elif pts == max_q_pts:
          q_leaders.append(name)

      if max_q_pts > 0:
        for leader in q_leaders:
          user_stats[leader]["bonus_q"] += bonus_q_val

    scores = []
    for name, stats in user_stats.items():
      total = (
          stats["p_points"]
          + stats["q_points"]
          + stats["bonus_p"]
          + stats["bonus_q"]
      )
      scores.append({
          "Name": name,
          "Total": total,
          "Gänge": stats["p_points"],
          "Bonus Gänge": stats["bonus_p"],
          "Fragen": stats["q_points"],
          "Bonus Fragen": stats["bonus_q"],
      })

    scores = sorted(scores, key=lambda x: x["Total"], reverse=True)

    # Schöneres UI für die Rangliste rendern
    current_rank = 1
    for i, entry in enumerate(scores):
      if i > 0 and entry["Total"] < scores[i - 1]["Total"]:
        current_rank = i + 1

      # Rang-Darstellung (ohne zusätzliche Zahl bei Medaillen)
      if current_rank == 1:
        rank_display = "🥇"
      elif current_rank == 2:
        rank_display = "🥈"
      elif current_rank == 3:
        rank_display = "🥉"
      else:
        rank_display = f"#{current_rank}"

      # Container für jeden Rang erstellen
      with st.container(border=True):
        col1, col2, col3 = st.columns([1, 4, 2])

        with col1:
          st.markdown(
              f"<h2 style='text-align: center; margin: 0;'>{rank_display}</h2>",
              unsafe_allow_html=True,
          )

        with col2:
          st.markdown(
              f"<h4 style='margin: 0; padding-top: 4px;'>{entry['Name']}</h4>",
              unsafe_allow_html=True,
          )
          st.caption(
              f"Gänge: {entry['Gänge']} P. (+{entry['Bonus Gänge']} B.) | "
              f"Fragen: {entry['Fragen']} P. (+{entry['Bonus Fragen']} B.)"
          )

        with col3:
          st.markdown(
              f"<div style='text-align: right;'><span"
              f" style='font-size: 0.8rem; color: gray;'>Total</span><br><b"
              f" style='font-size: 1.4rem; color: #ff4b4b;'>{entry['Total']}"
              " Pkt.</b></div>",
              unsafe_allow_html=True,
          )

  st.divider()

  # --- 2. TIPPS ABGEBEN UNTEN ---
  st.subheader("📲 Tipps abgeben")

  if participants_list:
    options_names = ["-- Bitte wählen --"] + sorted(participants_list)
    selected_participant = st.selectbox("Wähle deinen Namen aus:", options_names)
    participant_name = (
        "" if selected_participant == "-- Bitte wählen --" else selected_participant
    )
  else:
    st.info(
        "💡 Tipp: Im Admin-Bereich kannst du eine Teilnehmer-Liste (oder das"
        " PDF) hochladen, damit hier ein Auswahlmenü erscheint."
    )
    participant_name = st.text_input("Dein Name / Nickname:")

  if participant_name:
    st.write(f"Grüezi **{participant_name}**!")

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
            st.rerun()

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
            st.rerun()

  else:
    st.warning("Bitte wähle deinen Namen aus, um deine Tipps abzugeben.")

elif menu == "Admin-Bereich":
  st.subheader("⚙️ Admin-Verwaltung")
  admin_pw = st.text_input("Admin-Passwort:", type="password")

  if admin_pw == settings.get("admin_pw", "schwingen2026"):
    st.success("Admin-Zugriff aktiv.")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Paarungen & Gänge sperren",
        "Resultate Eintragen",
        "Zusatzfragen",
        "Teilnehmer-Import & Verwaltung",
        "Teilnehmer & Übersicht",
        "Einstellungen & Punkte",
    ])

    with tab1:
      st.write("### 1. Neue Paarung erfassen")
      with st.form("add_pairing"):
        gang_nr = st.number_input(
            "Gang-Nummer", min_value=1, max_value=8, value=1
        )
        s1 = st.text_input("1. Schwinger (z.B. Aeschbacher Matthias, S ***)")
        s2 = st.text_input("2. Schwinger (z.B. Giger Samuel, S ***)")
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

            res_options = ["-", s1, "Gestellt", s2]
            default_idx = (
                res_options.index(current_res)
                if current_res in res_options
                else 0
            )

            selected_res = st.selectbox(
                p_title, res_options, index=default_idx, key=f"res_{p_id}"
            )
            p["result"] = None if selected_res == "-" else selected_res

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
      st.write("### 📄 Teilnehmer-Liste verwalten (PDF & Manuell)")
      st.markdown(
          "Offizielle Startliste herunterladen: "
          "[Startliste ESV (PDF)](https://kilchberger-schwinget.ch/files/folder.28/startliste-esv.pdf)"
          ""
      )

      st.divider()
      st.write("#### A) Teilnehmer manuell hinzufügen oder löschen")

      with st.form("add_single_participant"):
        new_part = st.text_input("Name des neuen Teilnehmers")
        if st.form_submit_button("Teilnehmer hinzufügen") and new_part:
          clean_np = new_part.strip()
          if clean_np and clean_np not in participants_list:
            participants_list.append(clean_np)
            save_data(PARTICIPANTS_FILE, sorted(participants_list))
            st.success(f"'{clean_np}' hinzugefügt!")
            st.rerun()
          else:
            st.warning("Name ist leer oder existiert bereits.")

      if participants_list:
        with st.form("delete_participant_form"):
          del_part = st.selectbox(
              "Teilnehmer zum Löschen auswählen", sorted(participants_list)
          )
          if st.form_submit_button("Ausgewählten Teilnehmer löschen"):
            participants_list.remove(del_part)
            save_data(PARTICIPANTS_FILE, participants_list)
            st.success(f"'{del_part}' wurde gelöscht.")
            st.rerun()

      st.divider()
      st.write("#### B) Per PDF-Upload einlesen")
      uploaded_pdf = st.file_uploader(
          "Teilnehmer-PDF hochladen", type=["pdf", "txt"]
      )

      if uploaded_pdf is not None:
        extracted_names = []
        if uploaded_pdf.name.endswith(".pdf"):
          try:
            import pypdf

            reader = pypdf.PdfReader(uploaded_pdf)
            for page in reader.pages:
              text = page.extract_text()
              if text:
                for line in text.split("\n"):
                  clean_line = line.strip()
                  if clean_line and len(clean_line) > 2:
                    extracted_names.append(clean_line)
          except Exception as e:
            st.error(
                f"Fehler beim Lesen des PDFs: {e}. Ist 'pypdf' installiert?"
            )
        else:
          stringio = uploaded_pdf.getvalue().decode("utf-8")
          for line in stringio.split("\n"):
            clean_line = line.strip()
            if clean_line:
              extracted_names.append(clean_line)

        if extracted_names:
          st.write(
              f"Gefundene Einträge (Vorschau):", extracted_names[:10]
          )
          if st.button("Ausgelesene Namen zur Liste hinzufügen"):
            combined = list(set(participants_list + extracted_names))
            save_data(PARTICIPANTS_FILE, sorted(combined))
            st.success("Namen erfolgreich zur Teilnehmerliste hinzugefügt!")
            st.rerun()

      if participants_list:
        st.divider()
        st.write(
            f"**Aktuell hinterlegte Teilnehmer ({len(participants_list)}):**"
        )
        st.write(", ".join(participants_list))

        if st.button("Komplette Teilnehmer-Liste leeren"):
          if os.path.exists(PARTICIPANTS_FILE):
            os.remove(PARTICIPANTS_FILE)
          st.success("Teilnehmer-Liste komplett gelöscht.")
          st.rerun()

    with tab5:
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

    with tab6:
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
        b_p = st.number_input(
            "Bonuspunkte für den Rundensieger (pro Gang)",
            min_value=0,
            max_value=10,
            value=settings.get("bonus_pairing_round", 2),
        )
        b_q = st.number_input(
            "Bonuspunkte für den Sieger der Zusatzfragen",
            min_value=0,
            max_value=10,
            value=settings.get("bonus_question_round", 2),
        )
        new_pw = st.text_input(
            "Admin-Passwort ändern", value=settings.get("admin_pw", "")
        )

        submit_settings = st.form_submit_button("Einstellungen speichern")
        if submit_settings:
          settings["points_pairing"] = int(p_p)
          settings["points_question"] = int(p_q)
          settings["bonus_pairing_round"] = int(b_p)
          settings["bonus_question_round"] = int(b_q)
          if new_pw:
            settings["admin_pw"] = new_pw
          save_data(SETTINGS_FILE, settings)
          st.success("Einstellungen erfolgreich aktualisiert!")
          st.rerun()

      st.divider()
      st.write("### 🧪 Test-Daten generieren")
      if st.button("🚀 Test-Dummies erstellen"):
        dummy_pairings = [
            {
                "id": "1",
                "gang": 1,
                "schwinget_1": "Aeschbacher Matthias, S ***",
                "schwinget_2": "Vianin Pierre, S *",
                "result": "Aeschbacher Matthias, S ***",
            },
            {
                "id": "2",
                "gang": 1,
                "schwinget_1": "Giger Samuel, S ***",
                "schwinget_2": "Staudenmann Fabian, S ***",
                "result": "Gestellt",
            },
        ]
        save_data(PAIRINGS_FILE, dummy_pairings)

        dummy_questions = [
            {
                "id": "1",
                "question": "Wer gewinnt den Schlussgang?",
                "result": "Giger Samuel, S ***",
            }
        ]
        save_data(QUESTIONS_FILE, dummy_questions)

        dummy_participants = ["Hansueli", "Heiri", "Vreni"]
        save_data(PARTICIPANTS_FILE, dummy_participants)

        dummy_tips = {
            "Hansueli": {
                "pairings": {
                    "1": "Aeschbacher Matthias, S ***",
                    "2": "Gestellt",
                },
                "questions": {"1": "Giger Samuel, S ***"},
            }
        }
        save_data(TIPS_FILE, dummy_tips)

        st.success("Test-Daten erfolgreich erstellt!")
        st.rerun()

      st.divider()
      st.write("### ⚠️ Reset / Testdaten löschen")
      if st.button("🔄 Alles zurücksetzen (Reset)"):
        for f in [
            PAIRINGS_FILE,
            TIPS_FILE,
            QUESTIONS_FILE,
            PARTICIPANTS_FILE,
        ]:
          if os.path.exists(f):
            os.remove(f)
        settings["gang_locked"] = {}
        save_data(SETTINGS_FILE, settings)
        st.success("Alles zurückgesetzt!")
        st.rerun()

  elif admin_pw:
    st.error("Falsches Passwort.")
