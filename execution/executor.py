import urllib.parse
import subprocess
import os
from execution.voice_engine import speak
from execution.browser_control import open_url, open_youtube_search
from execution.gemini_engine import gemini_engine
from execution.research_agent import research_query
from execution.hud_server import broadcast

KNOWN_SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "linkedin": "https://www.linkedin.com",
    "instagram": "https://www.instagram.com",
    "facebook": "https://www.facebook.com",
    "github": "https://www.github.com",
    "twitter": "https://www.x.com",
    "x": "https://www.x.com",
}

KNOWN_APPS = {
    "vs code": [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
        r"C:\Program Files\Microsoft VS Code\Code.exe",
        r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
    ],
    "visual studio code": [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
        r"C:\Program Files\Microsoft VS Code\Code.exe",
        r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
    ],
    "telegram": [
        r"C:\Program Files\Telegram Desktop\Telegram.exe",
        os.path.expandvars(r"%APPDATA%\Telegram Desktop\Telegram.exe"),
    ],
    "discord": [
        r"C:\Program Files\Discord\Update.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Discord\Update.exe"),
    ],
    "spotify": [
        os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"),
        r"C:\Program Files\Spotify\Spotify.exe",
    ],
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "terminal": ["wt.exe"],
    "cmd": ["cmd.exe"],
    "command prompt": ["cmd.exe"],
    "explorer": ["explorer.exe"],
    "file explorer": ["explorer.exe"],
    "vlc": [r"C:\Program Files\VideoLAN\VLC\vlc.exe"],
    "steam": [r"C:\Program Files (x86)\Steam\steam.exe"],
    "obs": [r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"],
    "zoom": [os.path.expandvars(r"%APPDATA%\Zoom\bin\Zoom.exe")],
    "whatsapp": [os.path.expandvars(r"%APPDATA%\WhatsApp\WhatsApp.exe")],
    "slack": [os.path.expandvars(r"%APPDATA%\Slack\slack.exe")],
    "teams": [os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Teams\Update.exe")],
    "microsoft teams": [os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Teams\Update.exe")],
    "antigravity": ["python", os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.py")],
    "brave": [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
    ],
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ],
    "hud": [os.path.join(os.path.dirname(os.path.dirname(__file__)), "edith_ui.html")],
}

def find_app_path(paths):
    """Find the first valid path from a list of possible paths."""
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def open_app(app_name):
    """Opens an application by name."""
    app_lower = app_name.lower().strip()
    
    if app_lower in KNOWN_APPS:
        paths = KNOWN_APPS[app_lower]
        
        # Handle special case for antigravity (runs as python script)
        if app_lower == "antigravity":
            try:
                script_path = paths[1]
                subprocess.Popen(["python", script_path])
                speak(f"Opening Antigravity")
                return True
            except Exception as e:
                speak(f"Failed to open Antigravity: {str(e)}")
                return False
        
        # Handle special case for HUD (opens in browser)
        if app_lower == "hud":
            speak(f"Initializing {app_name}, Boss.")
            # Convert to file URL
            path = paths[0].replace("\\", "/")
            if not path.startswith("/"):
                path = "/" + path
            open_url(f"file://{path}")
            return True
        
        app_path = find_app_path(paths)
        if app_path:
            try:
                subprocess.Popen([app_path])
                speak(f"Opening {app_name}")
                return True
            except Exception as e:
                speak(f"Failed to open {app_name}: {str(e)}")
                return False
        else:
            speak(f"{app_name} is not installed or not found.")
            return False
    else:
        speak(f"I don't know how to open {app_name}.")
        return False

APP_PROCESS_NAMES = {
    "vs code": "Code",
    "visual studio code": "Code",
    "telegram": "Telegram",
    "discord": "Discord",
    "spotify": "Spotify",
    "notepad": "notepad",
    "calculator": "Calculator",
    "terminal": "WindowsTerminal",
    "cmd": "cmd",
    "command prompt": "cmd",
    "explorer": "explorer",
    "file explorer": "explorer",
    "vlc": "vlc",
    "steam": "steam",
    "obs": "obs64",
    "zoom": "Zoom",
    "whatsapp": "WhatsApp",
    "slack": "slack",
    "teams": "Teams",
    "microsoft teams": "Teams",
    "antigravity": "python",
    "chrome": "chrome",
    "brave": "brave",
    "browser": "brave",
    "firefox": "firefox",
    "edge": "msedge",
    "hud": "msedge",
}

def close_app(app_name):
    """Closes an application by name using taskkill."""
    app_lower = app_name.lower().strip()
    process_name = APP_PROCESS_NAMES.get(app_lower)
    
    if process_name:
        try:
            result = subprocess.run(["taskkill", "/F", "/IM", f"{process_name}.exe"], capture_output=True)
            if result.returncode == 0:
                speak(f"Closing {app_name}")
                return True
            return False
        except Exception as e:
            speak(f"Error closing {app_name}: {str(e)}")
            return False
    return False

def close_website(site_name):
    """Closes browser tabs for a specific site (closes all common browser processes)."""
    browsers = ["brave", "chrome", "msedge", "firefox"]
    success = False
    for browser in browsers:
        try:
            result = subprocess.run(["taskkill", "/F", "/IM", f"{browser}.exe"], capture_output=True)
            if result.returncode == 0:
                success = True
        except:
            pass
            
    if success:
        speak(f"Successfully closed {site_name}")
    else:
        speak(f"Could not close {site_name}.")
    return success

def execute_single_action(action_text):
    """Executes a single action."""
    action_lower = action_text.lower().strip()
    
    if action_lower.startswith("close ") or action_lower.startswith("quit "):
        target = action_lower.replace("close", "").replace("quit", "").strip()
        if target in KNOWN_SITES or "browser" in target or "tab" in target:
            return close_website(target)
        return close_app(target)
    
    if action_lower.startswith("open ") or action_lower.startswith("launch "):
        target = action_lower.replace("open", "").replace("launch", "").strip()
        if target in KNOWN_SITES:
            speak(f"Opening {target.capitalize()}")
            open_url(KNOWN_SITES[target])
            return True
        return open_app(target)
    
    elif "search" in action_lower:
        search_query = action_lower.replace("search for", "").replace("search", "").strip()
        if "youtube" in action_lower:
            open_youtube_search(search_query)
        else:
            open_url(f"https://www.google.com/search?q={urllib.parse.quote(search_query)}")
        return True
    
    return None

def execute_command(command_dict):
    """Executes the given command dictionary with Gemini intelligence."""
    if not command_dict:
        return

    intent = command_dict.get("intent", "").lower()
    command_type = command_dict.get("command_type", "unknown")

    print(f"\n[Executor] Running command: '{intent}' (Type: {command_type})")

    # Use Gemini for intent parsing
    gemini_result = gemini_engine.get_intent(intent)
    print(f"[Executor] Gemini result: {gemini_result}")

    if gemini_result:
        print(f"[Executor] Gemini Intent: {gemini_result}")
        g_type = gemini_result.get("type")
        g_intent = gemini_result.get("intent")
        g_target = gemini_result.get("target", "")
        g_params = gemini_result.get("parameters", "")
        
        if g_intent == "open":
            if g_type == "website" or "." in g_target or "com" in g_target:
                url = g_target if g_target.startswith("http") else f"https://www.{g_target}.com"
                speak(f"Opening {g_target}")
                open_url(url)
            else:
                open_app(g_target)
            return

        elif g_intent == "close":
            if g_type == "website" or "browser" in g_target or "tab" in g_target:
                close_website(g_target)
            else:
                close_app(g_target)
            return

        elif g_intent == "search" or g_type == "search":
            query = g_params if g_params else g_target
            if "youtube" in intent.lower() or "youtube" in g_target.lower():
                speak(f"Searching YouTube for {query}")
                open_youtube_search(query)
            else:
                speak(f"Searching Google for {query}")
                open_url(f"https://www.google.com/search?q={urllib.parse.quote(query)}")
            return

        elif g_intent == "question" or g_type == "question":
            summary = research_query(intent)
            speak(summary)
            return

    # Fallback
    print("[Executor] Falling back to execute_single_action")
    result = execute_single_action(intent)
    print(f"[Executor] Single action result: {result}")
