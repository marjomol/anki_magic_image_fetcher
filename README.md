# 🖼️ Magic Image Fetcher (Anki Add-on)

Automatically fetch high-quality images for your Anki notes using [Pexels](https://www.pexels.com/api/), [Unsplash](https://unsplash.com/developers), or Google Images (via [SerpAPI](https://serpapi.com/)). This add-on fills empty `Picture` fields in a selected deck, using AnkiConnect to communicate with Anki.

```
magic_image_fetcher/
├── __init__.py
├── magic_image_fetcher.py
├── config.json
├── requirements.txt
├── README.md
├── LICENSE
└── manifest.json
```

---

## ✨ Features

- Automatically finds and inserts an image into the Picture field if it's empty.
- Supports multiple sources: Pexels, Unsplash, Google Images (via SerpAPI).
- Lets you select which deck and note fields to use as search input.
- Images are referenced and clickable — clicking them opens the photographer's page or image source.
- Rotating log at `debug.log` (1MB, keep 5 backups).

---

## 🔧 Requirements

- Anki 2.1+
- [AnkiConnect](https://ankiweb.net/shared/info/2055492159) (required; the add-on talks to Anki via HTTP on localhost:8765)
- Python 3 on your system
- Python package: `requests` (install with pip)

---

## 🛠️ Installation

1. Find by ID, clone or download this repository into your Anki add-ons folder.
2. Install and configure the [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on.
3. Change `config.example.json` to `config.json` and fill in your API keys.
4. Install the required libraries by running:
   ```
   pip install -r requirements.txt
   ```
5. Restart Anki. A new menu item **"🖼️ Fetch Images"** will appear under **Tools**.

---

## 📸 How to Use

1. Click **Tools → 🖼️ Fetch Images**
2. Select your target deck.
3. Select search fields visually using dropdown menus:
   - The add-on automatically detects available fields from your selected deck's note type
   - Choose up to **3 fields** in order of preference via interactive dropdowns
   - Selected fields will be searched in the order you chose (first field is highest priority)
4. Choose your preferred image source.
5. The script will find empty `Picture` fields and fill them with an image based on your field content. If no image is found for the given field, the next option is taken. If no image is found either way, the next note without picture is processed.

---

## 📁 Configuration

Edit `config.json` like so:

```json
{
  "PEXELS_API_KEY": "your_pexels_key_here",
  "UNSPLASH_ACCESS_KEY": "your_unsplash_key_here",
  "SERPAPI_KEY": "your_serpapi_key_here"
}
```

Missing keys will hide those sources from the picker.

---

## 🌐 API Key Sources

- **Pexels**: https://www.pexels.com/api/
- **Unsplash**: https://unsplash.com/developers
- **SerpAPI**: https://serpapi.com/

All of these services offer free API plans suitable for lightweight use.

---

## 💡 Tips

- Only one image will be fetched per note to minimize API usage.
- Images are fetched in medium or high quality depending on source support.
- Make sure the field name `Picture` exists in your note type, or adjust the script if needed.
- Logs are written to `debug.log` with rotation (1MB, keep 5 backups).
- Be mindful of API rate limits.

---

## 📝 License

MIT License. See [LICENSE](LICENSE) for details.

