import os
import requests
import json
import argparse
import logging

addon_dir = os.path.abspath(os.path.dirname(__file__))
log_path = os.path.join(addon_dir, "debug.log")

# Force unbuffered logging
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)

# Get logger and add handler to force flush
logger = logging.getLogger()
for handler in logger.handlers:
    handler.setLevel(logging.DEBUG)

def debug(msg):
    logging.debug(msg)
    # Force flush to disk
    for handler in logging.getLogger().handlers:
        handler.flush()

debug("🔄 Starting Magic Image Fetcher script")
debug(f"📂 Log path: {log_path}")

# Load config.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
debug(f"📂 Config path: {CONFIG_PATH}")
try:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    debug(f"✅ Config loaded successfully")
except FileNotFoundError:
    debug("❌ config.json not found. Please create it with your API keys.")
    config = {}
except Exception as e:
    debug(f"❌ Error loading config.json: {e}")
    config = {}

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("--deck", required=True)
parser.add_argument("--fields", required=True)
parser.add_argument("--source", required=False, default="pexels")

try:
    args = parser.parse_args()
    debug(f"✅ Arguments parsed: deck={args.deck}, fields={args.fields}, source={args.source}")
except Exception as e:
    debug(f"❌ Error parsing arguments: {e}")
    raise

ANKI_CONNECT_URL = "http://localhost:8765"
IMAGE_SOURCE = args.source.lower()
DECK_NAME = args.deck
SEARCH_FIELDS = [f.strip() for f in args.fields.split(",")]
PICTURE_FIELD = "Picture"

debug(f"🎯 Settings: deck='{DECK_NAME}', fields={SEARCH_FIELDS}, source={IMAGE_SOURCE}")

def search_anki_for_empty_picture_notes():
    debug(f"🔍 Searching for notes with empty {PICTURE_FIELD} field in deck '{DECK_NAME}'")
    payload = {
        "action": "findNotes",
        "version": 6,
        "params": {
            "query": f'deck:"{DECK_NAME}" {PICTURE_FIELD}:'
        }
    }
    try:
        response = requests.post(ANKI_CONNECT_URL, json=payload)
        result = response.json()["result"]
        debug(f"✅ Found {len(result)} notes with empty pictures")
        return result
    except Exception as e:
        debug(f"❌ Error searching notes: {e}")
        return []

def get_notes_info(note_ids):
    debug(f"📥 Fetching info for {len(note_ids)} notes")
    payload = {
        "action": "notesInfo",
        "version": 6,
        "params": {
            "notes": note_ids
        }
    }
    try:
        response = requests.post(ANKI_CONNECT_URL, json=payload)
        result = response.json()["result"]
        debug(f"✅ Retrieved info for {len(result)} notes")
        return result
    except Exception as e:
        debug(f"❌ Error getting notes info: {e}")
        return []

def search_image_url(query):
    debug(f"🔍 Searching image for query: '{query}' using source: {IMAGE_SOURCE}")
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
        return None, None, None

    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 1}

    try:
        debug(f"📡 Calling Pexels API for: {query}")
        res = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
        debug(f"📡 Pexels response status: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            if data["photos"]:
                photo = data["photos"][0]
                image_url = photo["src"]["medium"]
                photographer = photo["photographer"]
                photographer_url = photo["url"]
                debug(f"✅ Pexels found image by {photographer}")
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
        debug(f"📡 Calling Unsplash API for: {query}")
        res = requests.get("https://api.unsplash.com/search/photos", headers=headers, params=params)
        debug(f"📡 Unsplash response status: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            results = data.get("results", [])
            if results:
                photo = results[0]
                image_url = photo["urls"]["regular"]
                photographer = photo["user"]["name"]
                photographer_url = photo["user"]["links"]["html"]
                debug(f"✅ Unsplash found image by {photographer}")
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
        debug(f"📡 Calling SerpAPI for: {query}")
        res = requests.get("https://serpapi.com/search", params=params)
        debug(f"📡 SerpAPI response status: {res.status_code}")
        
        if res.status_code == 200:
            data = res.json()
            images = data.get("images_results", [])
            if images:
                image = images[0]
                image_url = image.get("original") or image.get("source") or image.get("thumbnail")
                debug(f"✅ SerpAPI found image: {image_url}")
                return image_url
            else:
                debug("⚠️ No images found in SerpAPI.")
        else:
            debug(f"❌ SerpAPI error {res.status_code}: {res.text}")
    except Exception as e:
        debug(f"❌ SerpAPI request failed: {e}")
    return None

def update_note_picture(note_id, image_url, credit_text=None, credit_link=None):
    debug(f"📝 Updating note {note_id} with image: {image_url}")
    
    # Make the image clickable if credit_link exists
    if credit_link:
        img_tag = f'<a href="{credit_link}" target="_blank"><img src="{image_url}" style="max-width: 100%;"></a>'
        debug(f"📷 Image with credit link to: {credit_link}")
    else:
        img_tag = f'<img src="{image_url}" style="max-width: 100%;">'
        debug(f"📷 Image without credit link")

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
                    PICTURE_FIELD: full_html
                }
            }
        }
    }
    
    try:
        response = requests.post(ANKI_CONNECT_URL, json=payload)
        debug(f"📡 AnkiConnect update response: {response.status_code}")
        if response.status_code == 200:
            debug(f"✅ Successfully updated note {note_id}")
        else:
            debug(f"❌ Failed to update note {note_id}: {response.text}")
    except Exception as e:
        debug(f"❌ Error updating note {note_id}: {e}")

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

    processed_count = 0
    success_count = 0

    for note in notes:
        fields = note["fields"]
        note_id = note["noteId"]
        processed_count += 1
        debug(f"📝 Processing note {processed_count}/{len(notes)} - ID: {note_id}")

        image_found = False

        for field_name in SEARCH_FIELDS:
            search_query = fields.get(field_name, {}).get("value", "").strip()
            if not search_query:
                debug(f"⏭️ Field '{field_name}' is empty, skipping")
                continue

            debug(f"🔍 Trying field '{field_name}' with query '{search_query}'")
            img_url, credit_name, credit_link = search_image_url(search_query)

            if img_url:
                update_note_picture(note_id, img_url, credit_name, credit_link)
                debug(f"✅ Image added to note {note_id} from field '{field_name}'")
                image_found = True
                success_count += 1
                break
            else:
                debug(f"❌ No image found for '{search_query}' in field '{field_name}'")

        if not image_found:
            debug(f"⏭️ Skipping note {note_id}: no image found for any search field.")

    debug(f"🎉 Processing complete! Updated {success_count}/{processed_count} notes")

if __name__ == "__main__":
    main()
