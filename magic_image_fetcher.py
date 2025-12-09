import os
import requests
import json
import argparse
import subprocess
import sys
from bs4 import BeautifulSoup
import logging

# Automatically install necessary packages if they are not present
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

# Load config.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
try:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
except FileNotFoundError:
    debug("❌ config.json not found. Please create it with your API keys.")
    config = {}

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("--deck", required=True)
parser.add_argument("--fields", required=True)
parser.add_argument("--source", required=False, default="pexels")
args = parser.parse_args()

ANKI_CONNECT_URL = "http://localhost:8765"
IMAGE_SOURCE = args.source.lower()
DECK_NAME = args.deck
SEARCH_FIELDS = [f.strip() for f in args.fields.split(",")]
PICTURE_FIELD = "Picture"

def search_anki_for_empty_picture_notes():
    payload = {
        "action": "findNotes",
        "version": 6,
        "params": {
            "query": f'deck:"{DECK_NAME}" {PICTURE_FIELD}:'
        }
    }
    return requests.post(ANKI_CONNECT_URL, json=payload).json()["result"]

def get_notes_info(note_ids):
    payload = {
        "action": "notesInfo",
        "version": 6,
        "params": {
            "notes": note_ids
        }
    }
    return requests.post(ANKI_CONNECT_URL, json=payload).json()["result"]

def search_image_url(query):
    if IMAGE_SOURCE == "pexels":
        return search_pexels(query)
    elif IMAGE_SOURCE == "serpapi":
        return search_serpapi(query), None, None
    elif IMAGE_SOURCE == "unsplash":
        return search_unsplash(query)
    else:
        debug("⚠️ Unknown image source. Defaulting to Pexels.")
        return search_pexels(query)

def search_pexels(query):
    PEXELS_API_KEY = config.get("PEXELS_API_KEY")
    if not PEXELS_API_KEY:
        debug("⚠️ Missing Pexels API key in config.json.")
        return None, None, None  # Returning image URL and credit info

    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 1}

    try:
        res = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
        if res.status_code == 200:
            data = res.json()
            if data["photos"]:
                photo = data["photos"][0]
                image_url = photo["src"]["medium"]
                photographer = photo["photographer"]
                photographer_url = photo["url"]
                return image_url, photographer, photographer_url
        debug(f"⚠️ No results from Pexels for: {query}")
    except Exception as e:
        debug(f"❌ Pexels error: {e}")
    return None, None, None

def search_unsplash(query):
    UNSPLASH_ACCESS_KEY = config.get("UNSPLASH_ACCESS_KEY")
    if not UNSPLASH_ACCESS_KEY:
        debug("⚠️ Missing Unsplash API key in config.json.")
        return None, None, None

    headers = {
        "Accept-Version": "v1",
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    params = {
        "query": query,
        "per_page": 1
    }

    try:
        res = requests.get("https://api.unsplash.com/search/photos", headers=headers, params=params)
        if res.status_code == 200:
            data = res.json()
            results = data.get("results", [])
            if results:
                photo = results[0]
                image_url = photo["urls"]["regular"]  # Higher quality
                photographer = photo["user"]["name"]
                photographer_url = photo["user"]["links"]["html"]
                return image_url, photographer, photographer_url
            else:
                debug(f"⚠️ No results from Unsplash for: {query}")
        else:
            debug(f"❌ Unsplash error {res.status_code}: {res.text}")
    except Exception as e:
        debug(f"❌ Unsplash error: {e}")
    return None, None, None

def search_serpapi(query):
    SERPAPI_KEY = config.get("SERPAPI_KEY")
    if not SERPAPI_KEY:
        debug("⚠️ Missing SerpAPI key in config.json.")
        return None

    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google_images"
    }

    try:
        res = requests.get("https://serpapi.com/search", params=params)
        if res.status_code == 200:
            data = res.json()
            images = data.get("images_results", [])
            if images:
                image = images[0]
                return image.get("original") or image.get("source") or image.get("thumbnail")
            else:
                debug("⚠️ No images found in SerpAPI.")
        else:
            debug(f"❌ SerpAPI error {res.status_code}: {res.text}")
    except Exception as e:
        debug(f"❌ SerpAPI request failed: {e}")
    return None

def update_note_picture(note_id, image_url, credit_text=None, credit_link=None):
    # Make the image clickable if credit_link exists
    if credit_link:
        img_tag = f'<a href="{credit_link}" target="_blank"><img src="{image_url}" style="max-width: 100%;"></a>'
    else:
        img_tag = f'<img src="{image_url}" style="max-width: 100%;">'

    # Full HTML for the field
    full_html = img_tag

    # Send the data to AnkiConnect
    payload = {
        "action": "updateNoteFields",
        "version": 6,
        "params": {
            "note": {
                "id": note_id,
                "fields": {
                    PICTURE_FIELD: full_html  # No additional encoding
                }
            }
        }
    }
    
    debug(f"📷 Generated HTML:\n{full_html}")  # Ensure this is printed correctly
    response = requests.post(ANKI_CONNECT_URL, json=payload)
    
    # Logging the response for debug
    debug(f"AnkiConnect update response: {response.status_code} - {response.text}")

def main():
    debug("🔄 Starting Magic Image Fetcher main()")

    if not config:
        debug("❌ Missing config. Aborting.")
        return

    note_ids = search_anki_for_empty_picture_notes()
    debug(f"🟡 Found {len(note_ids)} notes with empty picture fields.")

    if not note_ids:
        debug("⚠️ No matching notes to update.")
        return

    notes = get_notes_info(note_ids)
    debug(f"🟡 Retrieved {len(notes)} notes with full info.")

    for note in notes:
        fields = note["fields"]
        note_id = note["noteId"]
        debug(f"📝 Processing note ID {note_id}")

        image_found = False

        for field_name in SEARCH_FIELDS:
            search_query = fields.get(field_name, {}).get("value", "").strip()
            if not search_query:
                continue

            debug(f"🔍 Trying field '{field_name}' with query '{search_query}'")
            img_url, credit_name, credit_link = search_image_url(search_query)

            if img_url:
                update_note_picture(note_id, img_url, credit_name, credit_link)
                debug(f"✅ Image added to note {note_id} from field '{field_name}'")
                image_found = True
                break
            else:
                debug(f"❌ No image found for '{search_query}' in field '{field_name}'")

        if not image_found:
            debug(f"⏭️ Skipping note {note_id}: no image found for any search field.")

if __name__ == "__main__":
    main()