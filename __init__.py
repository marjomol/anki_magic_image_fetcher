import os
import subprocess
import json
import logging
from logging.handlers import RotatingFileHandler
import sys
from aqt import mw
from aqt.qt import QAction, QInputDialog
from aqt.utils import showInfo

addon_dir = os.path.abspath(os.path.dirname(__file__))
log_path = os.path.join(addon_dir, "debug.log")

# Set up rotating file handler
handler = RotatingFileHandler(
    log_path,
    maxBytes=1024*1024,  # 1MB
    backupCount=5  # Keep 5 old log files (debug.log.1, debug.log.2, etc.)
)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

def debug(msg):
    logger.debug(msg)
    # Force flush to disk
    for h in logger.handlers:
        h.flush()

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

    # Prompt for search fields
    search_fields, ok = QInputDialog.getText(mw, "Search Fields", "Enter search fields (comma-separated):")
    if not ok or not search_fields.strip():
        debug("❌ Search fields cancelled")
        return
    debug(f"✅ Search fields: {search_fields}")

    # Prompt for image source - use the available sources
    source_choice, ok = QInputDialog.getItem(mw, "Image Source", "Choose an image source:", source_options, 0, False)
    if not ok or not source_choice:
        debug("❌ Image source selection cancelled")
        return
    debug(f"✅ Image source selected: {source_choice}")

    debug(f"🚀 Launching script with deck={deck_name}, fields={search_fields}, source={source_choice}")

    # Run the script with args - use python3
    args = [
        "python3",  # Use system Python interpreter
        script_path,
        f"--deck={deck_name.strip()}",
        f"--fields={search_fields.strip()}",
        f"--source={source_choice.strip().lower()}"
    ]

    debug(f"📝 Command: {' '.join(args)}")

    try:
        process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
