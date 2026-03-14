import os
import json
import pdfplumber
import io
from nicegui import ui, events
from logic import Character

# Pfade im Docker-Container
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

    # Robuste Upload-Funktion
    async def handle_upload(e):
        try:
            # 1. Name finden
            file_name = getattr(e, 'name', 'Charakter.pdf')
            
            # 2. Content finden (flexibel für verschiedene NiceGUI Versionen)
            content_source = None
            if hasattr(e, 'content'):
                content_source = e.content
            elif hasattr(e, 'file'):
                content_source = e.file
            
            if not content_source:
                ui.notify('Fehler: Dateiinhalt nicht lesbar', color='negative')
                return

            # 3. Stream auslesen (mit await für asynchrone Streams)
            raw_data = content_source.read()
            if hasattr(raw_data, '__await__'):
                raw_data = await raw_data

            # 4. PDF Text extrahieren
            with pdfplumber.open(io.BytesIO(raw_data)) as pdf:
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() or ""
                
                if full_text:
                    # AUSGABE INS LOG (Wichtig für uns!)
                    print(f"\n--- PDF TEXT START: {file_name} ---")
                    print(full_text)
                    print("--- PDF TEXT ENDE ---\n")
                    
                    # Automatischer Namens-Check
                    if "Takumi" in full_text:
                        hero.name = "Takumi Ishu"
                        name_input.set_value("Takumi Ishu")
                        ui.notify('Takumi Ishu erkannt!', color='positive')
                    else:
                        ui.notify('PDF erfolgreich analysiert!', color='positive')
                else:
                    ui.notify('Kein Text im PDF gefunden', color='warning')

        except Exception as ex:
            ui.notify(f'Upload-Fehler: {ex}', color='negative')
            print(f"Detail-Fehler: {ex}")

    # --- UI DESIGN ---
    ui.query('.q-page').classes('bg-slate-100')
    
    with ui.column().classes('w-full items-center q-pa-md'):
        ui.label('🐺 Wolperting v1.6').classes('text-h3 text-primary q-mb-md')

        # Upload Bereich
        with ui.card().classes('w-full max-w-lg q-pa-md q-mb-md shadow-lg'):
            ui.label('PDF Charakter-Import').classes('text-h6 text-grey-8')
            ui.upload(on_upload=handle_upload, label='Bogen hochladen').classes('w-full')

        # Charakter Basis-Daten
        with ui.card().classes('w-full max-w-lg q-pa-md shadow-lg'):
            global name_input
            name_input = ui.input('Name des Helden', value=hero.name, 
                                  on_change=lambda e: setattr(hero, 'name', e.value)).classes('w-full')
            ui.button('ÄNDERUNGEN SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-md px-6')

        # Attribute Bereich
        ui.label('Attribute').classes('text-h5 q-mt-lg text-primary')
        with ui.grid(columns=1).classes('w-full max-w-lg'):
            for stat in hero.stats:
                with ui.card().classes('q-pa-sm q-mb-xs shadow-sm'):
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label(stat).classes('text-bold text-lg')
                        
                        # Modifikator-Label
                        mod_val = hero.get_modifier(stat)
                        ml = ui.label(f'Mod: {mod_val}').classes('text-blue-600 font-mono')
                        
                        # Zahlen-Input
                        def update_stat(e, s=stat, label=ml):
                            val = int(e.value) if e.value is not None else 10
                            hero.stats[s] = val
                            new_mod = (val - 10) // 2
                            label.set_text(f'Mod: {new_mod}')

                        ui.number(value=hero.stats[stat], format='%.0f', 
                                  on_change=update_stat).classes('w-20')

# App Start
ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)
