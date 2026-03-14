import os
import json
import pdfplumber
from nicegui import ui
from logic import Character

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

# --- NEU: PDF LOGIK ---
def handle_upload(e):
    # Speichert das PDF temporär
    pdf_path = os.path.join(DATA_DIR, e.name)
    with open(pdf_path, 'wb') as f:
        f.write(e.content.read())
    
    # Text extrahieren (Testlauf)
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text()
        # Wir zeigen die ersten 200 Zeichen als Benachrichtigung
        ui.notify(f'PDF gelesen: {text[:100]}...')
        # Hier könnten wir jetzt 'hero.name' automatisch setzen, wenn wir den Text parsen
    ui.notify('Datei erfolgreich hochgeladen!')

hero = load_hero()

ui.query('.q-page').classes('bg-slate-100')

with ui.column().classes('w-full items-center q-pa-md'):
    ui.label('🐺 Wolperting v1.1').classes('text-h3 text-primary q-mb-md')

    # Upload Bereich
    with ui.card().classes('w-full max-w-lg q-pa-md q-mb-md'):
        ui.label('PDF Import (Beta)').classes('text-h6')
        ui.upload(on_upload=handle_upload, label='Regelwerk/Charakterblatt hochladen').classes('w-full')

    # Charakter Info
    with ui.card().classes('w-full max-w-lg q-pa-md'):
        ui.input('Name', value=hero.name, on_change=lambda e: setattr(hero, 'name', e.value)).classes('w-full')
        ui.button('SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-sm')

    # Attribute
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

ui.run(host='0.0.0.0', port=5005, title='Wolperting Mobile', reload=False)
