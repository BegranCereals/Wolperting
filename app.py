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

def get_mod_value(score):
    """Berechnet den reinen numerischen Modifikator."""
    return (score - 10) // 2

def get_mod_str(score):
    """Gibt den Modifikator als Text (+4, -1 etc.) zurück."""
    mod = get_mod_value(score)
    return f"+{mod}" if mod >= 0 else str(mod)

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
    ui_elements = {'inputs': {}, 'mods': {}}

    def update_all_displays():
        """Aktualisiert die gesamte UI basierend auf dem hero-Objekt."""
        name_input.set_value(hero.name)
        class_input.set_value(hero.class_name)
        hp_input.set_value(hero.hp_current)
        ac_display.set_text(str(hero.ac))
        ini_display.set_text(f"+{hero.initiative}" if hero.initiative >= 0 else str(hero.initiative))
        pass_perc_display.set_text(str(getattr(hero, 'passive_perception', 10)))
        for stat, val in hero.stats.items():
            if stat in ui_elements['inputs']:
                ui_elements['inputs'][stat].set_value(val)
                ui_elements['mods'][stat].set_text(get_mod_str(val))

    async def handle_upload(e: events.UploadEventArguments):
        try:
            content = None
            for attr in ['content', 'file']:
                target = getattr(e, attr, None)
                if target:
                    raw = target.read()
                    content = await raw if asyncio.iscoroutine(raw) else raw
                    if content: break
            if not content: return

            full_text = ""
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    full_text += (page.extract_text() or "") + "\n"
            
            # 1. Name & Klasse (wie bisher)
            lines = [l.strip() for l in full_text.split('\n') if l.strip()]
            if lines: hero.name = lines[0]
            
            # 2. Attribute auslesen
            stats_map = {"Stärke": ["str"], "Geschicklichkeit": ["dex"], "Konstitution": ["con"], 
                         "Intelligenz": ["int"], "Weisheit": ["wis"], "Charisma": ["cha"]}
            for stat_name, aliases in stats_map.items():
                for alias in aliases:
                    match = re.search(rf'{alias}\s*(\d+)', full_text, re.IGNORECASE)
                    if match:
                        hero.stats[stat_name] = int(match.group(1))
                        break

            # 3. Initiative & Passive Wahrnehmung aus PDF (oder berechnen)
            ini_match = re.search(r'initiative\s*([+-]?\d+)', full_text, re.IGNORECASE)
            hero.initiative = int(ini_match.group(1)) if ini_match else get_mod_value(hero.stats["Geschicklichkeit"])
            
            pp_match = re.search(r'(?:passive wisdom|passive perception)\s*(\d+)', full_text, re.IGNORECASE)
            hero.passive_perception = int(pp_match.group(1)) if pp_match else (10 + get_mod_value(hero.stats["Weisheit"]))

            # 4. HP & AC
            hp_m = re.search(r'hit point maximum\s*(\d+)', full_text.lower())
            if hp_m: hero.hp_max = int(hp_m.group(1)); hero.hp_current = hero.hp_max
            ac_m = re.search(r'armor class\s*(\d+)', full_text.lower())
            if ac_m: hero.ac = int(ac_m.group(1))

            update_all_displays()
            ui.notify('Import abgeschlossen!', color='positive')
        except Exception as ex:
            ui.notify(f'Fehler: {ex}', color='negative')

    # --- UI LAYOUT ---
    ui.query('.q-page').classes('bg-slate-100')
    with ui.column().classes('w-full items-center q-pa-md max-w-2xl mx-auto'):
        ui.label('🐺 Wolperting v3.6').classes('text-h3 text-primary font-bold q-mb-md')

        with ui.card().classes('w-full q-pa-md shadow-lg border-t-8 border-primary'):
            ui.upload(on_upload=handle_upload, label='Bogen laden').classes('w-full q-mb-sm')
            name_input = ui.input('Held', value=hero.name).classes('text-h5 w-full')
            class_input = ui.input('Klasse', value=hero.class_name).classes('w-full')

        # Profi-Leiste: HP, AC, Initiative, Passive Wahrnehmung
        with ui.row().classes('w-full q-mt-md gap-2 justify-between'):
            # HP
            with ui.card().classes('col q-pa-sm items-center shadow-md bg-red-50 border-red-200'):
                ui.label('HP').classes('text-xs font-bold text-red-600')
                hp_input = ui.number(value=hero.hp_current).classes('text-h5 w-16')
            # AC
            with ui.card().classes('col q-pa-sm items-center shadow-md bg-blue-50 border-blue-200'):
                ui.label('AC').classes('text-xs font-bold text-blue-600')
                ac_display = ui.label(str(hero.ac)).classes('text-h5 font-bold text-blue-900')
            # INI
            with ui.card().classes('col q-pa-sm items-center shadow-md bg-orange-50 border-orange-200'):
                ui.label('INI').classes('text-xs font-bold text-orange-600')
                ini_display = ui.label(str(hero.initiative)).classes('text-h5 font-bold text-orange-900')
            # PASSIVE PERC
            with ui.card().classes('col q-pa-sm items-center shadow-md bg-green-50 border-green-200'):
                ui.label('PASS. W.').classes('text-xs font-bold text-green-600')
                pass_perc_display = ui.label(str(getattr(hero, 'passive_perception', 10))).classes('text-h5 font-bold text-green-900')

        # Attribute
        grid = ui.grid(columns=2).classes('w-full q-mt-md gap-4')
        with grid:
            for stat in hero.stats:
                with ui.card().classes('q-pa-md shadow-md items-center'):
                    ui.label(stat).classes('text-xs uppercase text-gray-400 font-bold')
                    mod_label = ui.label(get_mod_str(hero.stats[stat])).classes('text-h4 font-bold text-gray-800')
                    ui_elements['mods'][stat] = mod_label
                    val_input = ui.number(value=hero.stats[stat], 
                        on_change=lambda e, s=stat: [
                            hero.stats.update({s: int(e.value or 10)}),
                            ui_elements['mods'][s].set_text(get_mod_str(int(e.value or 10))),
                            # Automatik für Pass. Wahrnehmung wenn Weisheit sich ändert
                            pass_perc_display.set_text(str(10 + get_mod_value(hero.stats["Weisheit"]))) if s == "Weisheit" else None
                        ]).classes('w-16 text-center')
                    ui_elements['inputs'][stat] = val_input

        ui.button('SPEICHERN', on_click=lambda: save_hero(hero)).classes('w-full q-mt-xl py-4 text-xl shadow-xl')

ui.run(host='0.0.0.0', port=5005, title='Wolperting', reload=False)
