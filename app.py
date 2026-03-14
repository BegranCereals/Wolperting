import os
import json
import pdfplumber
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
    ui.notify(f'Held {char.name} gesichert!')

# Wir definieren die Seite jetzt explizit
@ui.page('/')
def main_page():
    hero = load_hero()

    async def handle_upload(e: events.UploadEventArguments):
        # Datei sicher speichern
        pdf_path = os.path.join(DATA_DIR, e.name)
        with open(pdf_path, 'wb') as f:
            f.write(e.content.read())
        
        # PDF Text extrahieren
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                
                # Zeige die ersten Zeichen im Log (Portainer) und als Info
                print(f"EXTRAKTIERTER TEXT:\n{text[:500]}")
                ui.notify('PDF erfolgreich analysiert!', color='positive')
        except Exception as ex:
            ui.notify(f'Fehler beim Lesen: {ex}', color='negative')

    # --- UI LAYOUT ---
    ui.query('.q-page').classes('bg-slate-100')

    with ui.column().classes('w-full items-center q-pa-md'):
        ui.label('🐺 Wolperting v1.2').classes('text-h3 text-primary q-mb-md')

        # Upload Bereich
        with ui.card().classes('w-full max-w-lg q-pa-md q-mb-md'):
            ui.label('PDF Import').classes('text-h6')
            # Hier nutzen wir das Event-Argument korrekt
            ui.upload(on_upload=handle_upload, label='Bogen hochladen').classes('w-full')

        # Charakter Karte
        with ui.card().classes('w-full max-w-lg q-pa-md'):
            ui.input('Name', value=hero.name, 
                     on_change=lambda e: setattr(hero, 'name', e.value)).classes('w-full')
            ui.button('SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-sm')

        # Stats
        ui.label('Attribute').classes('text-h5 q-mt-md')
        with ui.grid(columns=1).classes('w-full max-w-lg'):
            for stat in hero.stats:
                with ui.card().classes('q-pa-sm'):
                    with ui.row().classes('w-full items-center justify-between'):
                        ui.label(stat).classes('text-bold')
                        ml = ui.label(f'Mod: {hero.get_modifier(stat)}')
                        
                        def update_stat(e, s=stat, label=ml):
                            hero.stats[s] = int(e.value) if e.value is not None else 10
                            label.set_text(f'Mod: {hero.get_modifier(s)}')
                        
                        ui.number(value=hero.stats[stat], format='%.0f', on_change=update_stat).classes('w-20')

# Start-Konfiguration
ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)
