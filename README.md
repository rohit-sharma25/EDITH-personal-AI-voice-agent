<img width="1366" height="661" alt="image" src="https://github.com/user-attachments/assets/4734683f-13ea-426b-9d6b-857de8e92509" />

# Edith PCE Agent

Edith is an autonomous, voice-activated AI assistant built using the Planning, Computing, and Execution (PCE) architecture. Edith runs in the background, constantly listening for a wake word, and is capable of controlling your web browser, performing research, and executing scheduled tasks using local Windows resources.

## 🏗 Architecture Overview

The system is separated into strict functional layers:
- **Coordinator Layer (`edith/edith_coordinator.py`)**: The master brain. Routes voice intents to the correct execution scripts and reads planning documents for context.
- **Voice Engine (`edith/execution/voice_engine.py`)**: The ears. Handles ambient noise calibration, wake word detection, and continuous audio recording.
- **Executor (`edith/execution/executor.py`)**: The hands. Triggers actions based on classified intents.
- **Browser Control (`edith/execution/browser_control.py`)**: Uses Selenium and BeautifulSoup to navigate, click, and scrape web pages.
- **Research Agent (`edith/execution/research_agent.py`)**: Performs automated searches and summarizes results via Gemini AI.

## 📁 Key Files

- `Start_EDITH.bat` — Windows launcher that uses the included virtual environment and starts `edith/run_edith.py`.
- `edith/run_edith.py` — Main local entrypoint that opens the UI and starts the event loop.
- `edith/edith_coordinator.py` — Coordinator layer and voice intent router.
- `edith/requirements.txt` — Python package dependencies.
- `edith/.env.example` — Example environment variables.

## ✅ Minimum Requirements

- Windows PC
- Python 3.8+ installed
- Microphone access
- Internet access for browser automation and API calls
- Chrome or Edge browser for the UI and Selenium automation

## 🔧 Setup on Windows

Open PowerShell or Command Prompt and run these commands from the repository root:

1. Create a virtual environment inside `edith\venv`:
   ```powershell
   py -3 -m venv edith\venv
   ```

2. Activate the virtual environment:
   - PowerShell:
     ```powershell
     edith\venv\Scripts\Activate.ps1
     ```
   - Command Prompt:
     ```cmd
     edith\venv\Scripts\activate.bat
     ```

3. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r edith\requirements.txt
   ```

4. Configure environment variables:
   ```powershell
   copy edith\.env.example edith\.env
   ```
   Then open `edith\.env` and add your keys:
   ```env
   SCRAPING_API_KEY=your_scraper_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   WAKE_WORD=Edith
   ```

## ▶️ Running Edith Locally on Your PC

### Option 1: Use the Windows launcher

From the repository root, double-click `Start_EDITH.bat`, or run it from PowerShell:

```powershell
.\Start_EDITH.bat
```

This launcher will:
- switch to the repo folder
- verify the virtual environment exists at `edith\venv\Scripts\python.exe`
- launch `edith/run_edith.py`
- pause after the program exits so you can read messages

### Option 2: Run directly from the virtual environment

From the repository root with the venv activated:

```powershell
python edith\run_edith.py
```

### Option 3: Run the coordinator only

If you want to start the core voice coordinator directly:

```powershell
python edith\edith_coordinator.py
```

## 🎙 How Edith Works

When the app starts, it will:
- open `edith/edith_ui.html` in your default browser
- initialize the Orb WebSocket server
- speak a startup confirmation
- listen for the wake word configured in `edith/.env`

You should see console messages like:
- `E.D.I.T.H. is currently running. Say 'Hey Edith' to give commands.`
- `Press Ctrl+C to terminate.`

## 💬 Voice Commands

Say the wake word first, then your command. Example phrases:

- `Hey Edith... open YouTube`
- `Hey Edith... open Google`
- `Hey Edith... search for latest AI news on YouTube`
- `Hey Edith... research the latest AI news`
- `Hey Edith... research Python tutorials every 60 minutes`

## 🛠 Troubleshooting

- If the launch script says the virtual environment is missing, run:
  ```powershell
  py -3 -m venv edith\venv
  ```
- If packages fail to install, ensure you are using the virtual environment's Python.
- If voice does not work, verify your microphone is connected and not in use by another app.
- If the browser UI does not open, check that your default browser is installed and allowed to open local files.

## 📌 Notes

- The live UI is opened from `edith/edith_ui.html`.
- The `Start_EDITH.bat` launcher is the easiest Windows start path.
- Use the `edith` folder as your working directory for all Python commands.
