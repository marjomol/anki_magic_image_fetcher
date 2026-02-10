import os
import sys
import platform
import subprocess
import json
import logging
from logging.handlers import RotatingFileHandler
from aqt import mw
from aqt.qt import QAction, QInputDialog
from aqt.utils import showInfo

addon_dir = os.path.abspath(os.path.dirname(__file__))
log_path = os.path.join(addon_dir, "debug.log")

# Set up rotating file handler with UTF-8 encoding
handler = RotatingFileHandler(
    log_path,
    maxBytes=1024*1024,   # 1MB
    backupCount=5,        # keep 5 backups
    encoding="utf-8"      # IMPORTANT: allow emojis/non-ASCII
)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

def debug(msg):
    logger.debug(msg)

# Test that logging works immediately
debug("🔄 Starting Magic Image Fetcher")
debug(f"📂 Log path: {log_path}")

# Load config.json to check available API keys
def get_available_sources():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    debug(f"📂 Config path: {config_path}")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        debug(f"✅ Config loaded: {list(config.keys())}")
    except Exception as e:
        debug(f"⚠️ Failed to load config.json: {e}")
        showInfo(f"Error loading config.json: {e}")
        return []

    sources = []
    if config.get("PEXELS_API_KEY"):
        sources.append("Pexels")
    if config.get("UNSPLASH_ACCESS_KEY"):
        sources.append("Unsplash")
    if config.get("SERPAPI_KEY"):
        sources.append("SerpAPI")
    
    debug(f"✅ Available sources: {sources}")
    return sources


def get_fields_for_deck(deck_name):
    """Return the list of field names for the chosen deck's note type."""
    debug(f"📥 Fetching fields for deck: {deck_name}")

    note_ids = mw.col.find_notes(f'deck:"{deck_name}"')
    if not note_ids:
        debug("⚠️ No notes found in deck")
        showInfo("Selected deck has no notes.")
        return []

    models = {}
    for nid in note_ids:
        try:
            note = mw.col.get_note(nid)
            model = mw.col.models.get(note.mid)
            if model:
                models[note.mid] = model
        except Exception as e:
            debug(f"⚠️ Skipping note {nid}: {e}")

    if not models:
        debug("⚠️ No note types found for deck")
        showInfo("Could not determine note type for this deck.")
        return []

    # Choose note type if multiple are present
    model_items = [(model.get("name", f"Model {mid}"), mid, model) for mid, model in models.items()]
    selected_model = model_items[0][2]

    if len(model_items) > 1:
        model_items.sort(key=lambda item: item[0].lower())
        model_names = [item[0] for item in model_items]
        choice, ok = QInputDialog.getItem(
            mw,
            "Select Note Type",
            "Deck has multiple note types. Choose one:",
            model_names,
            0,
            False,
        )
        if not ok or not choice:
            debug("❌ Note type selection cancelled")
            return []
        debug(f"✅ Note type selected: {choice}")
        selected_model = next(model for name, _, model in model_items if name == choice)
    else:
        debug(f"✅ Single note type detected: {model_items[0][0]}")

    fields = [fld.get("name", "") for fld in selected_model.get("flds", []) if fld.get("name")]
    debug(f"📑 Available fields: {fields}")
    if not fields:
        showInfo("No fields found for the selected note type.")
    return fields


def choose_ordered_fields(fields, max_fields=3):
    """Prompt the user to choose up to max_fields fields in order."""
    available = list(fields)
    selected = []

    for idx in range(max_fields):
        if not available:
            break

        prompt = f"Choose field #{idx + 1}:"
        field, ok = QInputDialog.getItem(
            mw,
            "Select Field",
            prompt,
            available,
            0,
            False,
        )

        if not ok or not field:
            if selected:
                debug("✅ Field selection finished early by user")
                break
            debug("❌ Field selection cancelled")
            return []

        selected.append(field)
        available = [f for f in available if f != field]

    debug(f"✅ Ordered fields selected: {selected}")
    return selected


def run_image_script():
    debug("🚀 run_image_script() called")
    
    # Prompt for image source
    source_options = get_available_sources()
    if not source_options:
        debug("⚠️ No image sources configured in config.json.")
        showInfo("No image sources configured in config.json. Please add API keys.")
        return

    addon_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(addon_dir, "magic_image_fetcher.py")
    debug(f"📂 Script path: {script_path}")

    # Get list of all deck names
    deck_names = mw.col.decks.all_names_and_ids()
    deck_list = [deck.name for deck in deck_names]
    debug(f"📚 Available decks: {deck_list}")

    # Show dropdown for deck selection
    deck_name, ok = QInputDialog.getItem(mw, "Select Deck", "Choose a deck:", deck_list, 0, False)
    if not ok or not deck_name.strip():
        debug("❌ Deck selection cancelled")
        return
    debug(f"✅ Deck selected: {deck_name}")

    available_fields = get_fields_for_deck(deck_name)
    if not available_fields:
        return

    ordered_fields = choose_ordered_fields(available_fields, max_fields=3)
    if not ordered_fields:
        showInfo("No fields selected. Aborting.")
        return

    search_fields = ", ".join(ordered_fields)
    debug(f"✅ Search fields (ordered): {search_fields}")

    # Prompt for image source - use the available sources
    source_choice, ok = QInputDialog.getItem(mw, "Image Source", "Choose an image source:", source_options, 0, False)
    if not ok or not source_choice:
        debug("❌ Image source selection cancelled")
        return
    debug(f"✅ Image source selected: {source_choice}")

    debug(f"🚀 Launching script with deck={deck_name}, fields={search_fields}, source={source_choice}")

    # Choose Python interpreter based on OS
    # Windows: search for python.exe in Anki directory or use fallback
    # macOS/Linux: use python3 (from system PATH)
    if platform.system() == "Windows":
        # Prefer pythonw.exe to avoid opening a console window
        anki_dir = os.path.dirname(sys.executable)
        possible_python_paths = [
            os.path.join(anki_dir, "pythonw.exe"),
            os.path.join(anki_dir, "python.exe"),
            os.path.join(os.path.dirname(anki_dir), "pythonw.exe"),
            os.path.join(os.path.dirname(anki_dir), "python.exe"),
            "pythonw.exe",
            "python.exe",
            "python",
        ]

        python_cmd = None
        for path in possible_python_paths:
            if path in ["pythonw.exe", "python.exe", "python"] or os.path.isfile(path):
                python_cmd = path
                debug(f"🖥️ Windows detected, using Python: {python_cmd}")
                break

        if not python_cmd:
            python_cmd = "python"
            debug(f"🖥️ Windows detected, falling back to: {python_cmd}")
    else:
        python_cmd = "python3"
        debug(f"🖥️ {platform.system()} detected, using system python3")

    # Run the script with args
    args = [
        python_cmd,
        script_path,
        f"--deck={deck_name.strip()}",
        f"--fields={search_fields.strip()}",
        f"--source={source_choice.strip().lower()}"
    ]

    debug(f"📝 Command: {' '.join(args)}")

    try:
        creation_flags = 0
        if platform.system() == "Windows":
            creation_flags = subprocess.CREATE_NO_WINDOW

        process = subprocess.Popen(
            args,
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creation_flags,
        )
        debug(f"✅ Subprocess launched successfully with PID: {process.pid}")
        showInfo(f"Image fetching started! Check {log_path} for progress.")
    except Exception as e:
        debug(f"❌ Failed to launch subprocess: {e}")
        showInfo(f"Error launching subprocess: {e}")

# Attach to Anki menu
action = QAction("🖼️ Fetch Images", mw)
action.triggered.connect(run_image_script)
mw.form.menuTools.addAction(action)

debug("✅ Menu action attached successfully")
