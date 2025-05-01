# 🖼️ Magic Image Fetcher (Anki Add-on)

Automatically fetch high-quality images for your Anki notes using [Pexels](https://www.pexels.com/api/), [Unsplash](https://unsplash.com/developers), or [SerpAPI](https://serpapi.com/). This add-on helps fill empty `Picture` fields in your selected deck.

```
magic_image_fetcher/
├── __init__.py
├── magic_image_fetcher.py
├── config.json
├── README.md
├── LICENSE
└── manifest.json
```

---

## ✨ Features

- Automatically finds and inserts an image into the Picture field if it's empty.
- Supports multiple sources: Pexels, Unsplash, Google Images (via SerpAPI).
- Lets you select which deck and fields to use as search input.
- Images are referenced and clickable — clicking them opens the photographer's page or image source.

---

## 🔧 Installation

1. Clone or download this repository into your Anki add-ons folder.
2. Change `config.example.json` to `config.json` and fill in your API keys.
3. Restart Anki. A new menu item **"🖼️ Fetch Images"** will appear under **Tools**.

---

## 📸 How to Use

1. Click **Tools → 🖼️ Fetch Images**
2. Select your target deck.
3. Enter search fields among the ones of your notes (comma-separated field names).
4. Choose your preferred image source.
5. The script will find empty `Picture` fields and fill them with an image based on your field content.

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

If you leave a key empty or omit it, that image source will not appear in the selection menu.

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

---

## 📝 License

MIT License. See [LICENSE](LICENSE) for details.
