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

def get_modifier(score):
    """Berechnet den D&D Modifikator gemäß PHB: (Wert - 10) // 2"""
    mod = (score - 10) // 2
    return f"+{mod}" if mod >= 0 else str(mod)

def load_hero():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                return Character.from_dict(json.load(f))
        except: return Character()
    return Character()

def save_hero(char):
    with open(SAVE_FILE, 'w') as f:
        json.dump(char.to_dict(), f, indent=4)
    ui.notify(f'Held {char.name} gesichert!', color='positive')

@ui.page('/')
def main_page():
    hero = load_hero()
    ui_elements = {'inputs': {}, 'mods': {}}

    def update_ui_from_hero():
        name_input.set_value(hero.name)
        class_input.set_value(hero.class_name)
        hp_input.set_value(hero.hp_current)
        ac_display.set_text(str(hero.ac))
        for stat, val in hero.stats.items():
            if stat in ui_elements['inputs']:
                ui_elements['inputs'][stat].set_value(val)
                ui_elements['mods'][stat].set_text(get_modifier(val))

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
            
            # Extraktion
            lines = [l.strip() for l in full_text.split('\n') if l.strip()]
            if lines: hero.name = lines[0]

            # Klassen & Stats Suche
            for c in ["Ranger", "Monk", "Paladin", "Fighter", "Wizard"]:
                if c.lower() in full_text.lower():
                    hero.class_name = c
                    break

            stats_map = {"Stärke": ["str"], "Geschicklichkeit": ["dex"], "Konstitution": ["con"], 
                         "Intelligenz": ["int"], "Weisheit": ["wis"], "Charisma": ["cha"]}
            
            for stat_name, aliases in stats_map.items():
                for alias in aliases:
                    match = re.search(rf'{alias}\s*(\d+)', full_text, re.IGNORECASE)
                    if match:
                        hero.stats[stat_name] = int(match.group(1))
                        break

            # HP & AC
            hp_m = re.search(r'hit point maximum\s*(\d+)', full_text.lower())
            if hp_m: hero.hp_max = int(hp_m.group(1)); hero.hp_current = hero.hp_max
            ac_m = re.search(r'armor class\s*(\d+)', full_text.lower())
            if ac_m: hero.ac = int(ac_m.group(1))

            update_ui_from_hero()
            ui.notify(f'{hero.name} geladen!', color='positive')
        except Exception as ex:
            ui.notify(f'Fehler: {ex}', color='negative')

    # --- UI ---
    ui.query('.q-page').classes('bg-slate-100')
    with ui.column().classes('w-full items-center q-pa-md max-w-2xl mx-auto'):
        ui.label('🐺 Wolperting v3.5').classes('text-h3 text-primary font-bold q-mb-lg')

        # Top Card: Name & Klasse
        with ui.card().classes('w-full q-pa-md shadow-lg border-t-8 border-primary'):
            ui.upload(on_upload=handle_upload, label='Bogen importieren').classes('w-full q-mb-md')
            name_input = ui.input('Held', value=hero.name).classes('text-h5 w-full')
            class_input = ui.input('Klasse', value=hero.class_name).classes('w-full')

        # Kampfwerte Card
        with ui.row().classes('w-full q-mt-md gap-4'):
            with ui.card().classes('col q-pa-md items-center justify-center shadow-md bg-red-50 border border-red-200'):
                ui.label('TREFFERPUNKTE').classes('text-xs font-bold text-red-600')
                hp_input = ui.number(value=hero.hp_current).classes('text-h4 w-20 text-center')
            
            with ui.card().classes('col q-pa-md items-center justify-center shadow-md bg-blue-50 border border-blue-200'):
                ui.label('RÜSTUNG').classes('text-xs font-bold text-blue-600')
                ac_display = ui.label(str(hero.ac)).classes('text-h3 font-black text-blue-900')

        # Attribute Grid (PHB Style mit Modifikatoren)
        ui.label('Attribute').classes('text-h5 q-mt-xl text-primary font-bold self-start')
        grid = ui.grid(columns=2).classes('w-full q-mt-sm gap-4')
        with grid:
            for stat in hero.stats:
                with ui.card().classes('q-pa-md shadow-md border border-gray-200 items-center overflow-hidden'):
                    ui.label(stat).classes('text-xs uppercase text-gray-400 font-bold')
                    # Der große Modifikator in der Mitte
                    mod_label = ui.label(get_modifier(hero.stats[stat])).classes('text-h4 font-bold text-gray-800')
                    ui_elements['mods'][stat] = mod_label
                    # Der kleine Score darunter zum Einstellen
                    val_input = ui.number(value=hero.stats[stat], 
                        on_change=lambda e, s=stat: [
                            hero.stats.update({s: int(e.value or 10)}),
                            ui_elements['mods'][s].set_text(get_modifier(int(e.value or 10)))
                        ]).classes('w-16 text-center')
                    ui_elements['inputs'][stat] = val_input

        ui.button('SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-xl py-4 text-xl shadow-xl')

ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)
