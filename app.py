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
            # 1. Datei einlesen
            content = None
            for attr in ['content', 'file']:
                target = getattr(e, attr, None)
                if target:
                    raw = target.read()
                    content = await raw if asyncio.iscoroutine(raw) else raw
                    if content: break

            if not content:
                ui.notify('Keine Daten empfangen', color='negative')
                return

            # 2. PDF Text extrahieren
            full_text = ""
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    full_text += (page.extract_text() or "") + "\n"
            
            # 3. Dynamische Erkennung (statt Brute Force)
            # Wir suchen die erste Zeile für den Namen
            lines = [l.strip() for l in full_text.split('\n') if l.strip()]
            new_name = lines[0] if lines else "Unbekannter Held"
            
            # Suche nach typischen Klassen
            classes = ["Monk", "Paladin", "Ranger", "Wizard", "Fighter", "Rogue", "Cleric", "Bard"]
            found_class = "Abenteurer"
            for c in classes:
                if c.lower() in full_text.lower():
                    found_class = c
                    break

            # 4. Charakter aktualisieren
            hero.name = new_name
            hero.class_name = found_class
            
            # Versuche, HP zu finden (Suche nach "Hit Point Maximum")
            hp_match = re.search(r'Hit Point Maximum\s+(\d+)', full_text)
            if hp_match:
                hero.hp_max = int(hp_match.group(1))
                hero.hp_current = hero.hp_max

            # UI Update
            name_input.set_value(hero.name)
            info_label.set_text(f"Klasse: {hero.class_name}")
            hp_input.set_value(getattr(hero, 'hp_current', 10))
            hp_input.props(f'label="Max: {getattr(hero, "hp_max", 10)}"')
            
            ui.notify(f'Held {hero.name} geladen!', color='positive')

        except Exception as ex:
            ui.notify(f'Fehler beim Import: {ex}', color='negative')

    # --- UI ---
    ui.query('.q-page').classes('bg-slate-50')
    with ui.column().classes('w-full items-center q-pa-md max-w-2xl mx-auto'):
        ui.label('🐺 Wolperting v3.1').classes('text-h3 text-primary font-bold')

        with ui.card().classes('w-full q-pa-md shadow-md border-l-4 border-primary'):
            ui.upload(on_upload=handle_upload, label='Neuen PDF-Bogen testen').classes('w-full')

        with ui.card().classes('w-full q-pa-md q-mt-md shadow-lg'):
            global name_input, info_label
            name_input = ui.input('Name', value=hero.name).classes('text-xl font-bold w-full')
            info_label = ui.label(f"Klasse: {getattr(hero, 'class_name', '---')}").classes('text-grey-6')

        with ui.card().classes('w-full q-pa-md q-mt-md shadow-md'):
            global hp_input
            hp_input = ui.number(label="Trefferpunkte", value=getattr(hero, 'hp_current', 10)).classes('w-full')

        ui.button('SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-md')

ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)
