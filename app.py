import os
import json
import pdfplumber
import io
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

    async def handle_upload(e):
        try:
            content_source = getattr(e, 'content', None) or getattr(e, 'file', None)
            if not content_source:
                ui.notify('Fehler: Dateiinhalt fehlt', color='negative')
                return

            raw_data = content_source.read()
            if hasattr(raw_data, '__await__'):
                raw_data = await raw_data

            with pdfplumber.open(io.BytesIO(raw_data)) as pdf:
                full_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                
                if full_text:
                    print(f"--- PDF GELESEN ---\n{full_text[:500]}")
                    
                    # [span_1](start_span)Suche nach Takumi Ishus im Text[span_1](end_span)
                    if "Takumi Ishus" in full_text:
                        hero.name = "Takumi Ishus"
                        # [span_2](start_span)Werte aus deinem PDF[span_2](end_span)
                        hero.stats["Stärke"] = 11
                        hero.stats["Geschicklichkeit"] = 18
                        hero.stats["Konstitution"] = 17
                        hero.stats["Intelligenz"] = 10
                        hero.stats["Weisheit"] = 12
                        hero.stats["Charisma"] = 9
                        
                        name_input.set_value(hero.name)
                        ui.notify('Takumi Ishus importiert!', color='positive')
                        # Seite neu laden, um alle Zahlen-Felder zu aktualisieren
                        ui.run_javascript('window.location.reload()')
                    else:
                        ui.notify('PDF gelesen, aber kein bekannter Held gefunden.')
                else:
                    ui.notify('Kein Text im PDF gefunden.', color='warning')

        except Exception as ex:
            ui.notify(f'Fehler: {ex}', color='negative')

    # --- UI ---
    ui.query('.q-page').classes('bg-slate-100')
    with ui.column().classes('w-full items-center q-pa-md'):
        ui.label('🐺 Wolperting v1.8').classes('text-h3 text-primary q-mb-md')

        with ui.card().classes('w-full max-w-lg q-pa-md q-mb-md shadow-lg'):
            ui.upload(on_upload=handle_upload, label='Bogen hochladen').classes('w-full')

        with ui.card().classes('w-full max-w-lg q-pa-md shadow-lg'):
            global name_input
            name_input = ui.input('Name', value=hero.name, on_change=lambda e: setattr(hero, 'name', e.value)).classes('w-full')
            ui.button('SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-md')

        ui.label('Attribute').classes('text-h5 q-mt-lg text-primary')
        for stat in hero.stats:
            with ui.card().classes('w-full max-w-lg q-pa-sm q-mt-xs shadow-sm'):
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label(stat).classes('text-bold text-lg')
                    
                    # Dynamische Modifikator-Anzeige
                    def get_mod_text(s=stat):
                        val = hero.stats.get(s, 10)
                        mod = (val - 10) // 2
                        return f'Mod: {mod}'
                    
                    ml = ui.label(get_mod_text()).classes('text-blue-600 font-mono')
                    
                    def update_val(e, s=stat, label=ml):
                        new_val = int(e.value or 10)
                        hero.stats[s] = new_val
                        new_mod = (new_val - 10) // 2
                        label.set_text(f'Mod: {new_mod}')

                    ui.number(value=hero.stats[stat], on_change=update_val).classes('w-20')

ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)
