import json
import os
import streamlit as st

PAIRINGS_FILE = "pairings.json"
TIPS_FILE = "tips.json"
QUESTIONS_FILE = "questions.json"
SETTINGS_FILE = "settings.json"
PARTICIPANTS_FILE = "participants.json"
SCHWINGER_FILE = "schwinger.json"

# --- OFFIZIELLE SCHWINGER-LISTE (Alphabetisch nach Nachname, Nick Alpiger auf NWSV korrigiert) ---
DEFAULT_SCHWINGER = [
    # BKSV (Bernisch-kantonaler Schwingerverband)
    {"id": 1, "name": "Aeschbacher Matthias ***", "verband": "BKSV"},
    {"id": 2, "name": "Dubach Damian *", "verband": "BKSV"},
    {"id": 3, "name": "Gasser Dominik **", "verband": "BKSV"},
    {"id": 4, "name": "Gobeli Patrick *", "verband": "BKSV"},
    {"id": 5, "name": "Kämpf Bernhard ***", "verband": "BKSV"},
    {"id": 6, "name": "Ledermann Michael **", "verband": "BKSV"},
    {"id": 7, "name": "Moser Michael ***", "verband": "BKSV"},
    {"id": 8, "name": "Rutsch Remo **", "verband": "BKSV"},
    {"id": 9, "name": "Scheuner Adrian *", "verband": "BKSV"},
    {"id": 10, "name": "Scheuner David *", "verband": "BKSV"},
    {"id": 11, "name": "Schwander Severin **", "verband": "BKSV"},
    {"id": 12, "name": "Staudenmann Fabian ***", "verband": "BKSV"},
    {"id": 13, "name": "Trittibach Silvan *", "verband": "BKSV"},
    {"id": 14, "name": "Walther Adrian ***", "verband": "BKSV"},
    {"id": 15, "name": "Zaugg Lars **", "verband": "BKSV"},
    # ISV (Innerschweizer Schwingerverband)
    {"id": 16, "name": "Ambühl Joel ***", "verband": "ISV"},
    {"id": 17, "name": "Appert Silvan *", "verband": "ISV"},
    {"id": 18, "name": "Bieri Marcel ***", "verband": "ISV"},
    {"id": 19, "name": "Bissig Luc *", "verband": "ISV"},
    {"id": 20, "name": "Bissig Lukas ***", "verband": "ISV"},
    {"id": 21, "name": "Bruhin Fredi *", "verband": "ISV"},
    {"id": 22, "name": "Bucher Christian *", "verband": "ISV"},
    {"id": 23, "name": "Doppmann Urs *", "verband": "ISV"},
    {"id": 24, "name": "Gwerder Michael ***", "verband": "ISV"},
    {"id": 25, "name": "Heinzer Lukas *", "verband": "ISV"},
    {"id": 26, "name": "Lang Sven *", "verband": "ISV"},
    {"id": 27, "name": "Lustenberger Marc ***", "verband": "ISV"},
    {"id": 28, "name": "Reichmuth Roland *", "verband": "ISV"},
    {"id": 29, "name": "Schönbächler Martin *", "verband": "ISV"},
    {"id": 30, "name": "Schwyzer Samuel **", "verband": "ISV"},
    {"id": 31, "name": "Zemp Christian *", "verband": "ISV"},
    # NOSV (Nordostschweizer Schwingerverband)
    {"id": 32, "name": "Bachmann Janos *", "verband": "NOSV"},
    {"id": 33, "name": "Biäsch Christian *", "verband": "NOSV"},
    {"id": 34, "name": "Bösch Mario **", "verband": "NOSV"},
    {"id": 35, "name": "Giger Samuel ***", "verband": "NOSV"},
    {"id": 36, "name": "Good Marco *", "verband": "NOSV"},
    {"id": 37, "name": "Kindlimann Fabian ***", "verband": "NOSV"},
    {"id": 38, "name": "Müller Josias *", "verband": "NOSV"},
    {"id": 39, "name": "Oettli Silvio **", "verband": "NOSV"},
    {"id": 40, "name": "Orlik Armon ***", "verband": "NOSV"},
    {"id": 41, "name": "Ott Damian ***", "verband": "NOSV"},
    {"id": 42, "name": "Roth Martin **", "verband": "NOSV"},
    {"id": 43, "name": "Schlegel Werner ***", "verband": "NOSV"},
    {"id": 44, "name": "Schneider Domenic ***", "verband": "NOSV"},
    {"id": 45, "name": "Schneider Mario **", "verband": "NOSV"},
    {"id": 46, "name": "Signer Andy **", "verband": "NOSV"},
    # NWSV (Nordwestschweizer Schwingerverband inkl. Nick Alpiger)
    {"id": 47, "name": "Alpiger Nick ***", "verband": "NWSV"},
    {"id": 48, "name": "Döbeli Andreas ***", "verband": "NWSV"},
    {"id": 49, "name": "Frank Marius **", "verband": "NWSV"},
    {"id": 50, "name": "Glutz Jonas *", "verband": "NWSV"},
    {"id": 51, "name": "Hermann Oliver *", "verband": "NWSV"},
    {"id": 52, "name": "Odermatt Adrian **", "verband": "NWSV"},
    {"id": 53, "name": "Scherz Valentin *", "verband": "NWSV"},
    {"id": 54, "name": "Strebel Joel ***", "verband": "NWSV"},
    {"id": 55, "name": "Voggensperger Lars **", "verband": "NWSV"},
    # SWSV (Südwestschweizer Schwingerverband)
    {"id": 56, "name": "Borcard Johann *", "verband": "SWSV"},
    {"id": 57, "name": "Collaud Romain ***", "verband": "SWSV"},
    {"id": 58, "name": "Kramer Lario ***", "verband": "SWSV"},
    {"id": 59, "name": "Tornare Laurent *", "verband": "SWSV"},
    {"id": 60, "name": "Tornare Paul *", "verband": "SWSV"},
]

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
        "schwinget_2": "Lüscher Sinisha *",
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
        "schwinget_1": "Burger Matthieu *",
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

DEFAULT_QUESTIONS = [
    {
        "id": "q1",
        "question": "Wie viele Gänge gewinnt Andy?",
        "type": "gang_count",
        "category": "Siege Andy",
        "result": None,
    },
    {
        "id": "q2",
        "question": "Schlussgangteilnehmer 1",
        "type": "schwinger_all",
        "category": "Schlussgangteilnehmer",
        "result": None,
    },
    {
        "id": "q3",
        "question": "Schlussgangteilnehmer 2",
        "type": "schwinger_all",
        "category": "Schlussgangteilnehmer",
        "result": None,
    },
    {
        "id": "q4",
        "question": (
            "Wer wird Festsieger? (bei mehreren Siegern gilt der Erstplatzierte"
            " 1a)"
        ),
        "type": "schwinger_all",
        "category": "Sieger",
        "result": None,
    },
    {
        "id": "q5",
        "question": "Bester Schwinger NOS (gemäss Rangliste fortlaufende Platzierung)",
        "type": "schwinger_verband",
        "verband": "NOSV",
        "category": "Beste Schwinger",
        "result": None,
    },
    {
        "id": "q6",
        "question": "Bester Schwinger BKSV (gemäss Rangliste fortlaufende Platzierung)",
        "type": "schwinger_verband",
        "verband": "BKSV",
        "category": "Beste Schwinger",
        "result": None,
    },
    {
        "id": "q7",
        "question": "Bester Schwinger ISV (gemäss Rangliste fortlaufende Platzierung)",
        "type": "schwinger_verband",
        "verband": "ISV",
        "category": "Beste Schwinger",
        "result": None,
    },
    {
        "id": "q8",
        "question": "Bester Schwinger NWSV (gemäss Rangliste fortlaufende Platzierung)",
        "type": "schwinger_verband",
        "verband": "NWSV",
        "category": "Beste Schwinger",
        "result": None,
    },
    {
        "id": "q9",
        "question": "Bester Schwinger SWSV (gemäss Rangliste fortlaufende Platzierung)",
        "type": "schwinger_verband",
        "verband": "SWSV",
        "category": "Beste Schwinger",
        "result": None,
    },
]

DEFAULT_PARTICIPANTS = []


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
schwinger_list = load_data(SCHWINGER_FILE, DEFAULT_SCHWINGER)
if not schwinger_list:
  schwinger_list = DEFAULT_SCHWINGER
  save_data(SCHWINGER_FILE, schwinger_list)

pairings = load_data(PAIRINGS_FILE, DEFAULT_PAIRINGS)
if not pairings:
  pairings = DEFAULT_PAIRINGS
  save_data(PAIRINGS_FILE, pairings)

questions = load_data(QUESTIONS_FILE, DEFAULT_QUESTIONS)
if not questions:
  questions = DEFAULT_QUESTIONS
  save_data(QUESTIONS_FILE, questions)

participants_list = load_data(PARTICIPANTS_FILE, DEFAULT_PARTICIPANTS)

tips = load_data(TIPS_FILE, {})
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
        "questions_locked": False,
    },
)

# Hilfslisten für Dropdowns
all_schwinger_names = sorted([s["name"] for s in schwinger_list])

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
        
        st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 1.15rem !important;
            font-weight: 700 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        sub_tab_p, sub_tab_q = st.tabs(["⚔️ Gänge / Paarungen", "📋 Zusatzfragen"])

        with sub_tab_p:
          st.write("")
          if not pairings:
            st.info("Noch keine Paarungen erfasst.")
          else:
            locked_dict = settings.get("gang_locked", {})
            # Nur Gänge anzeigen, die NICHT gesperrt sind (Gänge 1 bis 6)
            available_gangs = [g for g in range(1, 7) if not locked_dict.get(str(g), False)]

            if not available_gangs:
              st.info("Zurzeit sind keine Gänge verfügbar.")
            else:
              with st.form("tipping_form_pairings"):
                new_user_pairings = user_data.get("pairings", {})
                pts_p_val = settings.get("points_pairing", 1)

                from itertools import groupby

                sorted_pairings = sorted(pairings, key=lambda x: x["gang"])

                for gang_nr, gang_pairings in groupby(
                    sorted_pairings, key=lambda x: x["gang"]
                ):
                  gang_str = str(gang_nr)
                  if locked_dict.get(gang_str, False):
                    continue

                  with st.container(border=True):
                    st.markdown(f"### {gang_nr}. Gang")
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

                      achieved_p = 0
                      possible_p = pts_p_val if p.get("result") else 0
                      if p.get("result"):
                        if default_tip != "-" and default_tip == p["result"]:
                          achieved_p = pts_p_val

                      label = f"{s1}  ⚔️  {s2}"
                      
                      col_l, col_r = st.columns([4, 1.3])
                      with col_l:
                        st.markdown(
                            f"<p style='font-size:1.0rem;font-weight:600;margin-bottom:0px;padding-top:4px;'>{label}</p>",
                            unsafe_allow_html=True,
                        )
                      with col_r:
                        st.markdown(
                            f"<p style='font-size:0.95rem;color:#666;text-align:right;margin-bottom:0px;padding-top:8px;'>(Punkte: {achieved_p} / {possible_p})</p>",
                            unsafe_allow_html=True,
                        )

                      tip = st.selectbox(
                          label,
                          options,
                          index=default_idx,
                          key=f"tip_{p_id}",
                          label_visibility="collapsed",
                      )
                      new_user_pairings[p_id] = tip
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
            q_is_locked = settings.get("questions_locked", False)
            if q_is_locked:
              st.info("Zurzeit sind keine Zusatzfragen verfügbar.")
            else:
              with st.form("tipping_form_questions"):
                new_user_questions = user_data.get("questions", {})
                q_points_config = settings.get("question_points", {})

                schlussgang_q_ids = [q["id"] for q in questions if q.get("category") == "Schlussgangteilnehmer"]
                sg_results = [
                    str(q.get("result")).strip().lower()
                    for q in questions
                    if q.get("category") == "Schlussgangteilnehmer" and q.get("result") is not None
                ]
                sg_results_clean = [res for res in sg_results if res and res != "-"]
                schlussgang_evaluated = len(sg_results_clean) >= 2

                categories = [
                    "Siege Andy",
                    "Schlussgangteilnehmer",
                    "Sieger",
                    "Beste Schwinger",
                ]

                for cat in categories:
                  cat_questions = [
                      q
                      for q in questions
                      if q.get("category", "Beste Schwinger") == cat
                  ]
                  if cat_questions:
                    st.markdown(
                        f"<h4 style='color:#555555;margin-top:18px;margin-bottom:4px;font-weight:600;font-size:1.05rem;'>{cat}</h4>",
                        unsafe_allow_html=True,
                    )
                    st.markdown("<hr style='margin-top:0px;margin-bottom:12px;'>", unsafe_allow_html=True)

                    for q in cat_questions:
                      q_id = q["id"]
                      q_text = q["question"]
                      q_type = q.get("type", "schwinger_all")
                      q_verband = q.get("verband", None)
                      default_ans = new_user_questions.get(q_id, "")

                      if q_type == "gang_count":
                        options = ["-"] + [str(i) for i in range(1, 7)]
                      elif q_type == "schwinger_verband" and q_verband:
                        if q_verband == "NOSV":
                          options = ["-"] + sorted([
                              s["name"]
                              for s in schwinger_list
                              if s["verband"] == q_verband
                              and not s["name"].startswith("Alpiger Nick")
                          ])
                        else:
                          options = ["-"] + sorted([
                              s["name"]
                              for s in schwinger_list
                              if s["verband"] == q_verband
                          ])
                      else:
                        options = ["-"] + all_schwinger_names

                      default_idx = (
                          options.index(default_ans)
                          if default_ans in options
                          else 0
                      )

                      max_q_pts = q_points_config.get(q_id, 2)
                      achieved_q_pts = 0
                      possible_q_pts = max_q_pts if q.get("result") is not None else 0

                      if q.get("result") is not None:
                        user_ans_val = str(default_ans).strip().lower()
                        correct_ans_val = str(q.get("result")).strip().lower()

                        if cat == "Schlussgangteilnehmer" and schlussgang_evaluated:
                          if user_ans_val and user_ans_val != "-" and user_ans_val in sg_results_clean:
                            if q_id == schlussgang_q_ids[1] and len(schlussgang_q_ids) > 1:
                              other_q_id = schlussgang_q_ids[0]
                              other_user_ans = str(new_user_questions.get(other_q_id, "")).strip().lower()
                              if user_ans_val == other_user_ans:
                                achieved_q_pts = 0 if other_user_ans == user_ans_val and q_id != schlussgang_q_ids[0] else max_q_pts
                              else:
                                achieved_q_pts = max_q_pts
                            else:
                              achieved_q_pts = max_q_pts
                        else:
                          if user_ans_val and user_ans_val == correct_ans_val:
                            achieved_q_pts = max_q_pts

                      col_l, col_r = st.columns([4, 1.3])
                      with col_l:
                        st.markdown(
                            f"<p style='font-size:1.0rem;font-weight:600;margin-bottom:0px;padding-top:4px;'>{q_text}</p>",
                            unsafe_allow_html=True,
                        )
                      with col_r:
                        st.markdown(
                            f"<p style='font-size:0.95rem;color:#666;text-align:right;margin-bottom:0px;padding-top:8px;'>(Punkte: {achieved_q_pts} / {possible_q_pts})</p>",
                            unsafe_allow_html=True,
                        )

                      ans = st.selectbox(
                          q_text,
                          options,
                          index=default_idx,
                          key=f"q_sel_{q_id}",
                          label_visibility="collapsed",
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

      schlussgang_q_ids = [q["id"] for q in questions if q.get("category") == "Schlussgangteilnehmer"]

      user_stats = {}
      for name, entry_val in tips.items():
        data = (
            entry_val["data"]
            if isinstance(entry_val, dict) and "data" in entry_val
            else entry_val
        )
        user_p_tips = data.get("pairings", {})
        user_q_tips = data.get("questions", {})

        p_points_total = 0
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

        sg_results = [
            str(q.get("result")).strip().lower()
            for q in questions
            if q.get("category") == "Schlussgangteilnehmer" and q.get("result") is not None
        ]
        sg_results_clean = [res for res in sg_results if res and res != "-"]
        schlussgang_evaluated = len(sg_results_clean) >= 2

        for q in questions:
          q_id = q["id"]
          if q.get("result") is not None:
            user_ans = str(user_q_tips.get(q_id, "")).strip().lower()
            correct_ans = str(q.get("result")).strip().lower()
            
            if q.get("category") == "Schlussgangteilnehmer" and schlussgang_evaluated:
              if user_ans and user_ans != "-" and user_ans in sg_results_clean:
                if len(schlussgang_q_ids) >= 2 and q_id == schlussgang_q_ids[1]:
                  other_q_id = schlussgang_q_ids[0]
                  other_user_ans = str(user_q_tips.get(other_q_id, "")).strip().lower()
                  if user_ans == other_user_ans:
                    continue
                q_points_val += q_points_config.get(q_id, 2)
            else:
              if user_ans and user_ans == correct_ans:
                q_points_val += q_points_config.get(q_id, 2)

        user_stats[name] = {
            "gang_points_map": gang_points_map,
            "q_points": q_points_val,
            "p_points": p_points_total,
            "bonus_p": 0,
            "bonus_q": 0,
            "raw_data": data
        }

      existing_gangs = set(p["gang"] for p in pairings)
      for g in existing_gangs:
        if any(p.get("result") for p in pairings if p["gang"] == g):
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

      if any(q.get("result") is not None for q in questions) and questions:
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
            "raw_data": stats["raw_data"]
        })

      scores = sorted(scores, key=lambda x: x["Total"], reverse=True)

      current_rank = 1
      for i, entry in enumerate(scores):
        if i > 0 and entry["Total"] < scores[i - 1]["Total"]:
          current_rank = i + 1

        rank_display = (
            "🥇"
            if current_rank == 1
            else "🥈"
            if current_rank == 2
            else "🥉"
            if current_rank == 3
            else f"#{current_rank}"
        )

        with st.container(border=True):
          col1, col2 = st.columns([5.2, 1.8])
          with col1:
            st.markdown(
                f"<div style='display: flex; align-items: center; gap: 8px; margin-left: 6px;'>"
                f"<span style='font-size: 1.1rem; font-weight: bold;'>{rank_display}</span>"
                f"<span style='font-size: 1.0rem; font-weight: bold;'>{entry['Name']}</span>"
                f"</div>"
                f"<div style='font-size: 0.75rem; color: gray; margin-top: 2px; margin-left: 34px;'>"
                f"G: {entry['Gänge']}(+{entry['Bonus Gänge']}B) | F: {entry['Fragen']}(+{entry['Bonus Fragen']}B)"
                f"</div>",
                unsafe_allow_html=True,
            )
          with col2:
            st.markdown(
                f"<div style='display: flex; align-items: center; justify-content: flex-end; height: 100%; min-height: 38px;'>"
                f"<b style='font-size: 1.15rem; color: #ff4b4b;'>{entry['Total']} Pkt.</b>"
                f"</div>",
                unsafe_allow_html=True,
            )

          with st.expander(f"Tipps von {entry['Name']} anzeigen"):
            user_p_tips = entry["raw_data"].get("pairings", {})
            user_q_tips = entry["raw_data"].get("questions", {})
            
            from itertools import groupby
            sorted_pairings = sorted(pairings, key=lambda x: x["gang"])
            
            if pairings:
              st.markdown("<p style='font-size: 0.9rem; font-weight: bold; margin-bottom: 4px;'>⚔️ Paarungen & Tipps</p>", unsafe_allow_html=True)
              for gang_nr, gang_pairings in groupby(sorted_pairings, key=lambda x: x["gang"]):
                st.markdown(f"<p style='font-size: 0.9rem; font-weight: bold; margin-bottom: 2px;'>{gang_nr}. Gang</p>", unsafe_allow_html=True)
                for p in gang_pairings:
                  p_id = p["id"]
                  s1 = p["schwinget_1"]
                  s2 = p["schwinget_2"]
                  tip = user_p_tips.get(p_id, "-")
                  res = p.get("result")
                  
                  p_pts_earned = 0
                  p_pts_possible = pts_p if res else 0
                  if res and tip != "-" and tip == res:
                    p_pts_earned = pts_p
                  
                  match_str = f"{s1} vs {s2}"
                  st.markdown(f"<p style='font-size: 0.9rem; color: #333; margin: 0 0 2px 10px;'>• {match_str} ➔ <b>{tip}</b> (Pkt: {p_pts_earned}/{p_pts_possible})</p>", unsafe_allow_html=True)
                st.write("")

            if questions:
              st.markdown("<p style='font-size: 0.9rem; font-weight: bold; margin-top: 8px; margin-bottom: 4px;'>📋 Zusatzfragen & Tipps</p>", unsafe_allow_html=True)
              for q in questions:
                q_id = q["id"]
                q_text = q["question"]
                q_res = q.get("result")
                q_tip = user_q_tips.get(q_id, "-")
                if not q_tip:
                  q_tip = "-"
                
                max_q_pts = q_points_config.get(q_id, 2)
                q_pts_earned = 0
                q_pts_possible = max_q_pts if q_res is not None else 0
                
                if q_res is not None:
                  user_ans_val = str(q_tip).strip().lower()
                  correct_ans_val = str(q_res).strip().lower()
                  if user_ans_val and user_ans_val == correct_ans_val:
                    q_pts_earned = max_q_pts
                
                res_display = f" | Richtig: <b>{q_res}</b>" if q_res is not None and q_res != "" else ""
                st.markdown(f"<p style='font-size: 0.9rem; color: #333; margin: 0 0 2px 10px;'>• {q_text} ➔ Tipp: <b>{q_tip}</b>{res_display} (Pkt: {q_pts_earned}/{q_pts_possible})</p>", unsafe_allow_html=True)

elif menu == "Admin-Bereich":
  st.subheader("⚙️ Admin-Verwaltung")
  admin_pw = st.text_input("Admin-Passwort:", type="password")

  if admin_pw == settings.get("admin_pw", "schwingen2026"):
    st.success("Admin-Zugriff aktiv.")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Schwinger-Liste",
        "Paarungen & Gänge sperren",
        "Resultate Eintragen",
        "Zusatzfragen",
        "Tippspiel-Teilnehmer",
        "Wer hat gespielt?",
        "Einstellungen & Punkte",
    ])

    with tab1:
      st.write("### 🤼 Offizielle Schwinger-Liste verwalten")
      st.write(
          "Hier kannst du einzelne Schwinger hinzufügen, löschen oder die"
          " komplette Liste auf den offiziellen Standard zurücksetzen."
      )

      with st.form("add_schwinger_form"):
        st.write("#### Neuen Schwinger erfassen")
        new_s_name = st.text_input(
            "Name und Sterne (Nachname Vorname ***):"
        )
        new_s_verband = st.selectbox(
            "Teilverband:", ["BKSV", "ISV", "NOSV", "NWSV", "SWSV"]
        )
        if st.form_submit_button("Schwinger hinzufügen") and new_s_name:
          clean_name = new_s_name.strip()
          new_id = max([s["id"] for s in schwinger_list], default=0) + 1
          schwinger_list.append(
              {"id": new_id, "name": clean_name, "verband": new_s_verband}
          )
          schwinger_list = sorted(schwinger_list, key=lambda x: x["name"])
          save_data(SCHWINGER_FILE, schwinger_list)
          st.success(
              f"Schwinger '{clean_name}' ({new_s_verband}) hinzugefügt!"
          )
          st.rerun()

      st.divider()
      st.write("#### Bestehende Schwinger bearbeiten / löschen")
      if schwinger_list:
        with st.form("delete_schwinger_form"):
          schwinger_options = {
              f"{s['name']} ({s['verband']})": s["id"] for s in schwinger_list
          }
          selected_to_delete_label = st.selectbox(
              "Schwinger auswählen zum Löschen:", list(schwinger_options.keys())
          )
          if st.form_submit_button("Ausgewählten Schwinger löschen"):
            target_id = schwinger_options[selected_to_delete_label]
            schwinger_list = [s for s in schwinger_list if s["id"] != target_id]
            save_data(SCHWINGER_FILE, schwinger_list)
            st.success("Schwinger erfolgreich gelöscht.")
            st.rerun()

      st.divider()
      if st.button("🔄 Offizielle Kilchberger-Standardliste wiederherstellen"):
        save_data(SCHWINGER_FILE, DEFAULT_SCHWINGER)
        st.success("Offizielle Startliste wurde zurückgesetzt!")
        st.rerun()

    with tab2:
      st.write("### 1. Neue Paarung erfassen")
      with st.form("add_pairing"):
        gang_nr = st.number_input(
            "Gang-Nummer", min_value=1, max_value=6, value=1
        )
        s1 = st.selectbox(
            "1. Schwinger", sorted(all_schwinger_names), key="admin_s1"
        )
        s2 = st.selectbox(
            "2. Schwinger", sorted(all_schwinger_names), key="admin_s2"
        )
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
      st.write("### 2. Gänge für Tippabgabe sperren (1. bis 6. Gang)")
      locked_dict = settings.get("gang_locked", {})
      with st.form("lock_gangs_form"):
        new_locked_dict = {}
        for g in range(1, 7):
          current_state = locked_dict.get(str(g), False)
          new_locked_dict[str(g)] = st.checkbox(
              f"{g}. Gang für Tipps sperren",
              value=current_state,
              key=f"lock_g_{g}",
          )
        if st.form_submit_button("Sperr-Status speichern"):
          settings["gang_locked"] = new_locked_dict
          save_data(SETTINGS_FILE, settings)
          st.success("Gang-Sperren aktualisiert!")
          st.rerun()

    with tab3:
      st.write("### Resultate für Paarungen eintragen")
      if not pairings:
        st.info("Keine Paarungen vorhanden.")
      else:
        with st.form("result_form"):
          for p in pairings:
            p_id = p["id"]
            s1 = p["schwinget_1"]
            s2 = p["schwinget_2"]
            p_title = f"{p['gang']}. Gang: {s1}  ⚔️  {s2}"
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

    with tab4:
      st.write("### 🔒 Zusatzfragen sperren")
      q_locked_current = settings.get("questions_locked", False)
      with st.form("lock_questions_form"):
        new_q_locked = st.checkbox(
            "Zusatzfragen für die Tippabgabe sperren",
            value=q_locked_current
        )
        if st.form_submit_button("Sperr-Status speichern"):
          settings["questions_locked"] = new_q_locked
          save_data(SETTINGS_FILE, settings)
          st.success("Sperrstatus der Zusatzfragen aktualisiert!")
          st.rerun()

      st.divider()
      st.write("### Richtige Antworten für Zusatzfragen eintragen")
      if not questions:
        st.info("Noch keine Zusatzfragen erfasst.")
      else:
        with st.form("q_result_form"):
          for q in questions:
            q_id = q["id"]
            q_text = q["question"]
            q_type = q.get("type", "schwinger_all")
            q_verband = q.get("verband", None)
            current_res = q.get("result", "")

            if q_type == "gang_count":
              options = ["-"] + [str(i) for i in range(1, 7)]
            elif q_type == "schwinger_verband" and q_verband:
              if q_verband == "NOSV":
                options = ["-"] + sorted([
                    s["name"]
                    for s in schwinger_list
                    if s["verband"] == q_verband
                    and not s["name"].startswith("Alpiger Nick")
                ])
              else:
                options = ["-"] + sorted([
                    s["name"] for s in schwinger_list if s["verband"] == q_verband
                ])
            else:
              options = ["-"] + all_schwinger_names

            default_idx = (
                options.index(current_res) if current_res in options else 0
            )
            selected_res = st.selectbox(
                f"Antwort für: '{q_text}'",
                options,
                index=default_idx,
                key=f"q_res_{q_id}",
            )
            q["result"] = None if selected_res == "-" else selected_res

          if st.form_submit_button("Antworten speichern"):
            save_data(QUESTIONS_FILE, questions)
            st.success("Zusatzfragen-Resultate gespeichert!")
            st.rerun()

    with tab5:
      st.write("### 👥 Tippspiel-Teilnehmer verwalten")
      with st.form("add_single_participant"):
        new_part = st.text_input(
            "Name des Teilnehmers (z. B. Max Mustermann)"
        )
        if st.form_submit_button("Teilnehmer hinzufügen") and new_part:
          clean_np = new_part.strip()
          if clean_np and clean_np not in participants_list:
            participants_list.append(clean_np)
            save_data(PARTICIPANTS_FILE, sorted(participants_list))
            st.success(f"Teilnehmer '{clean_np}' hinzugefügt!")
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
            st.success(f"Teilnehmer '{selected_to_edit}' wurde gelöscht.")
            st.rerun()

        st.divider()
        st.write(
            f"**Aktuelle Teilnehmer ({len(participants_list)}):**"
        )
        for p_name in sorted(participants_list):
          st.write(f"- {p_name}")

    with tab6:
      st.write("### 👥 Wer hat gespielt & Vollständigkeit")
      if not tips:
        st.info("Bisher haben sich noch keine Teilnehmer registriert.")
      else:
        participant_overview = []
        total_pairings = len(pairings)
        total_questions = len(questions)

        for name, entry_val in tips.items():
          data = (
              entry_val["data"]
              if isinstance(entry_val, dict) and "data" in entry_val
              else entry_val
          )
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

          participant_overview.append({
              "Name": name,
              "Paarungs-Tipps": p_status,
              "Zusatzfragen": q_status,
          })
        st.table(participant_overview)

    with tab7:
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
        new_wp = st.text_input(
            "Admin-Passwort ändern", value=settings.get("admin_pw", "")
        )

        submit_settings = st.form_submit_button("Einstellungen speichern")
        if submit_settings:
          settings["points_pairing"] = int(p_p)
          settings["question_points"] = new_q_points
          settings["bonus_pairing_round"] = int(b_p)
          settings["bonus_question_round"] = int(b_q)
          if new_wp:
            settings["admin_pw"] = new_wp
          save_data(SETTINGS_FILE, settings)
          settings = load_data(SETTINGS_FILE, settings)
          st.success("Einstellungen erfolgreich aktualisiert!")
          st.rerun()

      st.divider()
      st.write("### ⚠️ Reset / Daten zurücksetzen")
      confirm_reset = st.checkbox(
          "⚠️ Ja, ich bin absolut sicher, dass ich alle Daten (Tipps,"
          " Paarungen, Fragen, Teilnehmer) auf den Standard zurücksetzen will."
      )
      if st.button("🔄 Alles zurücksetzen", disabled=not confirm_reset):
        for f in [
            TIPS_FILE,
            QUESTIONS_FILE,
            PARTICIPANTS_FILE,
            SCHWINGER_FILE,
        ]:
          if os.path.exists(f):
            os.remove(f)
        save_data(PAIRINGS_FILE, DEFAULT_PAIRINGS)
        save_data(QUESTIONS_FILE, DEFAULT_QUESTIONS)
        save_data(SCHWINGER_FILE, DEFAULT_SCHWINGER)
        save_data(PARTICIPANTS_FILE, DEFAULT_PARTICIPANTS)
        settings["gang_locked"] = {}
        settings["questions_locked"] = False
        save_data(SETTINGS_FILE, settings)
        st.success("Alles auf den Standard zurückgesetzt!")
        st.rerun()

  elif admin_pw:
    st.error("Falsches Passwort.")
