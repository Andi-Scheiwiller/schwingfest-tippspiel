import json
import os
import streamlit as st

PAIRINGS_FILE = "pairings.json"
TIPS_FILE = "tips.json"
QUESTIONS_FILE = "questions.json"
SETTINGS_FILE = "settings.json"
PARTICIPANTS_FILE = "participants.json"

# --- ZENTRALE SCHWINGER-LISTE (ALLE SCHWINGER MIT STERNEN) ---
ALL_SCHWINGER = [
    "Aeschbacher Matthias ***",
    "Alpiger Nick ***",
    "Bieri Marcel ***",
    "Bissig Lukas ***",
    "Burger Matthieu ***",
    "Collaud Romain ***",
    "Giger Samuel ***",
    "Gwerder Michael ***",
    "Kramer Lario ***",
    "Lüscher Sinisha ***",
    "Lustenberger Marc ***",
    "Moser Michael ***",
    "Orlik Armon ***",
    "Schlegel Werner ***",
    "Staudenmann Fabian ***",
    "Strebel Joel ***",
    "Ott Damian ***",
    "Zaugg Lars **",
    "Schwyzer Samuel **",
]

# --- FEST DEFINIERTE STANDARD-PAARUNGEN (1. GANG) ---
DEFAULT_PAIRINGS = [
    {
        "id": "1",
        "gang": 1,
        "schwinget_1": "Schwyzer Samuel **",
        "schwinget_2": "Zaugg Lars **",
        "result": None,
    },
    {
        "id": "2",
        "gang": 1,
        "schwinget_1": "Bieri Marcel ***",
        "schwinget_2": "Kramer Lario ***",
        "result": None,
    },
    {
        "id": "3",
        "gang": 1,
        "schwinget_1": "Collaud Romain ***",
        "schwinget_2": "Strebel Joel ***",
        "result": None,
    },
    {
        "id": "4",
        "gang": 1,
        "schwinget_1": "Gwerder Michael ***",
        "schwinget_2": "Lüscher Sinisha ***",
        "result": None,
    },
    {
        "id": "5",
        "gang": 1,
        "schwinget_1": "Bissig Lukas ***",
        "schwinget_2": "Ott Damian ***",
        "result": None,
    },
    {
        "id": "6",
        "gang": 1,
        "schwinget_1": "Burger Matthieu ***",
        "schwinget_2": "Lustenberger Marc ***",
        "result": None,
    },
    {
        "id": "7",
        "gang": 1,
        "schwinget_1": "Aeschbacher Matthias ***",
        "schwinget_2": "Giger Samuel ***",
        "result": None,
    },
    {
        "id": "8",
        "gang": 1,
        "schwinget_1": "Alpiger Nick ***",
        "schwinget_2": "Walther Adrian ***",
        "result": None,
    },
    {
        "id": "9",
        "gang": 1,
        "schwinget_1": "Moser Michael ***",
        "schwinget_2": "Schlegel Werner ***",
        "result": None,
    },
    {
        "id": "10",
        "gang": 1,
        "schwinget_1": "Orlik Armon ***",
        "schwinget_2": "Staudenmann Fabian ***",
        "result": None,
    },
]

# --- FEST DEFINIERTE ZUSATZFRAGEN ---
DEFAULT_QUESTIONS = [
    {
        "id": "q1",
        "question": "Wie viele Gänge gewinnt Andy?",
        "type": "gang_count",
        "result": None,
    },
    {
        "id": "q2",
        "question": "Schlussgangteilnehmer 1",
        "type": "schwinger",
        "result": None,
    },
    {
        "id": "q3",
        "question": "Schlussgangteilnehmer 2",
        "type": "schwinger",
        "result": None,
    },
    {
        "id": "q4",
        "question": (
            "Wer wird Festsieger? (bei mehreren Siegern gilt der Erstplatzierte"
            " 1a)"
        ),
        "type": "schwinger",
        "result": None,
    },
    {
        "id": "q5",
        "question": "Bester Schwinger NOS",
        "type": "schwinger",
        "result": None,
    },
    {
        "id": "q6",
        "question": "Bester Schwinger BKSV",
        "type": "schwinger",
        "result": None,
    },
    {
        "id": "q7",
        "question": "Bester Schwinger ISV",
        "type": "schwinger",
        "result": None,
    },
    {
        "id": "q8",
        "question": "Bester Schwinger NWSV",
        "type": "schwinger",
        "result": None,
    },
    {
        "id": "q9",
        "question": "Bester Schwinger SWSV",
        "type": "schwinger",
        "result": None,
    },
]


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
    page_title="Tippspiel Kilchberger Schwinget",
    page_icon="🇨🇭",
    layout="centered",
)

st.title("🏆 Tippspiel Kilchberger Schwinget")

# Daten laden
pairings = load_data(PAIRINGS_FILE, DEFAULT_PAIRINGS)
if not pairings:
  pairings = DEFAULT_PAIRINGS
  save_data(PAIRINGS_FILE, pairings)

questions = load_data(QUESTIONS_FILE, DEFAULT_QUESTIONS)
if not questions:
  questions = DEFAULT_QUESTIONS
  save_data(QUESTIONS_FILE, questions)

tips = load_data(TIPS_FILE, {})
participants_list = load_data(PARTICIPANTS_FILE, [])
settings = load_data(
    SETTINGS_FILE,
    {
        "admin_pw": "schwingen2026",
        "points_pairing": 1,
        "question_points": {
            "q1": 2,
            "q2": 3,
            "q3": 3,
            "q4": 5,
            "q5": 2,
            "q6": 2,
            "q7": 2,
            "q8": 2,
            "q9": 2,
        },
        "bonus_pairing_round": 2,
        "bonus_question_round": 2,
        "gang_locked": {},
    },
)

# Hauptnavigation
menu = st.sidebar.selectbox("Navigation", ["Tippspiel", "Admin-Bereich"])

if menu == "Tippspiel":
  tab_tipp, tab_rang = st.tabs(["📝 Tipps abgeben", "📊 Live-Rangliste"])

  # --- TAB 1: TIPPS ABGEBEN ---
  with tab_tipp:
    st.subheader("📲 Tipps erfassen")
    st.write("")

    participant_name = ""

    if participants_list:
      name_options = (
          ["-- Bitte wählen --", "+ Name erfassen"] + sorted(participants_list)
      )
      selected_option = st.selectbox("Wähle deinen Namen aus:", name_options)

      if selected_option == "+ Name erfassen":
        new_typed_name = st.text_input(
            "Gib deinen Namen / Nickname ein (wird automatisch zur"
            " Tippspiel-Liste hinzugefügt):"
        )
        if new_typed_name:
          participant_name = new_typed_name.strip()
          if participant_name and participant_name not in participants_list:
            participants_list.append(participant_name)
            save_data(PARTICIPANTS_FILE, sorted(participants_list))
      elif selected_option != "-- Bitte wählen --":
        participant_name = selected_option
    else:
      new_typed_name = st.text_input(
          "Dein Name / Nickname (wird automatisch gespeichert):"
      )
      if new_typed_name:
        participant_name = new_typed_name.strip()
        if participant_name and participant_name not in participants_list:
          participants_list.append(participant_name)
          save_data(PARTICIPANTS_FILE, sorted(participants_list))

    if participant_name:
      st.write("")
      clean_name = participant_name.strip()

      user_entry = tips.get(clean_name, None)
      has_pin_stored = (
          isinstance(user_entry, dict)
          and "pin" in user_entry
          and user_entry["pin"]
      )
      access_granted = False

      if not has_pin_stored:
        st.info(
            f"🔑 **{clean_name}**, du hast noch keine Geheimzahl (PIN) gesetzt."
            " Bitte lege jetzt eine 2-stellige PIN fest:"
        )
        with st.form(f"set_pin_form_{clean_name}"):
          new_pin_input = st.text_input(
              "2-stellige Geheimzahl (z.B. 12):",
              max_chars=4,
              type="password",
          )
          pin_submit = st.form_submit_button("PIN festlegen & starten")
          if pin_submit:
            if (
                new_pin_input
                and new_pin_input.isdigit()
                and len(new_pin_input) >= 2
            ):
              existing_data = (
                  user_entry.get("data", {"pairings": {}, "questions": {}})
                  if isinstance(user_entry, dict) and "pin" in user_entry
                  else (
                      user_entry
                      if isinstance(user_entry, dict)
                      else {"pairings": {}, "questions": {}}
                  )
              )
              tips[clean_name] = {"pin": new_pin_input, "data": existing_data}
              save_data(TIPS_FILE, tips)
              st.success("PIN erfolgreich gespeichert!")
              st.rerun()
            else:
              st.error(
                  "Bitte gib eine gültige, mindestens 2-stellige Zahl ein."
              )
      else:
        entered_pin = st.text_input(
            f"🔐 Gib deine 2-stellige Geheimzahl für **{clean_name}** ein:",
            max_chars=4,
            type="password",
            key=f"login_pin_{clean_name}",
        )

        stored_pin = user_entry.get("pin")
        if entered_pin == stored_pin:
          access_granted = True
        elif entered_pin:
          st.error("❌ Falsche Geheimzahl!")

      if access_granted:
        st.success(f"🔓 Willkommen zurück, **{clean_name}**!")
        st.write("")

        user_data = user_entry.get("data", {"pairings": {}, "questions": {}})

        sub_tab_p, sub_tab_q = st.tabs(["Gänge / Paarungen", "Zusatzfragen"])

        with sub_tab_p:
          st.write("")
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
                  st.write("")

                  for p in gang_pairings:
                    p_id = p["id"]
                    s1 = p["schwinget_1"]
                    s2 = p["schwinget_2"]

                    default_tip = new_user_pairings.get(p_id, "-")
                    options = ["-", s1, "Gestellt", s2]
                    default_idx = (
                        options.index(default_tip)
                        if default_tip in options
                        else 0
                    )

                    label = f"{s1}  ⚔️  {s2}"
                    tip = st.selectbox(
                        label,
                        options,
                        index=default_idx,
                        key=f"tip_{p_id}",
                        disabled=is_locked,
                    )
                    new_user_pairings[p_id] = tip
                    st.write("")

              st.write("")
              submit_p = st.form_submit_button("Paarung-Tipps speichern")
              if submit_p:
                user_data["pairings"] = new_user_pairings
                tips[clean_name]["data"] = user_data
                save_data(TIPS_FILE, tips)
                st.success("Paarungs-Tipps gespeichert!")
                st.rerun()

        with sub_tab_q:
          st.write("")
          if not questions:
            st.info("Noch keine Zusatzfragen vorhanden.")
          else:
            with st.form("tipping_form_questions"):
              new_user_questions = user_data.get("questions", {})

              for q in questions:
                q_id = q["id"]
                q_text = q["question"]
                q_type = q.get("type", "schwinger")
                default_ans = new_user_questions.get(q_id, "")

                if q_type == "gang_count":
                  gang_options = ["-"] + [str(i) for i in range(1, 7)]
                  default_idx = (
                      gang_options.index(default_ans)
                      if default_ans in gang_options
                      else 0
                  )
                  ans = st.selectbox(
                      q_text, gang_options, index=default_idx, key=f"q_sel_{q_id}"
                  )
                  new_user_questions[q_id] = None if ans == "-" else ans
                else:
                  schwinger_options = ["-"] + sorted(ALL_SCHWINGER)
                  default_idx = (
                      schwinger_options.index(default_ans)
                      if default_ans in schwinger_options
                      else 0
                  )
                  ans = st.selectbox(
                      q_text,
                      schwinger_options,
                      index=default_idx,
                      key=f"q_sel_{q_id}",
                  )
                  new_user_questions[q_id] = None if ans == "-" else ans

                st.write("")

              submit_q = st.form_submit_button("Zusatzfragen speichern")
              if submit_q:
                user_data["questions"] = new_user_questions
                tips[clean_name]["data"] = user_data
                save_data(TIPS_FILE, tips)
                st.success("Zusatzfragen gespeichert!")
                st.rerun()

    else:
      st.warning(
          "Bitte wähle deinen Namen aus oder tippe einen neuen ein, um deine"
          " Tipps abzugeben."
      )

  # --- TAB 2: LIVE-RANGLISTE ---
  with tab_rang:
    st.subheader("📊 Live-Rangliste")
    st.write("")

    if not tips:
      st.info(
          "Bisher hat noch niemand getippt. Wähle deinen Namen aus und starte!"
      )
    else:
      pts_p = settings.get("points_pairing", 1)
      q_points_config = settings.get("question_points", {})
      bonus_p_val = settings.get("bonus_pairing_round", 2)
      bonus_q_val = settings.get("bonus_question_round", 2)

      user_stats = {}
      for name, entry_val in tips.items():
        if isinstance(entry_val, dict) and "data" in entry_val:
          data = entry_val["data"]
        else:
          data = entry_val

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
              tip_val = user_p_tips.get(p["id"])
              if tip_val and tip_val != "-" and tip_val == p["result"]:
                g_pts += pts_p
          gang_points_map[gang_nr] = g_pts
          p_points_total += g_pts

        for q in questions:
          q_id = q["id"]
          if q.get("result"):
            user_ans = str(user_q_tips.get(q_id, "")).strip().lower()
            correct_ans = str(q.get("result", "")).strip().lower()
            if user_ans and user_ans == correct_ans:
              q_points_val += q_points_config.get(q_id, 2)
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

      current_rank = 1
      for i, entry in enumerate(scores):
        if i > 0 and entry["Total"] < scores[i - 1]["Total"]:
          current_rank = i + 1

        if current_rank == 1:
          rank_display = "🥇"
        elif current_rank == 2:
          rank_display = "🥈"
        elif current_rank == 3:
          rank_display = "🥉"
        else:
          rank_display = f"#{current_rank}"

        with st.container(border=True):
          col1, col2, col3 = st.columns([1.2, 3.8, 2])

          with col1:
            st.markdown(
                f"<div style='font-size: 1.2rem; font-weight: bold; text-align:"
                f" center; padding-top: 6px;'>{rank_display}</div>",
                unsafe_allow_html=True,
            )

          with col2:
            st.markdown(
                f"<div style='font-size: 1rem; font-weight: bold; margin: 0;"
                f" line-height: 1.2;'>{entry['Name']}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='font-size: 0.75rem; color: gray; margin-top:"
                f" 2px;'>G: {entry['Gänge']} (+{entry['Bonus Gänge']}B) | F:"
                f" {entry['Fragen']} (+{entry['Bonus Fragen']}B)</div>",
                unsafe_allow_html=True,
            )

          with col3:
            st.markdown(
                f"<div style='text-align: right;'><span"
                f" style='font-size: 0.75rem; color: gray;'>Total</span><br><b"
                f" style='font-size: 1.2rem; color: #ff4b4b;'>{entry['Total']}"
                " Pkt.</b></div>",
                unsafe_allow_html=True,
            )

elif menu == "Admin-Bereich":
  st.subheader("⚙️ Admin-Verwaltung")
  admin_pw = st.text_input("Admin-Passwort:", type="password")

  if admin_pw == settings.get("admin_pw", "schwingen2026"):
    st.success("Admin-Zugriff aktiv.")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Paarungen & Gänge sperren",
        "Resultate Eintragen",
        "Zusatzfragen",
        "Tippspiel-Teilnehmer",
        "Wer hat gespielt?",
        "Einstellungen & Punkte",
    ])

    with tab1:
      st.write("### 1. Neue Paarung erfassen")
      with st.form("add_pairing"):
        gang_nr = st.number_input(
            "Gang-Nummer", min_value=1, max_value=8, value=1
        )
        s1 = st.selectbox("1. Schwinger", sorted(ALL_SCHWINGER), key="admin_s1")
        s2 = st.selectbox("2. Schwinger", sorted(ALL_SCHWINGER), key="admin_s2")
        if st.form_submit_button("Paarung hinzufügen"):
          if s1 == s2:
            st.error("Ein Schwinger kann nicht gegen sich selbst antreten.")
          else:
            new_id = str(len(pairings) + 1)
            pairings.append({
                "id": new_id,
                "gang": int(gang_nr),
                "schwinget_1": s1,
                "schwinget_2": s2,
                "result": None,
            })
            save_data(PAIRINGS_FILE, pairings)
            st.success("Paarung hinzugefügt!")
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
            p_title = f"Gang {p['gang']}: {s1}  ⚔️  {s2}"
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
      st.write("### Richtige Antworten für Zusatzfragen eintragen")
      if not questions:
        st.info("Noch keine Zusatzfragen erfasst.")
      else:
        with st.form("q_result_form"):
          for q in questions:
            q_id = q["id"]
            q_text = q["question"]
            q_type = q.get("type", "schwinger")
            current_res = q.get("result", "")

            if q_type == "gang_count":
              gang_options = ["-"] + [str(i) for i in range(1, 7)]
              default_idx = (
                  gang_options.index(current_res)
                  if current_res in gang_options
                  else 0
              )
              selected_res = st.selectbox(
                  f"Antwort für: '{q_text}'",
                  gang_options,
                  index=default_idx,
                  key=f"q_res_{q_id}",
              )
              q["result"] = None if selected_res == "-" else selected_res
            else:
              schwinger_options = ["-"] + sorted(ALL_SCHWINGER)
              default_idx = (
                  schwinger_options.index(current_res)
                  if current_res in schwinger_options
                  else 0
              )
              selected_res = st.selectbox(
                  f"Antwort für: '{q_text}'",
                  schwinger_options,
                  index=default_idx,
                  key=f"q_res_{q_id}",
              )
              q["result"] = None if selected_res == "-" else selected_res

          if st.form_submit_button("Antworten speichern"):
            save_data(QUESTIONS_FILE, questions)
            st.success("Zusatzfragen-Resultate gespeichert!")
            st.rerun()

    with tab4:
      st.write("### 👥 Tippspiel-Teilnehmer verwalten")
      with st.form("add_single_participant"):
        new_part = st.text_input(
            "Name des Tippspiel-Teilnehmers (z. B. Hansueli)"
        )
        if st.form_submit_button("Teilnehmer hinzufügen") and new_part:
          clean_np = new_part.strip()
          if clean_np and clean_np not in participants_list:
            participants_list.append(clean_np)
            save_data(PARTICIPANTS_FILE, sorted(participants_list))
            st.success(f"Tippspiel-Teilnehmer '{clean_np}' hinzugefügt!")
            st.rerun()
          else:
            st.warning("Name ist leer oder existiert bereits.")

      if participants_list:
        st.divider()
        with st.form("edit_delete_participant_form"):
          selected_to_edit = st.selectbox(
              "Teilnehmer auswählen", sorted(participants_list)
          )
          edited_name = st.text_input(
              "Namen korrigieren / umbenennen:", value=selected_to_edit
          )

          col_e1, col_e2 = st.columns(2)
          with col_e1:
            save_edit = st.form_submit_button("Änderung speichern")
          with col_e2:
            delete_clicked = st.form_submit_button("Teilnehmer löschen")

          if save_edit:
            clean_edited = edited_name.strip()
            if clean_edited and clean_edited != selected_to_edit:
              if clean_edited in participants_list:
                st.error("Dieser Name existiert bereits in der Liste.")
              else:
                idx = participants_list.index(selected_to_edit)
                participants_list[idx] = clean_edited
                save_data(PARTICIPANTS_FILE, sorted(participants_list))
                if selected_to_edit in tips:
                  tips[clean_edited] = tips.pop(selected_to_edit)
                  save_data(TIPS_FILE, tips)
                st.success(
                    f"Teilnehmer von '{selected_to_edit}' zu '{clean_edited}'"
                    " geändert!"
                )
                st.rerun()

          if delete_clicked:
            participants_list.remove(selected_to_edit)
            save_data(PARTICIPANTS_FILE, participants_list)
            st.success(f"Tippspiel-Teilnehmer '{selected_to_edit}' wurde gelöscht.")
            st.rerun()

        st.divider()
        st.write(f"**Aktuelle Teilnehmer ({len(participants_list)}):**")
        st.write(", ".join(participants_list))

        if st.button("Komplette Tippspiel-Teilnehmer-Liste leeren"):
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

        for name, entry_val in tips.items():
          if isinstance(entry_val, dict) and "data" in entry_val:
            data = entry_val["data"]
          else:
            data = entry_val

          user_p = data.get("pairings", {})
          user_q = data.get("questions", {})

          filled_pairings = sum(
              1
              for p in pairings
              if user_p.get(p["id"]) is not None
              and user_p.get(p["id"]) != "-"
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

        st.write("#### Punkte pro Zusatzfrage:")
        q_points_config = settings.get("question_points", {})
        new_q_points = {}
        for q in questions:
          q_id = q["id"]
          q_text = q["question"]
          default_val = q_points_config.get(q_id, 2)
          new_q_points[q_id] = st.number_input(
              f"Punkte für: '{q_text}'",
              min_value=0,
              max_value=20,
              value=default_val,
              key=f"pts_q_{q_id}",
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
          settings["question_points"] = new_q_points
          settings["bonus_pairing_round"] = int(b_p)
          settings["bonus_question_round"] = int(b_q)
          if new_pw:
            settings["admin_pw"] = new_pw
          save_data(SETTINGS_FILE, settings)
          st.success("Einstellungen erfolgreich aktualisiert!")
          st.rerun()

      st.divider()
      st.write("### ⚠️ Reset / Daten zurücksetzen")

      confirm_reset = st.checkbox(
          "⚠️ Ja, ich bin absolut sicher, dass ich alle Daten (Tipps,"
          " Paarungen, Fragen, Teilnehmer) auf den Standard-1. Gang"
          " zurücksetzen will."
      )

      if st.button("🔄 Alles zurücksetzen", disabled=not confirm_reset):
        for f in [TIPS_FILE, QUESTIONS_FILE, PARTICIPANTS_FILE]:
          if os.path.exists(f):
            os.remove(f)
        save_data(PAIRINGS_FILE, DEFAULT_PAIRINGS)
        save_data(QUESTIONS_FILE, DEFAULT_QUESTIONS)
        settings["gang_locked"] = {}
        save_data(SETTINGS_FILE, settings)
        st.success("Alles auf den 1. Gang zurückgesetzt!")
        st.rerun()

  elif admin_pw:
    st.error("Falsches Passwort.")
