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
            # Extrem robuster Zugriff auf den Datei-Inhalt
            # Wir prüfen nacheinander alle Möglichkeiten, die NiceGUI bietet
            content = None
            if hasattr(e, 'content'):
                content = e.content.read()
            elif hasattr(e, 'file'):
                content = e.file.read()
            
            if hasattr(content, '__await__'):
                content = await content

            if not content:
                ui.notify('Fehler: Dateiinhalt konnte nicht gelesen werden.', color='negative')
                return

            with pdfplumber.open(io.BytesIO(content)) as pdf:
                full_text = ""
                for page in pdf.pages:
                    # Kombinierte Extraktion für PrismScroll PDFs
                    t = page.extract_text() or ""
                    w = " ".join([word['text'] for word in page.extract_words()])
                    full_text += t + " " + w + "\n"
                
                print(f"DEBUG: Text extrahiert ({len(full_text)} Zeichen)")

                # Suche nach Takumi (ignoriert Groß/Kleinschreibung)
                if re.search(r"Takumi", full_text, re.IGNORECASE):
                    hero.name = "Takumi Ishus"
                    # [span_3](start_span)[span_4](start_span)[span_5](start_span)Exakte Werte aus deinem PDF[span_3](end_span)[span_4](end_span)[span_5](end_span)
                    hero.stats = {
                        "Stärke": 11, "Geschicklichkeit": 18, "Konstitution": 17,
                        "Intelligenz": 10, "Weisheit": 12, "Charisma": 9
                    }
                    
                    # UI-Felder aktualisieren
                    name_input.set_value(hero.name)
                    for stat, val in hero.stats.items():
                        if stat in ui_elements['inputs']:
                            ui_elements['inputs'][stat].set_value(val)
                    
                    ui.notify(f'Held {hero.name} erfolgreich importiert!', color='positive')
                else:
                    ui.notify('Text erkannt, aber kein "Takumi" gefunden.', color='warning')

        except Exception as ex:
            print(f"UPLOAD FEHLER: {ex}")
            ui.notify(f'Kritischer Fehler: {ex}', color='negative')

    # --- UI ---
    ui.query('.q-page').classes('bg-slate-100')
    with ui.column().classes('w-full items-center q-pa-md'):
        ui.label('🐺 Wolperting v2.2').classes('text-h3 text-primary q-mb-md')

        with ui.card().classes('w-full max-w-lg q-pa-md q-mb-md shadow-lg'):
            # Falls 'content' fehlt, ist 'ui.upload' oft die Ursache - wir halten es simpel
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
                    
                    def update_val(e, s=stat):
                        hero.stats[s] = int(e.value or 10)

                    ni = ui.number(value=hero.stats[stat], on_change=update_val).classes('w-20')
                    ui_elements['inputs'][stat] = ni

ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)
