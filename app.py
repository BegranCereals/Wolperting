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
    ui_elements = {'inputs': {}}

    async def handle_upload(e: events.UploadEventArguments):
        try:
            content = None
            for attr in ['content', 'file']:
                target = getattr(e, attr, None)
                if target:
                    raw = target.read()
                    content = await raw if asyncio.iscoroutine(raw) else raw
                    if content: break

            if not content:
                ui.notify('Fehler beim Lesen der Dateidaten.', color='negative')
                return

            full_text = ""
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    full_text += (page.extract_text() or "") + "\n"
                    full_text += " ".join([w['text'] for w in page.extract_words()]) + "\n"
            
            # DATEN-EXTRAKTION
            lines = [l.strip() for l in full_text.split('\n') if l.strip()]
            if lines:
                hero.name = lines[0]

            # Stats-Suche
            stats_map = {
                "Stärke": ["strength", "str"],
                "Geschicklichkeit": ["dexterity", "dex"],
                "Konstitution": ["constitution", "con"],
                "Intelligenz": ["intelligence", "int"],
                "Weisheit": ["wisdom", "wis"],
                "Charisma": ["charisma", "cha"]
            }

            for stat_name, aliases in stats_map.items():
                for alias in aliases:
                    pattern = re.compile(rf'{alias}\s*(\d+)', re.IGNORECASE)
                    match = pattern.search(full_text)
                    if match:
                        hero.stats[stat_name] = int(match.group(1))
                        break

            # HP & AC (mit Fallback auf Standardwerte)
            hp_match = re.search(r'hit point maximum\s*(\d+)', full_text.lower())
            hero.hp_max = int(hp_match.group(1)) if hp_match else 10
            hero.hp_current = hero.hp_max
            
            ac_match = re.search(r'armor class\s*(\d+)', full_text.lower())
            hero.ac = int(ac_match.group(1)) if ac_match else 10

            # UI AKTUALISIEREN
            name_input.set_value(hero.name)
            hp_input.set_value(hero.hp_current)
            ac_display.set_text(str(hero.ac))
            for stat, val in hero.stats.items():
                if stat in ui_elements['inputs']:
                    ui_elements['inputs'][stat].set_value(val)
            
            ui.notify(f'Daten für {hero.name} geladen!', color='positive')

        except Exception as ex:
            ui.notify(f'Import-Fehler: {ex}', color='negative')

    # --- UI ---
    ui.query('.q-page').classes('bg-slate-50')
    with ui.column().classes('w-full items-center q-pa-md max-w-2xl mx-auto'):
        ui.label('🐺 Wolperting v3.3').classes('text-h3 text-primary font-bold')

        with ui.card().classes('w-full q-pa-md shadow-md border-l-4 border-primary q-mb-md'):
            ui.upload(on_upload=handle_upload, label='Bogen importieren').classes('w-full')

        with ui.card().classes('w-full q-pa-md shadow-lg'):
            global name_input
            name_input = ui.input('Name', value=hero.name).classes('text-xl font-bold w-full')
            
            with ui.row().classes('w-full justify-around q-mt-md'):
                global hp_input
                hp_input = ui.number(label="HP", value=hero.hp_current).classes('w-32')
                with ui.column().classes('items-center'):
                    ui.label('AC').classes('text-xs uppercase')
                    global ac_display
                    ac_display = ui.label(str(hero.ac)).classes('text-h4 font-bold')

        ui.label('Attribute').classes('text-h5 q-mt-lg text-primary self-start')
        grid = ui.grid(columns=2).classes('w-full q-mt-sm')
        with grid:
            for stat in hero.stats:
                with ui.card().classes('q-pa-sm shadow-sm'):
                    ui.label(stat).classes('text-xs uppercase text-gray-500')
                    ni = ui.number(value=hero.stats[stat], 
                                   on_change=lambda e, s=stat: hero.stats.update({s: int(e.value or 10)})).classes('w-full')
                    ui_elements['inputs'][stat] = ni

        ui.button('SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-md py-4 text-lg')

ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)
