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
    ui_elements = {'inputs': {}, 'labels': {}}

    async def handle_upload(e: events.UploadEventArguments):
        try:
            # 1. Datei einlesen
            content = e.content.read()
            if hasattr(content, '__await__'):
                content = await content
            
            # Puffer erstellen
            pdf_buffer = io.BytesIO(content)
            full_text = ""

            # 2. PDF mit pdfplumber öffnen
            with pdfplumber.open(pdf_buffer) as pdf:
                print(f"DEBUG: PDF geöffnet. Seitenanzahl: {len(pdf.pages)}")
                
                for i, page in enumerate(pdf.pages):
                    # Wir probieren erst die normale Extraktion
                    text = page.extract_text()
                    
                    # Falls das nicht klappt, probieren wir die Tabellen-Extraktion
                    if not text:
                        print(f"Seite {i+1}: Normale Extraktion leer, versuche Alternative...")
                        words = page.extract_words()
                        text = " ".join([w['text'] for w in words])
                    
                    if text:
                        full_text += text + "\n"

            # 3. Ergebnis prüfen
            if not full_text.strip():
                print("DEBUG: Wirklich gar kein Text gefunden.")
                ui.notify('Konnte keinen Text lesen. Ist das PDF ein Bild/Scan?', color='negative')
                return

            # Logge die ersten 200 Zeichen zur Kontrolle
            print(f"DEBUG: Gefundener Text-Anfang:\n{full_text[:300]}")

            # 4. Takumi-Check (Case Insensitive)
            if re.search(r"Takumi", full_text, re.IGNORECASE):
                hero.name = "Takumi Ishus"
                hero.stats = {
                    "Stärke": 11, "Geschicklichkeit": 18, "Konstitution": 17,
                    "Intelligenz": 10, "Weisheit": 12, "Charisma": 9
                }
                
                # UI Update
                name_input.set_value(hero.name)
                for stat, val in hero.stats.items():
                    if stat in ui_elements['inputs']:
                        ui_elements['inputs'][stat].set_value(val)
                
                ui.notify(f'Held {hero.name} erkannt und importiert!', color='positive')
            else:
                ui.notify('PDF gelesen, aber kein bekannter Held gefunden.', color='warning')

        except Exception as ex:
            print(f"KRITISCHER FEHLER: {ex}")
            ui.notify(f'Fehler: {ex}', color='negative')

    # --- UI ---
    ui.query('.q-page').classes('bg-slate-100')
    with ui.column().classes('w-full items-center q-pa-md'):
        ui.label('🐺 Wolperting v2.0').classes('text-h3 text-primary q-mb-md')

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
                    
                    # Modifikator-Label
                    def calc_mod(val): return (val - 10) // 2
                    ml = ui.label(f'Mod: {calc_mod(hero.stats[stat])}').classes('text-blue-600 font-mono')
                    ui_elements['labels'] = ui_elements.get('labels', {})
                    ui_elements['labels'][stat] = ml
                    
                    def update_val(e, s=stat, label=ml):
                        val = int(e.value or 10)
                        hero.stats[s] = val
                        label.set_text(f'Mod: {calc_mod(val)}')

                    ni = ui.number(value=hero.stats[stat], on_change=update_val).classes('w-20')
                    ui_elements['inputs'][stat] = ni

ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)
