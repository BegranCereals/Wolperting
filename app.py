import os
import json
import pdfplumber
import io
from nicegui import ui, events
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

@ui.page('/')
def main_page():
    hero = load_hero()

    # Wir nutzen hier 'e' ganz allgemein ohne festen Typ
    async def handle_upload(e):
        try:
            # Der sicherste Weg in NiceGUI v1.4 an Name und Inhalt zu kommen:
            file_name = getattr(e, 'name', 'Charakter.pdf')
            content = e.content # Das ist der Dateistream
            
            # Wir lesen den Stream aus
            raw_data = content.read()
            
            # PDF verarbeiten
            with pdfplumber.open(io.BytesIO(raw_data)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                
                # Wenn wir Text gefunden haben, versuchen wir den Namen zu setzen
                if text:
                    print(f"--- PDF TEXT GEFUNDEN ---\n{text[:500]}")
                    # Kleiner Bonus: Wenn 'Takumi' im Text steht, trag es ein!
                    if "Takumi" in text:
                        hero.name = "Takumi Ishu"
                        name_input.set_value("Takumi Ishu")
                    
                    ui.notify(f'Erfolg: {file_name} eingelesen!', color='positive')
                else:
                    ui.notify('PDF leer oder nicht lesbar', color='warning')
        except Exception as ex:
            ui.notify(f'Fehler: {ex}', color='negative')

    ui.query('.q-page').classes('bg-slate-100')
    with ui.column().classes('w-full items-center q-pa-md'):
        ui.label('🐺 Wolperting v1.5').classes('text-h3 text-primary q-mb-md')

        with ui.card().classes('w-full max-w-lg q-pa-md q-mb-md'):
            ui.upload(on_upload=handle_upload, label='Bogen hochladen').classes('w-full')

        with ui.card().classes('w-full max-w-lg q-pa-md'):
            # Wir speichern die Referenz auf das Input-Feld, um es updaten zu können
            global name_input
            name_input = ui.input('Name', value=hero.name, 
                                  on_change=lambda e: setattr(hero, 'name', e.value)).classes('w-full')
            ui.button('SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-sm')

        # Attribute
        for stat in hero.stats:
            with ui.card().classes('w-full max-w-lg q-pa-sm q-mt-xs'):
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label(stat).classes('text-bold')
                    ui.number(value=hero.stats[stat], on_change=lambda e, s=stat: setattr(hero.stats, s, int(e.value or 0))).classes('w-20')

ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)
