import os
import subprocess
import sys
import json
import logging
from aqt import mw
from aqt.qt import QAction, QInputDialog

# Automatically install required packages if they are not present
required_packages = ["requests", "beautifulsoup4"]

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

addon_dir = os.path.abspath(os.path.dirname(__file__))
log_path = os.path.join(addon_dir, "debug.log")

logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def debug(msg):
    logging.debug(msg)

debug("🔄 Starting Magic Image Fetcher")

# Load config.json to check available API keys
def get_available_sources():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        debug(f"⚠️ Failed to load config.json: {e}")
        return []

    sources = []
    if config.get("PEXELS_API_KEY"):
        sources.append("Pexels")
    if config.get("UNSPLASH_ACCESS_KEY"):
        sources.append("Unsplash")
    if config.get("SERPAPI_KEY"):
        sources.append("SerpAPI")
    return sources


def run_image_script():
    # Prompt for image source
    source_options = get_available_sources()
    if not source_options:
        debug("⚠️ No image sources configured in config.json.")
        return

    addon_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(addon_dir, "magic_image_fetcher.py")

    # Get list of all deck names
    deck_names = mw.col.decks.all_names_and_ids()
    deck_list = [deck.name for deck in deck_names]

    # Show dropdown for deck selection
    deck_name, ok = QInputDialog.getItem(mw, "Select Deck", "Choose a deck:", deck_list, 0, False)
    if not ok or not deck_name.strip():
        return

    # Prompt for search fields
    search_fields, ok = QInputDialog.getText(mw, "Search Fields", "Enter search fields (comma-separated):")
    if not ok or not search_fields.strip():
        return

    # Prompt for image source
    source_options = ["Pexels", "Unsplash", "SerpAPI"]
    source_choice, ok = QInputDialog.getItem(mw, "Image Source", "Choose an image source:", source_options, 0, False)
    if not ok or not source_choice:
        return

    # Run the script with args
    args = [
        "python",
        script_path,
        f"--deck={deck_name.strip()}",
        f"--fields={search_fields.strip()}",
        f"--source={source_choice.strip().lower()}"
    ]

    subprocess.Popen(args, shell=True)

# Attach to Anki menu
action = QAction("🖼️ Fetch Images", mw)
action.triggered.connect(run_image_script)
mw.form.menuTools.addAction(action)