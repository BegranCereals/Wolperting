import streamlit as st
import math
from database import ALL_RACES, ALL_CLASSES, ALL_BACKGROUNDS
from models import Character  # Stelle sicher, dass Character importiert ist

# Page Configuration für ein breiteres DnD-Sheet
st.set_page_config(page_title="DnD Character Sheet", layout="wide")

# --- INITIAL SESSION STATES ---
if "char" not in st.session_state:
    # Standard-Dummy-Charakter, falls noch keiner erstellt wurde
    st.session_state.char = Character(name="Held ohne Namen")

if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1

# CSS für die Rahmen-Optik (Kacheln wie in image.png)
st.markdown("""
    <style>
    .dnd-box {
        border: 2px solid #2e2e2e;
        padding: 15px;
        border-radius: 5px;
        text-align: center;
        background-color: #fcfaf2;
        color: #1e1e1e;
        margin-bottom: 10px;
    }
    .dnd-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        color: #666;
        margin-top: 5px;
    }
    .dnd-value {
        font-size: 1.8rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


# --- POPUP DIALOG (CHARAKTER CREATOR WIZARD) ---
@st.dialog("Charakter Erstellen", width="large")
def character_creator_wizard():
    step = st.session_state.wizard_step

    # Progress Bar oben im Popup
    st.progress(step / 4, text=f"Schritt {step} von 4")

    if step == 1:
        st.subheader("Schritt 1: Basis & Rasse")
        char_name = st.text_input("Charakter Name", value=st.session_state.char.name)

        race_names = [r.name for r in ALL_RACES]
        chosen_race_name = st.selectbox("Rasse wählen", race_names)

        # Unterrassen-Logik falls vorhanden
        selected_race = next(r for r in ALL_RACES if r.name == chosen_race_name)
        chosen_subrace = None
        if selected_race.subraces:
            subrace_names = [sub.name for sub in selected_race.subraces]
            chosen_subrace_name = st.selectbox("Unterrassen-Spezialisierung", subrace_names)
            chosen_subrace = next(sub for sub in selected_race.subraces if sub.name == chosen_subrace_name)

        if st.button("Weiter zu Klasse ➡️"):
            st.session_state.char.name = char_name
            st.session_state.char.race = selected_race
            st.session_state.char.subrace = chosen_subrace
            st.session_state.wizard_step = 2
            st.rerun()

    elif step == 2:
        st.subheader("Schritt 2: Klasse wählen")
        class_names = [c.name for c in ALL_CLASSES]
        chosen_class_name = st.selectbox("Klasse wählen", class_names)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Zurück"):
                st.session_state.wizard_step = 1
                st.rerun()
        with col2:
            if st.button("Weiter zu Background ➡️"):
                selected_class = next(c for c in ALL_CLASSES if c.name == chosen_class_name)
                st.session_state.char.rpg_class = selected_class
                st.session_state.wizard_step = 3
                st.rerun()

    elif step == 3:
        st.subheader("Schritt 3: Hintergrund & Gesinnung")
        bg_names = [b.name for b in ALL_BACKGROUNDS]
        chosen_bg_name = st.selectbox("Hintergrund", bg_names)

        alignment = st.selectbox("Gesinnung (Alignment)", [
            "Lawful Good", "Neutral Good", "Chaotic Good",
            "Lawful Neutral", "True Neutral", "Chaotic Neutral",
            "Lawful Evil", "Neutral Evil", "Chaotic Evil"
        ])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Zurück"):
                st.session_state.wizard_step = 2
                st.rerun()
        with col2:
            if st.button("Weiter zu Attributen ➡️"):
                selected_bg = next(b for b in ALL_BACKGROUNDS if b.name == chosen_bg_name)
                st.session_state.char.background = selected_bg
                # Hier könntest du das Alignment im Modell speichern, falls das Attribut existiert:
                # st.session_state.char.alignment = alignment
                st.session_state.wizard_step = 4
                st.rerun()

    elif step == 4:
        st.subheader("Schritt 4: Attribute würfeln/verteilen")
        st.write("Verteile deine Basis-Werte (Standard-Werte vorausgewählt):")

        stats = ["Str", "Con", "Dex", "Int", "Wis", "Cha"]
        new_base = {}
        for s in stats:
            new_base[s] = st.number_input(f"Basis {s}", min_value=3, max_value=20, value=10)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Zurück"):
                st.session_state.wizard_step = 3
                st.rerun()
        with col2:
            if st.button("Character Sheet generieren! 🎲"):
                st.session_state.char.base_attributes = new_base
                st.session_state.wizard_step = 1  # Reset für das nächste Mal
                st.success("Charakter erfolgreich geladen!")
                st.rerun()


# --- HAUPT-UI (DAS CHARAKTERBLATT AUS image.png) ---

st.title("🧙‍♂️ D&D 5e Character Sheet Hub")

# Button um den Creator als Popup zu öffnen
if st.button("➕ Neuen Charakter erstellen (Popup)"):
    character_creator_wizard()

st.write("---")

# Daten aus dem Charaktermodell ziehen
char_data = st.session_state.char.get_final_stats()
char_obj = st.session_state.char

## --- REIHE 1: BILD & KLASSE/RASSE/BACKGROUND ---
row1_col1, row1_col2 = st.columns([1, 3])

with row1_col1:
    # Quadrat für das Bild
    st.markdown(f"""
        <div class="dnd-box" style="height: 140px; display: flex; align-items: center; justify-content: center;">
            <div>
                <span style="font-size: 2.5rem;">👤</span><br>
                <div class="dnd-title">{char_data['name']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with row1_col2:
    # Text-Details Block daneben
    klasse_name = char_obj.rpg_class.name if char_obj.rpg_class else "Keine Klasse"
    rasse_name = char_obj.race.name if char_obj.race else "Keine Rasse"
    bg_name = char_obj.background.name if char_obj.background else "Kein Hintergrund"
    alignment_val = getattr(char_obj, 'alignment', 'Neutral')

    st.markdown(f"""
        <div class="dnd-box" style="height: 140px; text-align: left;">
            <h3 style="margin: 0; color: #cc1111;">{klasse_name} | {rasse_name}</h3>
            <p style="margin: 5px 0 0 0; font-size: 1.1rem;">
                <b>Hintergrund:</b> {bg_name} | <b>Gesinnung:</b> {alignment_val}<br>
                <b>Stufe:</b> {char_data['level']}
            </p>
        </div>
    """, unsafe_allow_html=True)

## --- REIHE 2: AC, MVMSPD, HP ---
st.write("")
row2_col1, row2_col2, row2_col3 = st.columns(3)

# Wir errechnen AC (10 + Dex Modifikator als vereinfachtes Standard)
dex_mod = char_data["modifiers"].get("Dex", 0)
ac_val = 10 + dex_mod
speed_val = char_obj.race.speed if char_obj.race else 30

with row2_col1:
    st.markdown(
        f'<div class="dnd-box"><div class="dnd-value">{ac_val}</div><div class="dnd-title">Armor Class (AC)</div></div>',
        unsafe_allow_html=True)
with row2_col2:
    st.markdown(
        f'<div class="dnd-box"><div class="dnd-value">{speed_val} ft.</div><div class="dnd-title">Movement Speed (Mvmspd)</div></div>',
        unsafe_allow_html=True)
with row2_col3:
    st.markdown(
        f'<div class="dnd-box"><div class="dnd-value" style="color: #cc1111;">{char_data["hp"]}</div><div class="dnd-title">Hit Points (HP)</div></div>',
        unsafe_allow_html=True)

## --- REIHE 3: DIE ATTRIBUTE (MODIFIKATOREN GROSS) ---
st.write("")
# 5 Spalten laut Skizze (Str, Con, Dex, Int, Wis - Cha packen wir als 6. dazu oder lassen es fließen)
attr_cols = st.columns(6)
stats_ordered = ["Str", "Con", "Dex", "Int", "Wis", "Cha"]

for i, stat in enumerate(stats_ordered):
    with attr_cols[i]:
        mod = char_data["modifiers"].get(stat, 0)
        sign = "+" if mod >= 0 else ""
        score = char_data["attributes"].get(stat, 10)

        # Modifikator groß oben, Score klein drunter laut Skizze
        st.markdown(f"""
            <div class="dnd-box">
                <div class="dnd-value">{sign}{mod}</div>
                <div style="font-size: 1.1rem; font-weight: bold;">{stat}</div>
                <div style="font-size: 0.8rem; color: #555;">Score: {score}</div>
            </div>
        """, unsafe_allow_html=True)

# Inspiration & Prof Bonus direkt unter den Attributen zentriert
row3_sub1, row3_sub2 = st.columns(2)
with row3_sub1:
    st.markdown('<div class="dnd-box" style="padding: 5px;"><div class="dnd-title">💡 Inspiration: 1</div></div>',
                unsafe_allow_html=True)
with row3_sub2:
    prof_bonus = 2 + math.floor((char_data["level"] - 1) / 4)
    st.markdown(
        f'<div class="dnd-box" style="padding: 5px;"><div class="dnd-title">⚔️ Prof. Bonus: +{prof_bonus}</div></div>',
        unsafe_allow_html=True)

## --- REIHE 4: TRAITS, PROFICIENCIES, LANGUAGES ---
st.write("")
st.subheader("Traits / Proficiencies / Languages / Etc.")
with st.container(border=True):
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.write("**Rassen-Eigenschaften & Features:**")
        race_traits = char_data["traits"].get("Race", {})
        if race_traits:
            for t_name, t_desc in race_traits.items():
                st.write(f"• **{t_name}:** {t_desc}")
        else:
            st.write("_Keine speziellen Merkmale_")

    with col_t2:
        st.write("**Sprachen:**")
        bg_langs = char_data["languages"].get("Background", [])
        race_langs = char_data["languages"].get("Race", [])
        all_langs = list(set(race_langs + bg_langs))
        if all_langs:
            st.write(", ".join(all_langs))
        else:
            st.write("Common")

## --- REIHE 5: EQUIPMENT, SPELLS, SKILLS ---
st.write("")
row5_col1, row5_col2, row5_col3 = st.columns(3)

with row5_col1:
    st.markdown(
        '<div style="background-color: #2e2e2e; color: white; padding: 5px; text-align:center; font-weight:bold;">Equipment</div>',
        unsafe_allow_html=True)
    with st.container(border=True):
        st.write("• Startausrüstung aus Background")
        st.write("• 15 Goldmünzen (gp)")
        st.write("• Gewöhnliche Kleidung")

with row5_col2:
    st.markdown(
        '<div style="background-color: #2e2e2e; color: white; padding: 5px; text-align:center; font-weight:bold;">Spells & Slots</div>',
        unsafe_allow_html=True)
    with st.container(border=True):
        st.write("**Slots:** Lvl 1: [ ] [ ]")
        st.write("---")
        st.write("_Keine Zauber vorbereitet oder vergeben_")

with row5_col3:
    st.markdown(
        '<div style="background-color: #2e2e2e; color: white; padding: 5px; text-align:center; font-weight:bold;">Skills</div>',
        unsafe_allow_html=True)
    with st.container(border=True):
        # Hier listen wir die gelernten Skills aus dem Background auf
        bg_skills = char_data["proficiencies"]["Background"].get("skills", [])
        if bg_skills:
            for skill in bg_skills:
                st.write(f"☑️ {skill}")
        else:
            st.write("_Keine gelernten Skills gewählt_")