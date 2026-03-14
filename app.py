import os
import json
from nicegui import ui
from logic import Character

# Pfad innerhalb des Containers
DATA_DIR = '/app/data'
SAVE_FILE = os.path.join(DATA_DIR, 'current_char.json')

os.makedirs(DATA_DIR, exist_ok=True)

def load_hero():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                return Character.from_dict(json.load(f))
        except:
            return Character()
    return Character()

def save_hero(char):
    with open(SAVE_FILE, 'w') as f:
        json.dump(char.to_dict(), f, indent=4)
    ui.notify(f'Held {char.name} gesichert!', color='positive')

hero = load_hero()

ui.query('.q-page').classes('bg-slate-100')

with ui.column().classes('w-full items-center q-pa-md'):
    ui.label('🐺 Wolperting v1.0').classes('text-h3 text-primary q-mb-md')

    with ui.card().classes('w-full max-w-lg q-pa-md'):
        ui.input('Charakter Name', value=hero.name, 
                 on_change=lambda e: setattr(hero, 'name', e.value)).classes('w-full')
        ui.button('JETZT SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-sm')

    ui.label('Attribute').classes('text-h5 q-mt-md')
    with ui.grid(columns=1).classes('w-full max-w-lg'):
        for stat in hero.stats:
            with ui.card().classes('q-pa-sm'):
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label(stat).classes('text-bold text-lg')
                    
                    # Hier ist der Fix: Wir definieren das Label zuerst, 
                    # damit die Funktion darauf zugreifen kann
                    mod_label = ui.label(f'Mod: {hero.get_modifier(stat)}').classes('text-xl text-blue-500')
                    
                    # Die Update-Funktion
                    def update_stat(e, s=stat, ml=mod_label):
                        hero.stats[s] = int(e.value) if e.value is not None else 10
                        ml.set_text(f'Mod: {hero.get_modifier(s)}')
                    
                    # Das Eingabefeld nutzt direkt on_change
                    ui.number(value=hero.stats[stat], format='%.0f', 
                              on_change=update_stat).classes('w-20')

# Wichtig: Port 5005
ui.run(host='0.0.0.0', port=5005, title='Wolperting Mobile', reload=False)
