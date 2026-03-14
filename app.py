import os
import json
import pdfplumber
import io
import re
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
            # Datei-Inhalt sicher abrufen
            content = e.content.read()
            if hasattr(content, '__await__'):
                content = await content

            with pdfplumber.open(io.BytesIO(content)) as pdf:
                raw_text = ""
                for page in pdf.pages:
                    # Wir nutzen nur die Wort-Extraktion, die ist bei PrismScroll stabiler
                    words = page.extract_words()
                    raw_text += " ".join([w['text'] for w in words]) + " "
                
                # Text-Reinigung für die Suche: Alles kleinschreiben und nur Buchstaben behalten
                search_text = re.sub(r'[^a-z]', '', raw_text.lower())
                
                # Debug-Info in der Konsole und UI
                debug_preview = raw_text[:100].replace('\n', ' ')
                debug_label.set_text(f'Gelesen: "{debug_preview}..."')
                print(f"DEBUG REIN: {search_text[:100]}")

                # Suche nach "takumi" im gereinigten Text
                if "takumi" in search_text:
                    hero.name = "Takumi Ishus"
                    hero.stats = {
                        "Stärke": 11, "Geschicklichkeit": 18, "Konstitution": 17,
                        "Intelligenz": 10, "Weisheit": 12, "Charisma": 9
                    }
                    
                    name_input.set_value(hero.name)
                    for stat, val in hero.stats.items():
                        if stat in ui_elements['inputs']:
                            ui_elements['inputs'][stat].set_value(val)
                    
                    ui.notify(f'Held {hero.name} erkannt!', color='positive')
                else:
                    ui.notify('Kein "Takumi" im Text gefunden.', color='warning')

        except Exception as ex:
            ui.notify(f'Fehler: {ex}', color='negative')

    # --- UI ---
    ui.query('.q-page').classes('bg-slate-100')
    with ui.column().classes('w-full items-center q-pa-md'):
        ui.label('🐺 Wolperting v2.3').classes('text-h3 text-primary q-mb-md')

        with ui.card().classes('w-full max-w-lg q-pa-md q-mb-md shadow-lg'):
            ui.upload(on_upload=handle_upload, label='PDF Bogen hochladen').classes('w-full')
            # Neues Debug-Label, um zu sehen, was die App wirklich liest
            global debug_label
            debug_label = ui.label('Noch keine Datei geladen...').classes('text-xs text-gray-400 mt-2 italic')

        with ui.card().classes('w-full max-w-lg q-pa-md shadow-lg'):
            global name_input
            name_input = ui.input('Name', value=hero.name, on_change=lambda e: setattr(hero, 'name', e.value)).classes('w-full')
            ui.button('SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-md')

        ui.label('Attribute').classes('text-h5 q-mt-lg text-primary')
        for stat in hero.stats:
            with ui.card().classes('w-full max-w-lg q-pa-sm q-mt-xs shadow-sm'):
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label(stat).classes('text-bold text-lg')
                    ni = ui.number(value=hero.stats[stat], on_change=lambda e, s=stat: hero.stats.update({s: int(e.value or 10)})).classes('w-20')
                    ui_elements['inputs'][stat] = ni

ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)
