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

### Basic Requirements
- Anki 2.1+ (desktop version)
- [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on installed (see installation steps below)

### Technical Requirements
- **Python 3.8+** must be installed on your computer
- **Python package**: `requests` (instructions below)
- **API Key** from at least one image service (Pexels, Unsplash, or SerpAPI)

> **⚠️ Note for beginners**: This add-on requires basic familiarity with:
> - Installing Python on your system
> - Using command line/terminal
> - Obtaining API keys from websites
> 
> If you're not comfortable with these steps, you may want to ask someone with technical knowledge to help with the initial setup. Once configured, the add-on works automatically with just a few clicks!

---

## 🛠️ Installation

### Step 1: Install Python (if not already installed)

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer and **check "Add Python to PATH"** (important!)
3. Verify installation: open Command Prompt and type `python --version`

**macOS:**
- Python 3 is usually pre-installed. Verify by opening Terminal and typing `python3 --version`

**Linux:**
- Python 3 is usually pre-installed. Verify by opening Terminal and typing `python3 --version`

### Step 2: Install AnkiConnect

1. In Anki, go to **Tools → Add-ons → Get Add-ons...**
2. Enter code: `2055492159`
3. Click OK and restart Anki

### Step 3: Install Magic Image Fetcher

1. Download this add-on:
   - From AnkiWeb (recommended): Use code `649414227`
   - Or manually: Download and extract into your Anki add-ons folder
2. Restart Anki

### Step 4: Install Python Dependencies

Open your command line (Command Prompt on Windows, Terminal on macOS/Linux) and run:

**Windows:**
```bash
python -m pip install requests
```

**macOS/Linux:**
```bash
python3 -m pip install requests
```

### Step 5: Get API Keys (Free!)

**What's an API key?** Think of it as a password that lets this add-on access free image databases. You need to create a free account on at least one of these services:

**Option 1: Pexels (Recommended for beginners)**
1. Go to [pexels.com/api](https://www.pexels.com/api/)
2. Click "Sign Up" and create a free account
3. After logging in, you'll see your API key — copy it!

**Option 2: Unsplash**
1. Go to [unsplash.com/developers](https://unsplash.com/developers)
2. Create a free account and register a new application
3. Copy the "Access Key"

**Option 3: SerpAPI (Google Images)**
1. Go to [serpapi.com](https://serpapi.com/)
2. Sign up for a free account
3. Copy your API key from the dashboard

### Step 6: Configure Your API Key

1. In your Anki add-ons folder, find the `magic_image_fetcher` folder
2. Rename `config.example.json` to `config.json`
3. Open `config.json` with any text editor (Notepad, TextEdit, etc.)
4. Paste your API key(s) like this:

```json
{
  "PEXELS_API_KEY": "paste_your_pexels_key_here",
  "UNSPLASH_ACCESS_KEY": "paste_your_unsplash_key_here",
  "SERPAPI_KEY": "paste_your_serpapi_key_here"
}
```

5. Save the file
6. Restart Anki

**Done!** You should now see **"🖼️ Fetch Images"** in the **Tools** menu.

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

Your `config.json` should look like this (only fill in the services you want to use):

```json
{
  "PEXELS_API_KEY": "your_pexels_key_here",
  "UNSPLASH_ACCESS_KEY": "your_unsplash_key_here",
  "SERPAPI_KEY": "your_serpapi_key_here"
}
```

**You only need ONE API key to get started!** Leave the others as empty strings (`""`) if you don't plan to use them. The add-on will only show available sources in the dropdown menu.

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

