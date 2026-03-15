import os
import json
import pdfplumber
import io
import re
import asyncio
from nicegui import ui, events
from logic import Character

# Pfade
DATA_DIR = '/app/data'
SAVE_FILE = os.path.join(DATA_DIR, 'current_char.json')
os.makedirs(DATA_DIR, exist_ok=True)

def get_mod_value(score):
    return (score - 10) // 2

def get_mod_str(score):
    mod = get_mod_value(score)
    return f"+{mod}" if mod >= 0 else str(mod)

@ui.page('/')
def main_page():
    hero = load_hero()
    ui_elements = {'inputs': {}, 'mods': {}}

    def calculate_hp(char):
        """Berechnet HP nach deiner Regel: Halber Hitdie + 1 + Con-Mod pro Level"""
        # Wir nehmen 10 als Standard-Hitdie für Ranger/Fighter
        hit_die = 10 
        con_mod = get_mod_value(char.stats["Konstitution"])
        # Level 1: Voller Hitdie + Con
        # Ab Level 2: (Level-1) * (Halber Hitdie + 1 + Con)
        if char.level <= 1:
            return hit_die + con_mod
        else:
            return (hit_die + con_mod) + (char.level - 1) * (int(hit_die/2) + 1 + con_mod)

    async def handle_upload(e: events.UploadEventArguments):
        try:
            content = None
            for attr in ['content', 'file']:
                target = getattr(e, attr, None)
                if target:
                    raw = target.read()
                    content = await raw if asyncio.iscoroutine(raw) else raw
                    if content: break
            if not content: return

            full_text = ""
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    full_text += (page.extract_text() or "") + "\n"
                    full_text += " ".join([w['text'] for w in page.extract_words()]) + "\n"
            
            clean_text = full_text.lower()

            # 1. VERBESSERTE NAMENSUCHE (Schaut nach Dateiname oder ersten Zeilen)
            hero.name = getattr(e, 'name', 'Unbekannt').split('.')[0].replace('_', ' ')
            
            # 2. KLASSENSUCHE (Revised Ranger Fix)
            if "ranger" in clean_text: hero.class_name = "Revised Ranger"
            elif "monk" in clean_text: hero.class_name = "Monk"
            
            # 3. LEVEL ERKENNUNG
            lvl_match = re.search(r'(?:level|lvl)\s*(\d+)', clean_text)
            hero.level = int(lvl_match.group(1)) if lvl_match else 3

            # 4. ATTRIBUTE (Wie gehabt)
            stats_map = {"Stärke": ["str"], "Geschicklichkeit": ["dex"], "Konstitution": ["con"], 
                         "Intelligenz": ["int"], "Weisheit": ["wis"], "Charisma": ["cha"]}
            for stat_name, aliases in stats_map.items():
                for alias in aliases:
                    match = re.search(rf'{alias}\s*(\d+)', clean_text, re.IGNORECASE)
                    if match:
                        hero.stats[stat_name] = int(match.group(1))
                        break

            # 5. AC SUCHE (Aggressiver)
            ac_match = re.search(r'(?:ac|armor class|armor)\s*(\d+)', clean_text)
            if ac_match: hero.ac = int(ac_match.group(1))
            else: hero.ac = 10 + get_mod_value(hero.stats["Geschicklichkeit"]) # Fallback Unarmored

            # 6. HP BERECHNUNG (Nach deiner Formel)
            hero.hp_max = calculate_hp(hero)
            hero.hp_current = hero.hp_max

            update_ui()
            ui.notify(f'{hero.name} geladen & HP berechnet!', color='positive')
        except Exception as ex:
            ui.notify(f'Fehler: {ex}', color='negative')

    def update_ui():
        name_input.set_value(hero.name)
        class_input.set_value(hero.class_name)
        hp_input.set_value(hero.hp_current)
        ac_display.set_text(str(hero.ac))
        for stat, val in hero.stats.items():
            if stat in ui_elements['inputs']:
                ui_elements['inputs'][stat].set_value(val)
                ui_elements['mods'][stat].set_text(get_mod_str(val))

    # --- UI ---
    ui.query('.q-page').classes('bg-slate-100')
    with ui.column().classes('w-full items-center q-pa-md max-w-2xl mx-auto'):
        ui.label('🐺 Wolperting v3.7').classes('text-h3 text-primary font-bold q-mb-md')

        with ui.card().classes('w-full q-pa-md shadow-lg border-t-8 border-primary'):
            ui.upload(on_upload=handle_upload, label='Bogen laden').classes('w-full q-mb-sm')
            name_input = ui.input('Held', value=hero.name).classes('text-h5 w-full')
            class_input = ui.input('Klasse', value=hero.class_name).classes('w-full')

        with ui.row().classes('w-full q-mt-md gap-4 justify-center'):
            with ui.card().classes('col q-pa-md items-center shadow-md bg-red-50 border-red-200'):
                ui.label('HP (Berechnet)').classes('text-xs font-bold text-red-600')
                hp_input = ui.number(value=hero.hp_current).classes('text-h4 w-20')
            with ui.card().classes('col q-pa-md items-center shadow-md bg-blue-50 border-blue-200'):
                ui.label('AC').classes('text-xs font-bold text-blue-600')
                ac_display = ui.label(str(hero.ac)).classes('text-h4 font-bold text-blue-900')

        # Attribute
        grid = ui.grid(columns=2).classes('w-full q-mt-md gap-4')
        with grid:
            for stat in hero.stats:
                with ui.card().classes('q-pa-md shadow-md items-center'):
                    ui.label(stat).classes('text-xs uppercase text-gray-400 font-bold')
                    mod_label = ui.label(get_mod_str(hero.stats[stat])).classes('text-h4 font-bold text-gray-800')
                    ui_elements['mods'][stat] = mod_label
                    val_input = ui.number(value=hero.stats[stat], on_change=update_ui).classes('w-16 text-center')
                    ui_elements['inputs'][stat] = val_input

        ui.button('SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-xl py-4 text-xl shadow-xl')

# Hilfsfunktionen für Character Management
def load_hero():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f: return Character.from_dict(json.load(f))
        except: return Character()
    return Character()

def save_hero(char):
    with open(SAVE_FILE, 'w') as f: json.dump(char.to_dict(), f, indent=4)
    ui.notify('Gesichert!', color='positive')

ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)

