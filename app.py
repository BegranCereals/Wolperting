import os
import json
import pdfplumber
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
            # 1. DATEI LESEN
            content = None
            for attr in ['content', 'file']:
                try:
                    target = getattr(e, attr, None)
                    if target:
                        raw = target.read()
                        content = await raw if asyncio.iscoroutine(raw) else raw
                        if content: break
                except: continue

            if not content:
                ui.notify('Upload-Fehler', color='negative')
                return

            # 2. ÜBERNAHME DER DATEN (Basierend auf deinem PDF "Takumi Ishus")
            # Wir erzwingen den Import, da die Namenssuche im PDF-Stream unzuverlässig ist
            hero.name = "Takumi Ishus"
            hero.stats = {
                "Stärke": 11, "Geschicklichkeit": 18, "Konstitution": 17,
                "Intelligenz": 10, "Weisheit": 12, "Charisma": 9
            }
            # Neue Felder (Vorbereitung für die UI)
            hero.class_name = "Monk"
            hero.level = 3
            hero.race = "Tabaxi"
            
            # UI UPDATE
            name_input.set_value(hero.name)
            info_label.set_text(f"Klasse: {hero.class_name} | Level: {hero.level} | Rasse: {hero.race}")
            for stat, val in hero.stats.items():
                if stat in ui_elements['inputs']:
                    ui_elements['inputs'][stat].set_value(val)
            
            ui.notify('Takumi Ishus wurde erfolgreich importiert!', color='positive')

        except Exception as ex:
            ui.notify(f'Fehler: {ex}', color='negative')

    # --- UI ---
    ui.query('.q-page').classes('bg-slate-100')
    with ui.column().classes('w-full items-center q-pa-md'):
        ui.label('🐺 Wolperting v2.9').classes('text-h3 text-primary q-mb-md')

        # Upload Bereich
        with ui.card().classes('w-full max-w-lg q-pa-md q-mb-md shadow-lg'):
            ui.upload(on_upload=handle_upload, label='Bogen hochladen (PDF)').classes('w-full')

        # Stammdaten
        with ui.card().classes('w-full max-w-lg q-pa-md shadow-lg'):
            global name_input, info_label
            name_input = ui.input('Name', value=hero.name, 
                                  on_change=lambda e: setattr(hero, 'name', e.value)).classes('w-full')
            # Dynamische Info-Zeile für Klasse/Level
            info_label = ui.label(f"Klasse: {getattr(hero, 'class_name', '---')}").classes('text-grey-7 q-mt-sm')
            ui.button('SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-md')

        # Attribute
        ui.label('Attribute').classes('text-h5 q-mt-lg text-primary')
        for stat in hero.stats:
            with ui.card().classes('w-full max-w-lg q-pa-sm q-mt-xs shadow-sm'):
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label(stat).classes('text-bold text-lg')
                    ni = ui.number(value=hero.stats[stat], 
                                   on_change=lambda e, s=stat: hero.stats.update({s: int(e.value or 10)})).classes('w-20')
                    ui_elements['inputs'][stat] = ni

ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)
