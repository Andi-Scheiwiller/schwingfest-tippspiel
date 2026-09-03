import copy
from collections import Counter
from datetime import datetime
import json
import os
import re
import streamlit as st

PAIRINGS_FILE = "pairings.json"
TIPS_FILE = "tips.json"
QUESTIONS_FILE = "questions.json"
SETTINGS_FILE = "settings.json"
PARTICIPANTS_FILE = "participants.json"
SCHWINGER_FILE = "schwinger.json"

APP_VERSION = "v8"
APP_BUILD = "03.09.2026 13:38"

# --- OFFIZIELLE SCHWINGER-LISTE (Startliste ESV, Stand 30.08.2026) ---
DEFAULT_SCHWINGER = [
    # BKSV (Bernisch-kantonaler Schwingerverband)
    {"id": 1, "name": "Aeschbacher Matthias ***", "verband": "BKSV"},
    {"id": 2, "name": "Burger Etienne ***", "verband": "BKSV"},
    {"id": 3, "name": "Burger Matthieu ***", "verband": "BKSV"},
    {"id": 4, "name": "Gasser Dominik ***", "verband": "BKSV"},
    {"id": 5, "name": "Kämpf Bernhard ***", "verband": "BKSV"},
    {"id": 6, "name": "Ledermann Michael ***", "verband": "BKSV"},
    {"id": 7, "name": "Moser Michael ***", "verband": "BKSV"},
    {"id": 8, "name": "Nägeli Leandro **", "verband": "BKSV"},
    {"id": 9, "name": "Rutsch Remo **", "verband": "BKSV"},
    {"id": 10, "name": "Scheuner David **", "verband": "BKSV"},
    {"id": 11, "name": "Schwander Severin ***", "verband": "BKSV"},
    {"id": 12, "name": "Staudenmann Fabian ***", "verband": "BKSV"},
    {"id": 13, "name": "Trittibach Silvan **", "verband": "BKSV"},
    {"id": 14, "name": "Walther Adrian ***", "verband": "BKSV"},
    {"id": 15, "name": "Zaugg Lars **", "verband": "BKSV"},
    # ISV (Innerschweizer Schwingerverband)
    {"id": 16, "name": "Ambühl Joel ***", "verband": "ISV"},
    {"id": 17, "name": "Amrhyn Jonas **", "verband": "ISV"},
    {"id": 18, "name": "Appert Silvan ***", "verband": "ISV"},
    {"id": 19, "name": "Bieri Marcel ***", "verband": "ISV"},
    {"id": 20, "name": "Bissig Luc **", "verband": "ISV"},
    {"id": 21, "name": "Bissig Lukas ***", "verband": "ISV"},
    {"id": 22, "name": "Bruhin Fredi **", "verband": "ISV"},
    {"id": 24, "name": "Gwerder Michael ***", "verband": "ISV"},
    {"id": 25, "name": "Heinzer Lukas **", "verband": "ISV"},
    {"id": 26, "name": "Lang Sven ***", "verband": "ISV"},
    {"id": 27, "name": "Lustenberger Marc ***", "verband": "ISV"},
    {"id": 28, "name": "Reichmuth Roland **", "verband": "ISV"},
    {"id": 29, "name": "Schönbächler Martin **", "verband": "ISV"},
    {"id": 30, "name": "Schwyzer Samuel **", "verband": "ISV"},
    {"id": 31, "name": "Zemp Christian **", "verband": "ISV"},
    {"id": 61, "name": "Betschart Patrick **", "verband": "ISV"},
    # NOSV (Nordostschweizer Schwingerverband)
    {"id": 32, "name": "Bachmann Janos **", "verband": "NOSV"},
    {"id": 33, "name": "Biäsch Christian ***", "verband": "NOSV"},
    {"id": 34, "name": "Bösch Mario **", "verband": "NOSV"},
    {"id": 35, "name": "Giger Samuel ***", "verband": "NOSV"},
    {"id": 36, "name": "Good Marco ***", "verband": "NOSV"},
    {"id": 37, "name": "Habegger Andrin **", "verband": "NOSV"},
    {"id": 38, "name": "Kindlimann Fabian ***", "verband": "NOSV"},
    {"id": 39, "name": "Kolb This **", "verband": "NOSV"},
    {"id": 40, "name": "Müller Josias **", "verband": "NOSV"},
    {"id": 41, "name": "Orlik Armon ***", "verband": "NOSV"},
    {"id": 42, "name": "Ott Damian ***", "verband": "NOSV"},
    {"id": 43, "name": "Roth Martin ***", "verband": "NOSV"},
    {"id": 44, "name": "Schlegel Werner ***", "verband": "NOSV"},
    {"id": 45, "name": "Schneider Domenic ***", "verband": "NOSV"},
    {"id": 46, "name": "Schneider Mario **", "verband": "NOSV"},
    {"id": 47, "name": "Signer Andy **", "verband": "NOSV"},
    # NWSV (Nordwestschweizer Schwingerverband)
    {"id": 48, "name": "Alpiger Nick ***", "verband": "NWSV"},
    {"id": 49, "name": "Döbeli Andreas ***", "verband": "NWSV"},
    {"id": 50, "name": "Frank Marius ***", "verband": "NWSV"},
    {"id": 51, "name": "Glutz Jonas **", "verband": "NWSV"},
    {"id": 52, "name": "Lüscher Sinisha ***", "verband": "NWSV"},
    {"id": 53, "name": "Odermatt Adrian ***", "verband": "NWSV"},
    {"id": 54, "name": "Strebel Joel ***", "verband": "NWSV"},
    {"id": 55, "name": "Voggensperger Lars ***", "verband": "NWSV"},
    # SWSV (Südwestschweizer Schwingerverband)
    {"id": 56, "name": "Borcard Johann **", "verband": "SWSV"},
    {"id": 57, "name": "Collaud Romain ***", "verband": "SWSV"},
    {"id": 58, "name": "Kramer Lario ***", "verband": "SWSV"},
    {"id": 59, "name": "Tornare Laurent **", "verband": "SWSV"},
    {"id": 60, "name": "Tornare Paul **", "verband": "SWSV"},
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
    },    {
        "id": "q10",
        "question": "Wie viele Punkte erreicht der Festsieger?",
        "type": "winner_points",
        "category": "Tiebreaker",
        "result": None,
    },
]

DEFAULT_PARTICIPANTS = []

DEFAULT_SETTINGS = {
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
        "q10": 0,
    },
    "bonus_pairing_round": 2,
    "bonus_question_round": 2,
    "gang_locked": {},
    "questions_locked": False,
    # Version 3 = Tiebreaker-Frage; bestehende Spiel-/Admin-Daten bleiben erhalten.
    "data_version": 3,
}


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


def schwinger_base_name(value):
  """Entfernt nur die am Ende stehenden Kranz-Sterne für einen stabilen Namensabgleich."""
  if not isinstance(value, str):
    return value
  return re.sub(r"\s+\*{1,3}\s*$", "", value.strip())


def migrate_schwinger_references_to_official(pairings, questions, tips):
  """
  Schreibt bestehende Schwinger-Referenzen verlustfrei auf die aktuelle offizielle
  Schreibweise um. Nicht zuordenbare Werte bleiben bewusst unverändert.
  """
  official_by_base = {schwinger_base_name(s["name"]): s["name"] for s in DEFAULT_SCHWINGER}

  def official_name(value):
    if not isinstance(value, str):
      return value
    return official_by_base.get(schwinger_base_name(value), value)

  # Bestehende Paarungen und bereits eingetragene Resultate behalten.
  for pairing in pairings:
    pairing["schwinget_1"] = official_name(pairing.get("schwinget_1"))
    pairing["schwinget_2"] = official_name(pairing.get("schwinget_2"))
    if pairing.get("result") not in (None, "-", "Gestellt"):
      pairing["result"] = official_name(pairing.get("result"))

  # Bestehende Resultate der Zusatzfragen behalten.
  for question in questions:
    if question.get("type") in ("schwinger_all", "schwinger_verband"):
      if question.get("result") not in (None, "-"):
        question["result"] = official_name(question.get("result"))

  # Sämtliche bereits abgegebenen Tipps behalten und nur die Schreibweise aktualisieren.
  for entry in tips.values():
    data = entry.get("data", {}) if isinstance(entry, dict) and "data" in entry else entry
    if not isinstance(data, dict):
      continue

    user_pairings = data.get("pairings", {})
    if isinstance(user_pairings, dict):
      for pairing_id, value in list(user_pairings.items()):
        if value not in (None, "-", "Gestellt"):
          user_pairings[pairing_id] = official_name(value)

    user_questions = data.get("questions", {})
    if isinstance(user_questions, dict):
      for question_id, value in list(user_questions.items()):
        if value not in (None, "-"):
          user_questions[question_id] = official_name(value)

  return pairings, questions, tips


def get_schlussgang_points(questions, user_questions, q_points_config):
  """Punkte für Schlussgangteilnehmer unabhängig von der Tipp-Reihenfolge.

  Ein korrekt getippter Schwinger zählt genau einmal, auch wenn derselbe Name
  in beiden Tippfeldern eingetragen wurde. Ausgewertet wird erst, wenn beide
  Schlussgangteilnehmer als Resultat erfasst sind.
  """
  sg_questions = [
      q for q in questions if q.get("category") == "Schlussgangteilnehmer"
  ]
  points_by_qid = {q["id"]: 0 for q in sg_questions}

  result_names = [
      str(q.get("result")).strip().lower()
      for q in sg_questions
      if q.get("result") is not None
      and str(q.get("result")).strip() not in ("", "-")
  ]
  if len(result_names) < 2:
    return points_by_qid

  correct_names = set(result_names)
  already_counted = set()
  for q in sg_questions:
    q_id = q["id"]
    user_answer = str(user_questions.get(q_id, "")).strip().lower()
    if (
        user_answer
        and user_answer != "-"
        and user_answer in correct_names
        and user_answer not in already_counted
    ):
      points_by_qid[q_id] = q_points_config.get(q_id, 2)
      already_counted.add(user_answer)

  return points_by_qid


def autosave_user_tip(participant_name, section, item_id, widget_key, empty_as_none=False):
  """Speichert eine einzelne Tipp-Auswahl sofort, ohne andere Tipps zu verändern."""
  current_tips = load_data(TIPS_FILE, {})
  entry = current_tips.get(participant_name, {})

  if isinstance(entry, dict) and "data" in entry:
    data = entry.get("data", {"pairings": {}, "questions": {}})
  else:
    # Rückwärtskompatibilität für ältere Datenstruktur
    data = entry if isinstance(entry, dict) else {"pairings": {}, "questions": {}}
    entry = {"pin": None, "data": data}

  data.setdefault("pairings", {})
  data.setdefault("questions", {})

  value = st.session_state.get(widget_key, "-")
  if empty_as_none and value == "-":
    value = None

  data.setdefault(section, {})[item_id] = value
  entry["data"] = data
  current_tips[participant_name] = entry
  save_data(TIPS_FILE, current_tips)
  st.session_state[f"last_saved_{participant_name}"] = datetime.now().strftime("%H:%M:%S")


def is_gang_complete(gang_nr):
  gang_pairings = [p for p in pairings if p.get("gang") == gang_nr]
  return bool(gang_pairings) and all(p.get("result") is not None for p in gang_pairings)


def surname_sort_key(name):
  # Teilnehmernamen werden wie erfasst behandelt; erstes Wort als Nachname.
  return str(name).strip().casefold()


st.set_page_config(
    page_title="Tippspiel Kilchberger Schwinget",
    page_icon="🇨🇭",
    layout="centered",
)

st.title("🏆 Tippspiel Kilchberger Schwinget")

# Einheitliches, responsives Raster für Statistik und Ranglisten-Details.
st.markdown("""
<style>
/* Paarungsstatistik: jede Tippoption ist eine eigene kompakte Gruppe. */
.pair-grid {
  display:grid; grid-template-columns:minmax(0,1fr) 94px minmax(0,1fr);
  column-gap:18px; align-items:center; font-size:.82rem; line-height:1.3; margin:0 0 7px 0; color:#222;
}
.pair-choice {display:grid; grid-template-columns:minmax(0,1fr) auto; column-gap:8px; align-items:center; min-width:0;}
.pair-choice.center {grid-template-columns:auto auto; justify-content:center;}
.pair-choice .pct {white-space:nowrap; text-align:right; font-weight:700;}

/* Spieler-Tipps: Zeichen steht direkt beim zugehörigen Schwinger. */
.tip-grid {
  display:grid; grid-template-columns:20px minmax(0,1fr) minmax(0,1fr) 46px;
  column-gap:12px; align-items:center; font-size:.88rem; line-height:1.3; margin:0 0 6px 6px;
}
.tip-choice {display:grid; grid-template-columns:minmax(0,1fr) 20px; column-gap:5px; align-items:center; min-width:0;}
.tip-grid .mark,.tip-grid .sym,.tip-grid .pts {white-space:nowrap;}
.tip-grid .pts{text-align:right;}

/* Fragen: Resultat bewusst nahe bei der Nennung statt am rechten Fensterrand. */
.q-grid {display:grid; grid-template-columns:minmax(150px,300px) auto; column-gap:18px; align-items:start; width:fit-content; max-width:100%; font-size:.82rem; line-height:1.3; margin:0 0 6px 0; color:#222;}
.q-grid .count{white-space:nowrap; font-weight:700;}
.qtip-grid {display:grid; grid-template-columns:20px minmax(180px,320px) minmax(100px,220px) 48px; column-gap:12px; align-items:start; width:fit-content; max-width:100%; font-size:.88rem; line-height:1.3; margin:0 0 7px 6px;}
.qtip-grid .pts{text-align:right; white-space:nowrap;}

@media (max-width: 520px) {
  .pair-grid {grid-template-columns:minmax(0,1fr) 68px minmax(0,1fr); column-gap:7px; font-size:.70rem;}
  .pair-choice {column-gap:4px;}
  .pair-choice.center {grid-template-columns:auto auto; column-gap:3px;}
  .tip-grid {grid-template-columns:16px minmax(0,1fr) minmax(0,1fr) 38px; column-gap:5px; font-size:.74rem; margin-left:0;}
  .tip-choice {grid-template-columns:minmax(0,1fr) 16px; column-gap:2px;}
  .q-grid {grid-template-columns:minmax(120px,1fr) auto; column-gap:12px; width:100%; font-size:.76rem;}
  .qtip-grid {grid-template-columns:16px minmax(0,1fr) minmax(80px,.75fr) 40px; column-gap:5px; width:100%; font-size:.74rem; margin-left:0;}
}
</style>
""", unsafe_allow_html=True)

# Daten laden
# Wichtig: Vorhandene Dateien haben immer Vorrang. Dadurch bleiben Tipps,
# Resultate, Sperren und Einstellungen bei einem normalen Code-Update erhalten.
pairings = load_data(PAIRINGS_FILE, copy.deepcopy(DEFAULT_PAIRINGS))
if not pairings:
  pairings = copy.deepcopy(DEFAULT_PAIRINGS)
  save_data(PAIRINGS_FILE, pairings)

questions = load_data(QUESTIONS_FILE, copy.deepcopy(DEFAULT_QUESTIONS))
if not questions:
  questions = copy.deepcopy(DEFAULT_QUESTIONS)
  save_data(QUESTIONS_FILE, questions)

participants_list = load_data(PARTICIPANTS_FILE, copy.deepcopy(DEFAULT_PARTICIPANTS))
tips = load_data(TIPS_FILE, {})
settings = load_data(SETTINGS_FILE, copy.deepcopy(DEFAULT_SETTINGS))
if not isinstance(settings, dict):
  settings = copy.deepcopy(DEFAULT_SETTINGS)

# Die vorhandene Datenversion vor dem Ergänzen neuer Felder merken.
existing_data_version = settings.get("data_version", 0)

# Fehlende neue Einstellungsfelder ergänzen, bestehende Werte aber nie überschreiben.
for key, default_value in DEFAULT_SETTINGS.items():
  if key not in settings:
    settings[key] = copy.deepcopy(default_value)
# Neue Unterfelder ebenfalls nur ergänzen, nie bestehende Punktwerte überschreiben.
settings.setdefault("question_points", {})
settings["question_points"].setdefault("q10", 0)

# Neue Standardfragen verlustfrei ergänzen; vorhandene Fragen/Resultate nie überschreiben.
existing_question_ids = {q.get("id") for q in questions}
for default_q in DEFAULT_QUESTIONS:
  if default_q.get("id") not in existing_question_ids:
    questions.append(copy.deepcopy(default_q))
    existing_question_ids.add(default_q.get("id"))
    save_data(QUESTIONS_FILE, questions)

# Einmalige verlustfreie Migration auf die aktuelle Datenversion.
if existing_data_version < DEFAULT_SETTINGS["data_version"]:
  pairings, questions, tips = migrate_schwinger_references_to_official(
      pairings, questions, tips
  )
  save_data(PAIRINGS_FILE, pairings)
  save_data(QUESTIONS_FILE, questions)
  save_data(TIPS_FILE, tips)
  save_data(SCHWINGER_FILE, copy.deepcopy(DEFAULT_SCHWINGER))
  settings["data_version"] = DEFAULT_SETTINGS["data_version"]
  save_data(SETTINGS_FILE, settings)

schwinger_list = load_data(SCHWINGER_FILE, copy.deepcopy(DEFAULT_SCHWINGER))
if not schwinger_list:
  schwinger_list = copy.deepcopy(DEFAULT_SCHWINGER)
  save_data(SCHWINGER_FILE, schwinger_list)

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

        # Vollständigkeit nur für aktuell tippbare Inhalte.
        locked_now = settings.get("gang_locked", {})
        open_pairings = [p for p in pairings if not locked_now.get(str(p.get("gang")), False)]
        open_questions = [] if settings.get("questions_locked", False) else questions
        up = user_data.get("pairings", {})
        uq = user_data.get("questions", {})
        missing_p = sum(1 for p in open_pairings if up.get(p["id"]) in (None, "-", ""))
        missing_q = sum(1 for q in open_questions if uq.get(q["id"]) in (None, "-", ""))
        missing_total = missing_p + missing_q
        if missing_total == 0:
          st.success("✅ Alle aktuell verfügbaren Tipps abgegeben.")
        else:
          st.warning(f"⚠️ Noch {missing_total} aktuell verfügbare Tipps offen.")
        last_saved = st.session_state.get(f"last_saved_{clean_name}")
        if last_saved:
          st.caption(f"✓ Automatisch gespeichert · {last_saved}")

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
            from itertools import groupby
            locked_dict = settings.get("gang_locked", {})
            # Nur Gänge anzeigen, die NICHT gesperrt sind (Gänge 1 bis 6)
            available_gangs = [g for g in range(1, 7) if not locked_dict.get(str(g), False)]

            if not available_gangs:
              st.info("Zurzeit sind keine Gänge verfügbar.")
            else:
              new_user_pairings = user_data.get("pairings", {})
              pts_p_val = settings.get("points_pairing", 1)

              # Aktuellster verfügbarer Gang steht immer oben.
              sorted_pairings = sorted(pairings, key=lambda x: x["gang"], reverse=True)

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
                    widget_key = f"tip_{clean_name}_{p_id}"

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

                    st.selectbox(
                        label,
                        options,
                        index=default_idx,
                        key=widget_key,
                        label_visibility="collapsed",
                        on_change=autosave_user_tip,
                        args=(clean_name, "pairings", p_id, widget_key, False),
                    )
                    st.write("")

              st.caption("✓ Änderungen werden automatisch gespeichert.")

            # Gesperrte eigene Tipps bleiben unterhalb der offenen Gänge sichtbar.
            locked_pairings_own = [
                p for p in pairings
                if locked_dict.get(str(p.get("gang")), False)
            ]
            if locked_pairings_own:
              st.markdown("### 🔒 Gesperrte Gänge")
              st.caption("Diese Tipps sind gesperrt und können nicht mehr geändert werden.")
              sorted_locked_own = sorted(
                  locked_pairings_own, key=lambda x: x["gang"], reverse=True
              )
              for gang_nr, gang_pairings in groupby(
                  sorted_locked_own, key=lambda x: x["gang"]
              ):
                with st.container(border=True):
                  st.markdown(f"### {gang_nr}. Gang 🔒")
                  st.write("")
                  for p in gang_pairings:
                    p_id = p["id"]
                    s1 = p["schwinget_1"]
                    s2 = p["schwinget_2"]
                    saved_tip = user_data.get("pairings", {}).get(p_id, "-")
                    options = ["-", s1, "Gestellt", s2]
                    saved_idx = options.index(saved_tip) if saved_tip in options else 0
                    st.markdown(
                        f"<p style='font-size:1.0rem;font-weight:600;margin-bottom:0px;padding-top:4px;'>{s1}  ⚔️  {s2}</p>",
                        unsafe_allow_html=True,
                    )
                    st.selectbox(
                        f"locked_{clean_name}_{p_id}",
                        options,
                        index=saved_idx,
                        key=f"locked_tip_{clean_name}_{p_id}",
                        label_visibility="collapsed",
                        disabled=True,
                    )
                    st.write("")

        with sub_tab_q:
          st.write("")
          if not questions:
            st.info("Noch keine Zusatzfragen vorhanden.")
          else:
            q_is_locked = settings.get("questions_locked", False)
            if q_is_locked:
              st.info("Zurzeit sind keine Zusatzfragen verfügbar.")
            else:
              new_user_questions = user_data.get("questions", {})
              q_points_config = settings.get("question_points", {})

              schlussgang_points = get_schlussgang_points(
                  questions, new_user_questions, q_points_config
              )

              categories = [
                  "Siege Andy",
                  "Schlussgangteilnehmer",
                  "Sieger",
                  "Beste Schwinger",
                  "Tiebreaker",
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
                    elif q_type == "winner_points":
                      options = ["-"] + [f"{x / 4:.2f}" for x in range(228, 241)]
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

                      if cat == "Schlussgangteilnehmer":
                        achieved_q_pts = schlussgang_points.get(q_id, 0)
                      elif user_ans_val and user_ans_val == correct_ans_val:
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

                    widget_key = f"q_sel_{clean_name}_{q_id}"
                    st.selectbox(
                        q_text,
                        options,
                        index=default_idx,
                        key=widget_key,
                        label_visibility="collapsed",
                        on_change=autosave_user_tip,
                        args=(clean_name, "questions", q_id, widget_key, True),
                    )
                    st.write("")

              st.caption("✓ Änderungen werden automatisch gespeichert.")

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

        schlussgang_points = get_schlussgang_points(
            questions, user_q_tips, q_points_config
        )

        for q in questions:
          # Der Tiebreaker ist keine Zusatzfrage und gibt keine Fragepunkte.
          if q.get("type") == "winner_points":
            continue
          q_id = q["id"]
          if q.get("result") is not None:
            user_ans = str(user_q_tips.get(q_id, "")).strip().lower()
            correct_ans = str(q.get("result")).strip().lower()
            
            if q.get("category") == "Schlussgangteilnehmer":
              q_points_val += schlussgang_points.get(q_id, 0)
            elif user_ans and user_ans == correct_ans:
              q_points_val += q_points_config.get(q_id, 2)

        user_stats[name] = {
            "gang_points_map": gang_points_map,
            "q_points": q_points_val,
            "p_points": p_points_total,
            "bonus_p": 0,
            "bonus_q": 0,
            "gang_wins": [],
            "question_win": False,
            "raw_data": data
        }

      existing_gangs = set(p["gang"] for p in pairings)
      for g in existing_gangs:
        if is_gang_complete(g):
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
              user_stats[leader]["gang_wins"].append(g)

      # Zusatzfragen-Bonus/Ribbon erst, wenn ALLE normalen Zusatzfragen
      # ausgewertet sind. Der Tiebreaker (winner_points) zählt ausdrücklich nicht dazu.
      normal_questions = [q for q in questions if q.get("type") != "winner_points"]
      normal_questions_complete = bool(normal_questions) and all(
          q.get("result") is not None for q in normal_questions
      )
      if normal_questions_complete:
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
            user_stats[leader]["question_win"] = True

      # Tiebreaker gilt bei jeder punktgleichen Rangierung:
      # Gesamtpunkte -> kleinste Abweichung Siegerpunkte -> Name A-Z.
      winner_points_q = next((q for q in questions if q.get("type") == "winner_points"), None)
      actual_winner_points = None
      if winner_points_q and winner_points_q.get("result") not in (None, "", "-"):
        try:
          actual_winner_points = float(winner_points_q.get("result"))
        except (TypeError, ValueError):
          actual_winner_points = None

      scores = []
      for name, stats in user_stats.items():
        total = stats["p_points"] + stats["q_points"] + stats["bonus_p"] + stats["bonus_q"]
        tb_tip = stats["raw_data"].get("questions", {}).get("q10")
        try:
          tb_diff = abs(float(tb_tip) - actual_winner_points) if actual_winner_points is not None and tb_tip not in (None, "", "-") else float("inf")
        except (TypeError, ValueError):
          tb_diff = float("inf")
        scores.append({
            "Name": name, "Total": total, "Gänge": stats["p_points"],
            "Bonus Gänge": stats["bonus_p"], "Fragen": stats["q_points"],
            "Bonus Fragen": stats["bonus_q"], "GangWins": sorted(stats["gang_wins"]),
            "QuestionWin": stats["question_win"],
            "TBDiff": tb_diff, "raw_data": stats["raw_data"]
        })
      scores = sorted(scores, key=lambda x: (-x["Total"], x["TBDiff"], surname_sort_key(x["Name"])))

      # Trend: Vergleich mit dem Stand nach dem vorherigen vollständig ausgewerteten Gang.
      completed_gangs = sorted(g for g in existing_gangs if is_gang_complete(g))
      trend_map = {e["Name"]: 0 for e in scores}
      if completed_gangs:
        latest_g = completed_gangs[-1]
        previous_gangs = [g for g in completed_gangs if g < latest_g]
        if previous_gangs:
          cutoff = previous_gangs[-1]
          prev_rows = []
          for name, stats in user_stats.items():
            prev_p = sum(v for g, v in stats["gang_points_map"].items() if g <= cutoff)
            prev_bonus = 0
            for g in completed_gangs:
              if g <= cutoff and g in stats["gang_wins"]:
                prev_bonus += bonus_p_val
            prev_total = prev_p + prev_bonus + stats["q_points"] + stats["bonus_q"]
            prev_rows.append((name, prev_total))
          prev_rows.sort(key=lambda x: (-x[1], surname_sort_key(x[0])))
          prev_rank = {name: i + 1 for i, (name, _) in enumerate(prev_rows)}
          current_pos = {e["Name"]: i + 1 for i, e in enumerate(scores)}
          trend_map = {name: prev_rank.get(name, current_pos[name]) - current_pos[name] for name in current_pos}

      # Kompakte Tippstatistik, erst nach Sperrung sichtbar.
      locked_stats = settings.get("gang_locked", {})
      if any(locked_stats.get(str(g), False) for g in existing_gangs) or settings.get("questions_locked", False):
        with st.expander("📊 Tippstatistik"):
          stats_line_style = "font-size:0.82rem;color:#222;line-height:1.25;margin:0 0 4px 0;"
          stats_head_style = "font-size:0.9rem;color:#111;font-weight:700;line-height:1.2;margin:8px 0 4px 0;"
          locked_pairings = [p for p in pairings if locked_stats.get(str(p.get("gang")), False)]
          for g in sorted({p["gang"] for p in locked_pairings}, reverse=True):
            st.markdown(f"<p style='{stats_head_style}'>{g}. Gang</p>", unsafe_allow_html=True)
            for p in [x for x in locked_pairings if x["gang"] == g]:
              vals = []
              for e in tips.values():
                d = e.get("data", {}) if isinstance(e, dict) and "data" in e else e
                v = d.get("pairings", {}).get(p["id"]) if isinstance(d, dict) else None
                if v not in (None, "", "-"):
                  vals.append(v)
              c = Counter(vals); n = sum(c.values())
              if n:
                a = round(100*c.get(p["schwinget_1"],0)/n); d = round(100*c.get("Gestellt",0)/n); b = round(100*c.get(p["schwinget_2"],0)/n)
                st.markdown(
                    f"<div class='pair-grid'><span class='pair-choice'><span>{p['schwinget_1']}</span><span class='pct'>{a}%</span></span><span class='pair-choice center'><span>Gestellt</span><span class='pct'>{d}%</span></span><span class='pair-choice'><span>{p['schwinget_2']}</span><span class='pct'>{b}%</span></span></div>",
                    unsafe_allow_html=True,
                )
          if settings.get("questions_locked", False):
            st.markdown(f"<p style='{stats_head_style}'>📋 Zusatzfragen</p>", unsafe_allow_html=True)
            for q in questions:
              # Der Tiebreaker gehört bewusst nicht zur Tippstatistik.
              if q.get("type") == "winner_points":
                continue
              vals=[]
              for e in tips.values():
                d=e.get("data",{}) if isinstance(e,dict) and "data" in e else e
                v=d.get("questions",{}).get(q["id"]) if isinstance(d,dict) else None
                if v not in (None,"","-"): vals.append(str(v))
              c=Counter(vals)
              if q.get("type") == "gang_count":
                st.markdown(f"<p style='{stats_head_style}'>{q['question']}</p>", unsafe_allow_html=True)
                for x in range(1,7):
                  count=c.get(str(x),0); tipword="Tipp" if count==1 else "Tipps"; winword="Sieg" if x==1 else "Siege"
                  st.markdown(
                      f"<div class='q-grid'><span>{x} {winword}</span><span class='count'>{count} {tipword}</span></div>",
                      unsafe_allow_html=True,
                  )
              elif q.get("category") == "Schlussgangteilnehmer" and q.get("id") != "q2":
                continue
              elif q.get("category") == "Schlussgangteilnehmer":
                combined=[]
                for e in tips.values():
                  d=e.get("data",{}) if isinstance(e,dict) and "data" in e else e
                  if isinstance(d,dict):
                    for qid in ("q2","q3"):
                      v=d.get("questions",{}).get(qid)
                      if v not in (None,"","-"): combined.append(str(v))
                c=Counter(combined)
                st.markdown(f"<p style='{stats_head_style}'>Schlussgangteilnehmer</p>", unsafe_allow_html=True)
                for val,count in c.most_common(5):
                  st.markdown(
                      f"<div class='q-grid'><span>{val}</span><span class='count'>{count} {'Tipp' if count==1 else 'Tipps'}</span></div>",
                      unsafe_allow_html=True,
                  )
              else:
                st.markdown(f"<p style='{stats_head_style}'>{q['question']}</p>", unsafe_allow_html=True)
                for val,count in c.most_common(5):
                  st.markdown(
                      f"<div class='q-grid'><span>{val}</span><span class='count'>{count} {'Tipp' if count==1 else 'Tipps'}</span></div>",
                      unsafe_allow_html=True,
                  )

      current_rank = 1
      for i, entry in enumerate(scores):
        current_rank = i + 1

        rank_display = (
            "🥇"
            if current_rank == 1
            else "🥈"
            if current_rank == 2
            else "🥉"
            if current_rank == 3
            else f"{current_rank}"
        )

        with st.container(border=True):
          col1, col2 = st.columns([5.2, 1.8])
          with col1:
            st.markdown(
                f"<div style='display: flex; align-items: center; gap: 8px; margin-left: 6px;'>"
                f"<span style='font-size: 1.1rem; font-weight: bold;'>{rank_display}</span>"
                f"<span style='font-size: 1.0rem; font-weight: bold;'>{entry['Name']}</span>"
                f"<span style='font-size:0.8rem;'>{('▲' + str(trend_map.get(entry['Name']))) if trend_map.get(entry['Name'], 0) > 0 else ('▼' + str(abs(trend_map.get(entry['Name'])))) if trend_map.get(entry['Name'], 0) < 0 else '–'}</span>"
                f"</div>"
                f"<div style='font-size: 0.75rem; color: gray; margin-top: 2px; margin-left: 34px;'>"
                f"G: {entry['Gänge']}(+{entry['Bonus Gänge']}B) | F: {entry['Fragen']}(+{entry['Bonus Fragen']}B)"
                f"{' | ' + ' · '.join('🏆 G' + str(g) for g in entry['GangWins']) if entry['GangWins'] else ''}"
                f"{' · 🏆 F' if entry.get('QuestionWin') and entry['GangWins'] else (' | 🏆 F' if entry.get('QuestionWin') else '')}"
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
            locked_dict = settings.get("gang_locked", {})
            visible_pairings = [
                p for p in sorted_pairings
                if locked_dict.get(str(p["gang"]), False)
            ]
            questions_visible = settings.get("questions_locked", False)

            if visible_pairings:
              st.markdown("<p style='font-size: 0.9rem; font-weight: bold; margin-bottom: 4px;'>⚔️ Paarungen & Tipps</p>", unsafe_allow_html=True)
              for gang_nr, gang_pairings in groupby(visible_pairings, key=lambda x: x["gang"]):
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

                  if tip == "Gestellt":
                    tip_display = f"{s1} <b>−</b> · {s2} <b>−</b>"
                  elif tip == s1:
                    tip_display = f"<b>{s1} +</b> · {s2} 0"
                  elif tip == s2:
                    tip_display = f"{s1} 0 · <b>{s2} +</b>"
                  else:
                    tip_display = f"{s1} · {s2} —"
                  if res:
                    tip_correct = tip != "-" and tip == res
                    tip_color = "#176b3a" if tip_correct else "#777777"
                    tip_symbol = "✓" if tip_correct else "✗"
                    tip_weight = "700" if tip_correct else "400"
                  else:
                    tip_color = "#333333"
                    tip_symbol = ""
                    tip_weight = "400"
                  if tip == "Gestellt":
                    m1, m2 = "−", "−"
                  elif tip == s1:
                    m1, m2 = "+", "0"
                  elif tip == s2:
                    m1, m2 = "0", "+"
                  else:
                    m1, m2 = "", ""
                  st.markdown(
                      f"<div class='tip-grid' style='color:{tip_color};font-weight:{tip_weight};'><span class='sym'>{tip_symbol}</span><span class='tip-choice'><span>{s1}</span><b class='mark'>{m1}</b></span><span class='tip-choice'><span>{s2}</span><b class='mark'>{m2}</b></span><span class='pts'>{p_pts_earned}/{p_pts_possible}</span></div>",
                      unsafe_allow_html=True,
                  )
                st.write("")

            if questions_visible and questions:
              st.markdown("<p style='font-size: 0.9rem; font-weight: bold; margin-top: 8px; margin-bottom: 4px;'>📋 Zusatzfragen & Tipps</p>", unsafe_allow_html=True)
              schlussgang_points = get_schlussgang_points(
                  questions, user_q_tips, q_points_config
              )
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

                if q.get("category") == "Schlussgangteilnehmer":
                  q_pts_earned = schlussgang_points.get(q_id, 0)
                elif q_res is not None:
                  user_ans_val = str(q_tip).strip().lower()
                  correct_ans_val = str(q_res).strip().lower()
                  if user_ans_val and user_ans_val == correct_ans_val:
                    q_pts_earned = max_q_pts

                res_display = f" | Richtig: <b>{q_res}</b>" if q_res is not None and q_res != "" else ""
                if q.get("type") == "winner_points":
                  q_tip_color = "#333333"
                  q_symbol = ""
                  q_weight = "400"
                elif q_res is not None:
                  q_correct = q_pts_earned > 0
                  q_tip_color = "#176b3a" if q_correct else "#777777"
                  q_symbol = "✓" if q_correct else "✗"
                  q_weight = "700" if q_correct else "400"
                else:
                  q_tip_color = "#333333"
                  q_symbol = ""
                  q_weight = "400"
                st.markdown(
                    f"<div class='qtip-grid' style='color:{q_tip_color};font-weight:{q_weight};'><span>{q_symbol}</span><span>{q_text}</span><b>{q_tip}</b><span class='pts'>{q_pts_earned}/{q_pts_possible}</span></div>",
                    unsafe_allow_html=True,
                )

            if not visible_pairings and not questions_visible:
              st.info("Noch keine Tipps zur Anzeige freigegeben.")

elif menu == "Admin-Bereich":
  st.subheader("⚙️ Admin-Verwaltung")
  st.caption(f"Geladene Version: {APP_VERSION} · Build: {APP_BUILD}")
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
          from itertools import groupby

          sorted_result_pairings = sorted(
              pairings, key=lambda x: x["gang"], reverse=True
          )
          for gang_nr, gang_pairings in groupby(
              sorted_result_pairings, key=lambda x: x["gang"]
          ):
            with st.container(border=True):
              st.markdown(f"### {gang_nr}. Gang")
              st.write("")

              for p in gang_pairings:
                p_id = p["id"]
                s1 = p["schwinget_1"]
                s2 = p["schwinget_2"]
                p_title = f"{s1}  ⚔️  {s2}"
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
            elif q_type == "winner_points":
              options = ["-"] + [f"{x / 4:.2f}" for x in range(228, 241)]
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
            # Teilnehmer vollständig aus dem Tippspiel entfernen.
            # Die Rangliste basiert auf tips.json; deshalb muss beim Löschen
            # auch der zugehörige Tipp-Datensatz entfernt werden.
            if selected_to_edit in tips:
              del tips[selected_to_edit]
              save_data(TIPS_FILE, tips)
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
          "⚠️ Ja, ich bin absolut sicher, dass ich alle Daten und Einstellungen "
          "(Tipps, Paarungen, Resultate, Fragen, Teilnehmer, Sperren und Punkte) "
          "auf den Ausgangszustand zurücksetzen will."
      )
      if st.button("🔄 Alles zurücksetzen", disabled=not confirm_reset):
        # Bewusster Komplett-Reset: alle Spiel- und Admin-Eingaben zurück auf
        # den definierten Ausgangszustand. Erst dieser Button löscht Eingaben.
        save_data(TIPS_FILE, {})
        save_data(PAIRINGS_FILE, copy.deepcopy(DEFAULT_PAIRINGS))
        save_data(QUESTIONS_FILE, copy.deepcopy(DEFAULT_QUESTIONS))
        save_data(SCHWINGER_FILE, copy.deepcopy(DEFAULT_SCHWINGER))
        save_data(PARTICIPANTS_FILE, copy.deepcopy(DEFAULT_PARTICIPANTS))
        save_data(SETTINGS_FILE, copy.deepcopy(DEFAULT_SETTINGS))
        st.success("Alles vollständig auf den Ausgangszustand zurückgesetzt!")
        st.rerun()

  elif admin_pw:
    st.error("Falsches Passwort.")
