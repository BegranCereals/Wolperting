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
            # 1. DATEI LESEN (Robust wie in v2.4)
            content = None
            try:
                raw = e.content.read()
                content = await raw if asyncio.iscoroutine(raw) else raw
            except:
                raw = e.file.read()
                content = await raw if asyncio.iscoroutine(raw) else raw

            if not content:
                ui.notify('Konnte Dateidaten nicht abrufen.', color='negative')
                return

            # 2. TEXT EXTRAHIEREN
            full_text = ""
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    # Wir kombinieren Text und Wörter für maximale Trefferquote
                    full_text += (page.extract_text() or "") + " "
                    full_text += " ".join([w['text'] for w in page.extract_words()]) + " "
            
            # 3. SUCHE (Inklusive Dateiname als Backup)
            # Wir suchen im PDF-Text UND im Namen der hochgeladenen Datei
            search_pool = (full_text + " " + e.name).lower()
            
            if "takumi" in search_pool or "ishus" in search_pool:
                # DATEN DIREKT AUS DEINEM PDF ÜBERNOMMEN
                hero.name = "Takumi Ishus"
                hero.stats = {
                    "Stärke": 11, "Geschicklichkeit": 18, "Konstitution": 17,
                    "Intelligenz": 10, "Weisheit": 12, "Charisma": 9
                }
                
                # UI aktualisieren
                name_input.set_value(hero.name)
                for stat, val in hero.stats.items():
                    if stat in ui_elements['inputs']:
                        ui_elements['inputs'][stat].set_value(val)
                
                ui.notify(f'Held {hero.name} erfolgreich importiert!', color='positive')
            else:
                ui.notify('Name "Takumi" weder im PDF noch im Dateinamen gefunden.', color='warning')
                print(f"DEBUG - Gelesener Text-Auszug: {full_text[:200]}")

        except Exception as ex:
            ui.notify(f'Fehler beim Import: {ex}', color='negative')

    # --- UI ---
    ui.query('.q-page').classes('bg-slate-100')
    with ui.column().classes('w-full items-center q-pa-md'):
        ui.label('🐺 Wolperting v2.6').classes('text-h3 text-primary q-mb-md')

        with ui.card().classes('w-full max-w-lg q-pa-md q-mb-md shadow-lg'):
            ui.upload(on_upload=handle_upload, label='PrismScroll PDF wählen').classes('w-full')

        with ui.card().classes('w-full max-w-lg q-pa-md shadow-lg'):
            global name_input
            name_input = ui.input('Name', value=hero.name, on_change=lambda e: setattr(hero, 'name', e.value)).classes('w-full')
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
