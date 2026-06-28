import streamlit as st
import json
import os
import random
from models import Character
from database import ALL_RACES, ALL_CLASSES, ALL_BACKGROUNDS

st.set_page_config(page_title="Wolperting RPG", page_icon="🧙‍♂️", layout="wide")

# Ordner für gespeicherte Charaktere anlegen
SAVE_DIR = "saved_characters"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🐺 Wolperting Hauptmenü")
page = st.sidebar.radio("Wohin möchtest du?", ["Charakter-Editor", "Gespeicherte Helden", "D&D 5e Datenbank"])

# Farb-Legende in der Sidebar anzeigen
st.sidebar.markdown("---")
st.sidebar.markdown("**Farb-Legende (Herkunft):**")
st.sidebar.markdown("<span style='color:#FF4B4B'>🔴 Rasse (Race)</span>", unsafe_allow_html=True)
st.sidebar.markdown("<span style='color:#00D4B2'>🟢 Klasse (Class)</span>", unsafe_allow_html=True)
st.sidebar.markdown("<span style='color:#0080FF'>🔵 Hintergrund (Background)</span>", unsafe_allow_html=True)

# ==========================================
# SEITE 1: CHARAKTER-EDITOR
# ==========================================
if page == "Charakter-Editor":
    st.title("🧙‍♂️ Charakter-Editor")

    # 1. Grunddaten
    char_name = st.text_input("Name des Helden:", value="Gimli")

    col1, col2, col3 = st.columns(3)
    with col1:
        race_names = [r.name for r in ALL_RACES]
        if race_names:
            selected_race = st.selectbox("Rasse:", race_names)
            chosen_race = ALL_RACES[race_names.index(selected_race)]
        else:
            st.error("Keine Rassen in der Datenbank gefunden!")
            chosen_race = None

    with col2:
        chosen_subrace = None
        if chosen_race and chosen_race.subraces:
            sub_names = [sub.name for sub in chosen_race.subraces]
            selected_sub = st.selectbox("Unterrasse:", sub_names)
            chosen_subrace = chosen_race.subraces[sub_names.index(selected_sub)]
        else:
            st.write("Keine Unterrasse verfügbar.")

    with col3:
        class_names = [c.name for c in ALL_CLASSES]
        if class_names:
            selected_class = st.selectbox("Klasse:", class_names)
            chosen_class = ALL_CLASSES[class_names.index(selected_class)]
        else:
            chosen_class = None

    selected_bg = st.selectbox("Hintergrund:", [b.name for b in ALL_BACKGROUNDS])
    chosen_bg = ALL_BACKGROUNDS[[b.name for b in ALL_BACKGROUNDS].index(selected_bg)]

    st.divider()

    # 2. ATTRIBUTS-GENERIERUNG
    st.header("🎲 Attributswerte bestimmen")
    gen_method = st.radio("Methode wählen:",
                          ["Standard Array", "Points Buy (Standard 10er Basis)", "Würfeln (4d6 drop lowest)"])

    base_stats = {"Str": 10, "Dex": 10, "Con": 10, "Int": 10, "Wis": 10, "Cha": 10}

    if gen_method == "Standard Array":
        st.write("Verteile das Standard-Array: **15, 14, 13, 12, 10, 8**")
        cols = st.columns(6)
        available_scores = [15, 14, 13, 12, 10, 8]
        for i, stat in enumerate(base_stats.keys()):
            base_stats[stat] = cols[i].selectbox(f"{stat}", available_scores, index=i)

    elif gen_method == "Points Buy (Standard 10er Basis)":
        st.write("Einfaches Punktesystem (Startwert 10, passe Werte an):")
        cols = st.columns(6)
        for i, stat in enumerate(base_stats.keys()):
            base_stats[stat] = cols[i].number_input(f"{stat}", min_value=8, max_value=18, value=10)

    elif gen_method == "Würfeln (4d6 drop lowest)":
        if st.button("🎲 Jetzt Würfel werfen!") or 'rolled_stats' not in st.session_state:
            rolled = []
            for _ in range(6):
                dice = [random.randint(1, 6) for _ in range(4)]
                dice.remove(min(dice))
                rolled.append(sum(dice))
            st.session_state.rolled_stats = rolled
        st.info(f"Deine gewürfelten Werte: {st.session_state.rolled_stats}")
        cols = st.columns(6)
        for i, stat in enumerate(base_stats.keys()):
            base_stats[stat] = cols[i].selectbox(f"{stat} zuweisen", st.session_state.rolled_stats, index=i)

    # Charakter-Logik füttern
    held = Character(name=char_name)
    held.race = chosen_race
    held.subrace = chosen_subrace
    held.rpg_class = chosen_class
    held.background = chosen_bg
    held.base_attributes = base_stats

    daten = held.get_final_stats()
    st.divider()
    st.header("🎭 Persönlichkeit & Identität")
    st.write(f"Vorschläge basierend auf deinem Hintergrund: **{chosen_bg.name}**")


    # Helferfunktion, um Dropdowns mit "Selbst schreiben"-Option zu füllen
    def build_identity_select(label, suggestions, default_text):
        options = suggestions + ["📝 Eigenen Text schreiben..."]
        selection = st.selectbox(label, options)
        if selection == "📝 Eigenen Text schreiben...":
            return st.text_area(f"Eigener Text für {label}:", value=default_text)
        return selection


    col_p1, col_p2 = st.columns(2)
    with col_p1:
        char_traits = build_identity_select("Personality Traits", chosen_bg.suggested_traits,
                                            "Ich helfe immer denen...")
        char_ideals = build_identity_select("Ideals", chosen_bg.suggested_ideals, "Gerechtigkeit...")
    with col_p2:
        char_bonds = build_identity_select("Bonds", chosen_bg.suggested_bonds, "Ich würde mein Leben geben...")
        char_flaws = build_identity_select("Flaws", chosen_bg.suggested_flaws, "Ich kann Gold nicht widerstehen...")

    # Werte in das Objekt übertragen
    held.personality_traits = char_traits
    held.ideals = char_ideals
    held.bonds = char_bonds
    held.flaws = char_flaws
    # SPEICHERN BUTTON
    if st.button("💾 Charakter permanent abspeichern"):
        file_path = os.path.join(SAVE_DIR, f"{char_name.lower().replace(' ', '_')}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(held.to_json(), f, indent=4)
        st.success(f"🎉 Held {char_name} wurde erfolgreich als JSON-Datei gespeichert!")

    st.divider()

    # --- DIGITALE ANZEIGE (CHARAKTERBLATT) ---
    st.header(f"📜 Live-Charakterblatt: {daten['name']}")
    st.metric(label="❤️ Lebenspunkte (HP)", value=daten['hp'])

    # Attribute mit farbigen Boni-Meldungen
    st.subheader("⚔️ Finale Attribute (inkl. Rassenboni)")
    attr_cols = st.columns(6)
    for i, (stat, val) in enumerate(daten["attributes"].items()):
        mod = daten["modifiers"][stat]
        sign = "+" if mod >= 0 else ""
        attr_cols[i].metric(label=stat, value=val, delta=f"{sign}{mod}")

        # Farbhilfe für Attributs-Boni
        if stat in daten["bonus_sources"]["Race"]:
            attr_cols[i].markdown(
                f"<span style='color:#FF4B4B'>+{daten['bonus_sources']['Race'][stat]} von Rasse</span>",
                unsafe_allow_html=True)

    # Features & Eigenschaften mit farbigen Markierungen
    st.subheader("✨ Eigenschaften & Features")
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Volks-Eigenschaften (Race):**")
        for t_name, t_desc in daten["traits"]["Race"].items():
            st.markdown(f"<span style='color:#FF4B4B'>**{t_name}**: {t_desc}</span>", unsafe_allow_html=True)

        st.markdown("\n**Klassen-Features (Class):**")
        for t_name, t_desc in daten["traits"]["Class"].items():
            st.markdown(f"<span style='color:#00D4B2'>**{t_name}**: {t_desc}</span>", unsafe_allow_html=True)

    with col_right:
        st.markdown("**Kompetenzen & Kompetenzquellen:**")

        # Rasse Kompetenzen
        r_prof = daten["proficiencies"]["Race"]
        if r_prof["weapons"] or r_prof["armor"]:
            st.markdown(
                f"<span style='color:#FF4B4B'>Rasse schenkt: Weapons: {r_prof['weapons']}, Armor: {r_prof['armor']}</span>",
                unsafe_allow_html=True)

        # Klasse Kompetenzen
        c_prof = daten["proficiencies"]["Class"]
        if c_prof["weapons"] or c_prof["armor"]:
            st.markdown(
                f"<span style='color:#00D4B2'>Klasse schenkt: Weapons: {c_prof['weapons']}, Armor: {c_prof['armor']}</span>",
                unsafe_allow_html=True)

        # Background Kompetenzen
        b_prof = daten["proficiencies"]["Background"]
        if b_prof["skills"]:
            st.markdown(f"<span style='color:#0080FF'>Hintergrund schenkt Skills: {b_prof['skills']}</span>",
                        unsafe_allow_html=True)


# ==========================================
# SEITE 2: GESPEICHERTE HELDEN
# ==========================================
elif page == "Gespeicherte Helden":
    st.title("📂 Geladene & Gespeicherte Charaktere")
    files = [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]

    if not files:
        st.info("Noch keine gespeicherten Charaktere gefunden. Erstelle erst einen Helden im Editor!")
    else:
        selected_file = st.selectbox("Wähle einen Charakter zum Laden:", files)

        if st.button("🔄 Charakterblatt anzeigen"):
            with open(os.path.join(SAVE_DIR, selected_file), "r", encoding="utf-8") as f:
                char_data = json.load(f)

            st.success(f"Daten für {char_data['name']} geladen!")
            st.json(char_data)  # Zeigt die rohe JSON-Struktur übersichtlich an


# ==========================================
# SEITE 3: 5E TOOLS DATENBANK-BROWSER
# ==========================================
elif page == "D&D 5e Datenbank":
    st.title("📚 D&D 5e Kompendium-Browser")
    st.write("Hier kannst du alle rohen Datenbank-Einträge durchstöbern")

    sub_page = st.tabs(["🧬 Rassen (Races)", "⚔️ Klassen (Classes)", "📜 Hintergründe (Backgrounds)"])

    with sub_page[0]:
        for r in ALL_RACES:
            with st.expander(f"Race: {r.name} (Speed: {r.speed})"):
                st.write(f"**Attributs-Boni:** {r.ability_bonuses}")
                st.write(f"**Sprachen:** {r.languages}")
                st.write(f"**Eigenschaften:** {r.traits}")
                if r.subraces:
                    st.write(f"**Verfügbare Unterrassen:** {[sub.name for sub in r.subraces]}")

    with sub_page[1]:
        for c in ALL_CLASSES:
            with st.expander(f"Class: {c.name} (Hit Die: d{c.hit_die})"):
                st.write(f"**Rettungswürfe:** {c.proficiencies['saving_throws']}")
                st.write(f"**Waffen & Rüstung:** {c.proficiencies['weapons']} | {c.proficiencies['armor']}")
                st.write(f"**Klassenfeatures:** {c.features}")

    with sub_page[2]:
        for b in ALL_BACKGROUNDS:
            with st.expander(f"Background: {b.name}"):
                st.write(f"**Feature:** {b.feature_name} - *{b.feature_description}*")
                st.write(f"**Schenkt Fertigkeiten:** {b.skill_proficiencies}")