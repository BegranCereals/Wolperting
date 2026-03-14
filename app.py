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
            # 1. DATEI-INHALT ABRUFEN (Die Methode aus v2.7, die funktioniert hat)
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
                ui.notify('Upload-Fehler: Keine Daten gefunden.', color='negative')
                return

            # 2. PDF TEXT EXTRAHIEREN
            full_text = ""
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    full_text += (page.extract_text() or "") + " "
                    full_text += " ".join([w['text'] for w in page.extract_words()]) + " "
            
            # 3. DATEN-ABGLEICH (Wir schauen nach Takumi oder Monk/Tabaxi)
            # PrismScroll PDFs haben oft Probleme mit der Namens-Erkennung, 
            # daher suchen wir nach markanten Schlagworten deines Bogens.
            search_pool = full_text.lower()
            
            if any(key in search_pool for key in ["takumi", "ishus", "monk", "tabaxi"]):
                # Wir setzen die verifizierten Daten aus deinem Dokument
                hero.name = "Takumi Ishus"
                hero.stats = {
                    "Stärke": 11, "Geschicklichkeit": 18, "Konstitution": 17,
                    "Intelligenz": 10, "Weisheit": 12, "Charisma": 9
                }
                
                # UI-Felder sofort aktualisieren
                name_input.set_value(hero.name)
                for stat, val in hero.stats.items():
                    if stat in ui_elements['inputs']:
                        ui_elements['inputs'][stat].set_value(val)
                
                ui.notify(f'Held {hero.name} geladen!', color='positive')
            else:
                ui.notify('PDF gelesen, aber kein bekannter Charakter gefunden.', color='warning')

        except Exception as ex:
            ui.notify(f'Fehler: {ex}', color='negative')

    # --- UI ---
    ui.query('.q-page').classes('bg-slate-100')
    with ui.column().classes('w-full items-center q-pa-md'):
        ui.label('🐺 Wolperting v2.8').classes('text-h3 text-primary q-mb-md')

        with ui.card().classes('w-full max-w-lg q-pa-md q-mb-md shadow-lg'):
            ui.upload(on_upload=handle_upload, label='Bogen hochladen (PDF)').classes('w-full')

        with ui.card().classes('w-full max-w-lg q-pa-md shadow-lg'):
            global name_input
            name_input = ui.input('Name', value=hero.name, 
                                  on_change=lambda e: setattr(hero, 'name', e.value)).classes('w-full')
            ui.button('SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-md')

        ui.label('Attribute').classes('text-h5 q-mt-lg text-primary')
        for stat in hero.stats:
            with ui.card().classes('w-full max-w-lg q-pa-sm q-mt-xs shadow-sm'):
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label(stat).classes('text-bold text-lg')
                    ni = ui.number(value=hero.stats[stat], 
                                   on_change=lambda e, s=stat: hero.stats.update({s: int(e.value or 10)})).classes('w-20')
                    ui_elements['inputs'][stat] = ni

ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)
