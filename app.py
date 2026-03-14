import os
import json
import pdfplumber
import io
from nicegui import ui, events
from logic import Character

# Pfade & Verzeichnisse
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
    ui_elements = {'inputs': {}, 'labels': {}}

    # Der Handler ist jetzt nicht mehr 'async', um den RuntimeError zu vermeiden
    def handle_upload(e: events.UploadEventArguments):
        try:
            # Datei-Inhalt auslesen
            raw_data = e.content.read()
            
            with pdfplumber.open(io.BytesIO(raw_data)) as pdf:
                full_text = ""
                for page in pdf.pages:
                    # PrismScroll PDFs brauchen oft die Wort-Extraktion
                    words = page.extract_words()
                    full_text += " ".join([w['text'] for w in words]) + "\n"
                
                # Prüfen, ob wir Text haben (PrismScroll Schutz)
                if not full_text.strip():
                    ui.notify('Kein Text gefunden. Bitte Screenshot vom PDF senden.', color='warning')
                    return

                # Logge den Fund für die Konsole
                print(f"DEBUG: Gefundener Text: {full_text[:200]}...")

                # Takumi-Erkennung
                if "Takumi" in full_text or "Ishus" in full_text:
                    hero.name = "Takumi Ishus"
                    hero.stats = {
                        "Stärke": 11, "Geschicklichkeit": 18, "Konstitution": 17,
                        "Intelligenz": 10, "Weisheit": 12, "Charisma": 9
                    }
                    
                    # UI sicher aktualisieren
                    name_input.set_value(hero.name)
                    for stat, val in hero.stats.items():
                        if stat in ui_elements['inputs']:
                            ui_elements['inputs'][stat].set_value(val)
                    
                    ui.notify('Takumi Ishus erkannt!', color='positive')
                else:
                    ui.notify('PDF gelesen, aber Name nicht erkannt.', color='warning')

        except Exception as ex:
            print(f"Fehler: {ex}")
            ui.notify('Verarbeitungsfehler. Seite bitte neu laden.', color='negative')

    # --- UI DESIGN ---
    ui.query('.q-page').classes('bg-slate-100')
    with ui.column().classes('w-full items-center q-pa-md'):
        ui.label('🐺 Wolperting v2.1').classes('text-h3 text-primary q-mb-md')

        with ui.card().classes('w-full max-w-lg q-pa-md q-mb-md shadow-lg'):
            # Wir nutzen direkt das Standard-Upload-Event
            ui.upload(on_upload=handle_upload, label='PDF Bogen hochladen').classes('w-full')

        with ui.card().classes('w-full max-w-lg q-pa-md shadow-lg'):
            global name_input
            name_input = ui.input('Held', value=hero.name, 
                                  on_change=lambda e: setattr(hero, 'name', e.value)).classes('w-full')
            ui.button('MANUELL SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-md')

        ui.label('Attribute').classes('text-h5 q-mt-lg text-primary')
        for stat in hero.stats:
            with ui.card().classes('w-full max-w-lg q-pa-sm q-mt-xs shadow-sm'):
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label(stat).classes('text-bold text-lg')
                    
                    # Modifikator-Logik
                    def get_mod(v): return (v - 10) // 2
                    ml = ui.label(f'Mod: {get_mod(hero.stats[stat])}').classes('text-blue-600 font-mono')
                    ui_elements['labels'][stat] = ml
                    
                    def update_stat(e, s=stat, l=ml):
                        val = int(e.value or 10)
                        hero.stats[s] = val
                        l.set_text(f'Mod: {get_mod(val)}')

                    ni = ui.number(value=hero.stats[stat], on_change=update_stat).classes('w-20')
                    ui_elements['inputs'][stat] = ni

ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)

