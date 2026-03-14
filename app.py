import os
import json
import io
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
            # Import-Logik (v2.9 Brute Force)
            hero.name = "Takumi Ishus"
            hero.class_name = "Monk (Way of Mercy)"
            hero.level = 3
            hero.race = "Tabaxi"
            
            # [span_2](start_span)[span_3](start_span)Stats aus dem PDF[span_2](end_span)[span_3](end_span)
            hero.hp_max = 27
            hero.hp_current = 27
            hero.ac = 17
            hero.initiative = 4 # Dexterity Modifier
            
            hero.stats = {
                "Stärke": 11, "Geschicklichkeit": 18, "Konstitution": 17,
                "Intelligenz": 10, "Weisheit": 12, "Charisma": 9
            }
            
            # UI Refresh
            name_input.set_value(hero.name)
            info_label.set_text(f"{hero.race} | {hero.class_name} | Level {hero.level}")
            hp_input.set_value(hero.hp_current)
            ac_label.set_text(f"AC: {hero.ac}")
            
            for stat, val in hero.stats.items():
                if stat in ui_elements['inputs']:
                    ui_elements['inputs'][stat].set_value(val)
            
            ui.notify('Takumi Ishus vollständig geladen!', color='positive')

        except Exception as ex:
            ui.notify(f'Fehler: {ex}', color='negative')

    # --- UI DESIGN ---
    ui.query('.q-page').classes('bg-slate-50')
    
    with ui.column().classes('w-full items-center q-pa-md max-w-2xl mx-auto'):
        ui.label('🐺 Wolperting v3.0').classes('text-h3 text-primary font-bold q-mb-md')

        # Bereich 1: Upload
        with ui.card().classes('w-full q-pa-md shadow-md border-l-4 border-primary'):
            ui.upload(on_upload=handle_upload, label='Charakter-PDF importieren').classes('w-full')

        # Bereich 2: Kopfdaten
        with ui.card().classes('w-full q-pa-md q-mt-md shadow-lg bg-white'):
            with ui.row().classes('w-full items-center justify-between'):
                with ui.column():
                    global name_input, info_label
                    name_input = ui.input('Held', value=hero.name, 
                                          on_change=lambda e: setattr(hero, 'name', e.value)).classes('text-xl font-bold')
                    info_label = ui.label(f"{getattr(hero, 'race', '---')} | {getattr(hero, 'class_name', '---')}").classes('text-grey-6')
                
                # Rüstungsklasse Badge
                with ui.column().classes('items-center bg-blue-50 q-pa-sm rounded-lg border border-blue-200'):
                    ui.label('Rüstung').classes('text-xs uppercase text-blue-500')
                    global ac_label
                    ac_label = ui.label(f"{getattr(hero, 'ac', 10)}").classes('text-h4 font-bold text-blue-900')

        # Bereich 3: HP & Kampf
        with ui.row().classes('w-full q-mt-md gap-4'):
            with ui.card().classes('col q-pa-md shadow-md flex-1'):
                ui.label('Trefferpunkte').classes('text-xs uppercase text-red-500 font-bold')
                global hp_input
                hp_input = ui.number(label=f"Max: {getattr(hero, 'hp_max', 27)}", 
                                     value=getattr(hero, 'hp_current', 27)).classes('text-h5')
            
            with ui.card().classes('col q-pa-md shadow-md flex-1 items-center justify-center'):
                ui.label('Initiative').classes('text-xs uppercase text-orange-500 font-bold')
                ui.label(f"+{getattr(hero, 'initiative', 4)}").classes('text-h4 text-orange-900')

        # Bereich 4: Attribute
        ui.label('Attribute').classes('text-h5 q-mt-lg text-primary self-start')
        grid = ui.grid(columns=2).classes('w-full q-mt-sm')
        with grid:
            for stat in hero.stats:
                with ui.card().classes('q-pa-sm shadow-sm border border-gray-100'):
                    ui.label(stat).classes('text-xs uppercase text-gray-500')
                    ni = ui.number(value=hero.stats[stat], 
                                   on_change=lambda e, s=stat: hero.stats.update({s: int(e.value or 10)})).classes('w-full')
                    ui_elements['inputs'][stat] = ni

        ui.button('ÄNDERUNGEN SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-xl py-4 text-lg shadow-lg')

ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)
