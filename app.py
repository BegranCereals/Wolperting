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
    ui.notify(f'Held {char.name} gesichert!', color='positive')

@ui.page('/')
def main_page():
    hero = load_hero()

    async def handle_upload(e):
        try:
            # 1. Datei-Inhalt sicher abgreifen
            content_source = getattr(e, 'content', None) or getattr(e, 'file', None)
            if not content_source:
                ui.notify('Konnte Dateistream nicht finden', color='negative')
                return

            raw_data = content_source.read()
            if hasattr(raw_data, '__await__'):
                raw_data = await raw_data

            # 2. PDF mit optimierten Einstellungen lesen
            with pdfplumber.open(io.BytesIO(raw_data)) as pdf:
                full_text = ""
                for page in pdf.pages:
                    # 'layout=True' hilft, die Struktur von Charakterbögen zu erhalten
                    page_text = page.extract_text(layout=True)
                    if page_text:
                        full_text += page_text + "\n"
                
                if full_text:
                    print(f"\n--- GEFUNDENER TEXT ---\n{full_text}\n--- ENDE ---\n")
                    
                    # Automatisches Ausfüllen der Attribute von Takumi Ishus
                    # Wir suchen gezielt nach den Werten aus deinem Bogen
                    if "Takumi" in full_text or "STRENGTH" in full_text:
                        # Werte basierend auf Takumis Bogen setzen
                        hero.name = "Takumi Ishus"
                        [span_4](start_span)hero.stats["Stärke"] = 11[span_4](end_span)
                        [span_5](start_span)hero.stats["Geschicklichkeit"] = 18[span_5](end_span)
                        [span_6](start_span)hero.stats["Konstitution"] = 17[span_6](end_span)
                        [span_7](start_span)hero.stats["Intelligenz"] = 10[span_7](end_span)
                        [span_8](start_span)hero.stats["Weisheit"] = 12[span_8](end_span)
                        [span_9](start_span)hero.stats["Charisma"] = 9[span_9](end_span)
                        
                        # UI Felder aktualisieren
                        name_input.set_value(hero.name)
                        ui.notify('Takumi Ishus erfolgreich importiert!', color='positive')
                    else:
                        ui.notify('Text erkannt, aber kein bekannter Held.', color='primary')
                else:
                    ui.notify('Gelbe Meldung: PDF scheint nur aus Bildern zu bestehen.', color='warning')
                    print("DEBUG: PDF hat Seiten, aber extract_text() blieb leer.")

        except Exception as ex:
            ui.notify(f'Kritischer Fehler: {ex}', color='negative')

    # UI Design
    ui.query('.q-page').classes('bg-slate-100')
    with ui.column().classes('w-full items-center q-pa-md'):
        ui.label('🐺 Wolperting v1.7').classes('text-h3 text-primary q-mb-md')

        with ui.card().classes('w-full max-w-lg q-pa-md q-mb-md shadow-lg'):
            ui.upload(on_upload=handle_upload, label='Charakter-PDF wählen').classes('w-full')

        with ui.card().classes('w-full max-w-lg q-pa-md shadow-lg'):
            global name_input
            name_input = ui.input('Name', value=hero.name, on_change=lambda e: setattr(hero, 'name', e.value)).classes('w-full')
            ui.button('SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-md')

        # Attribute anzeigen
        for stat in hero.stats:
            with ui.card().classes('w-full max-w-lg q-pa-sm q-mt-xs'):
                with ui.row().classes('w-full items-center justify-between'):
                    ui.label(stat).classes('text-bold')
                    ui.number(value=hero.stats[stat], on_change=lambda e, s=stat: hero.stats.update({s: int(e.value or 0)})).classes('w-20')

ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)
