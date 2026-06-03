import urllib.parse
import subprocess
import os
from execution.voice_engine import speak
from execution.browser_control import open_url, open_youtube_search
from execution.gemini_engine import gemini_engine
from execution.research_agent import research_query
from execution.hud_server import broadcast
from execution.config import get_known_sites, get_known_apps, get_app_process_names
from execution.logger import log_info, log_error, log_action

KNOWN_SITES = get_known_sites()
KNOWN_APPS = get_known_apps()
APP_PROCESS_NAMES = get_app_process_names()

def find_app_path(paths):
    """Find the first valid path from a list of possible paths."""
    for path in paths:
        candidate = os.path.expanduser(os.path.expandvars(path))
        if not os.path.isabs(candidate):
            candidate = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), candidate))
        if os.path.exists(candidate):
            return candidate
    return None

def open_app(app_name):
    """Opens an application by name."""
    app_lower = app_name.lower().strip()
    log_info("Executor", "Open app requested", f"app={app_lower}")
    
    if app_lower in KNOWN_APPS:
        paths = KNOWN_APPS[app_lower]
        app_path = find_app_path(paths)
        
        if app_lower == "antigravity":
            try:
                if not app_path:
                    raise FileNotFoundError("Antigravity script path not found")
                subprocess.Popen(["python", app_path])
                speak("Opening Antigravity")
                log_action("Executor", "launch_app", app_lower, "success")
                return True
            except Exception as e:
                speak(f"Failed to open Antigravity: {str(e)}")
                log_error("Executor", "Failed to open Antigravity", e)
                return False
        
        if app_lower == "hud":
            if not app_path:
                speak(f"HUD file not found for {app_name}.")
                log_error("Executor", f"HUD path missing for {app_name}")
                return False
            speak(f"Initializing {app_name}, Boss.")
            path = app_path.replace("\\", "/")
            if not path.startswith("/"):
                path = "/" + path
            open_url(f"file://{path}")
            log_action("Executor", "launch_app", app_lower, "success")
            return True
        
        if app_path:
            try:
                subprocess.Popen([app_path])
                speak(f"Opening {app_name}")
                log_action("Executor", "launch_app", app_lower, "success")
                return True
            except Exception as e:
                speak(f"Failed to open {app_name}: {str(e)}")
                log_error("Executor", f"Failed to open {app_name}", e)
                return False
        else:
            speak(f"{app_name} is not installed or not found.")
            log_error("Executor", f"App not found in file system: {app_name}")
            return False
    else:
        speak(f"I don't know how to open {app_name}.")
        log_error("Executor", f"Unknown app request: {app_name}")
        return False

def close_app(app_name):
    """Closes an application by name using taskkill."""
    app_lower = app_name.lower().strip()
    log_info("Executor", "Close app requested", f"app={app_lower}")
    process_name = APP_PROCESS_NAMES.get(app_lower)
    
    if process_name:
        try:
            result = subprocess.run(["taskkill", "/F", "/IM", f"{process_name}.exe"], capture_output=True)
            if result.returncode == 0:
                speak(f"Closing {app_name}")
                log_action("Executor", "close_app", app_lower, "success")
                return True
            log_error("Executor", f"Taskkill returned non-zero for {app_name}", details=f"code={result.returncode}")
            return False
        except Exception as e:
            speak(f"Error closing {app_name}: {str(e)}")
            log_error("Executor", f"Error closing {app_name}", e)
            return False
    log_error("Executor", f"Unknown process name for {app_name}")
    return False

def close_website(site_name):
    """Closes browser tabs for a specific site (closes all common browser processes)."""
    log_info("Executor", "Close website requested", f"site={site_name}")
    browsers = ["brave", "chrome", "msedge", "firefox"]
    success = False
    for browser in browsers:
        try:
            result = subprocess.run(["taskkill", "/F", "/IM", f"{browser}.exe"], capture_output=True)
            if result.returncode == 0:
                success = True
        except Exception as e:
            log_error("Executor", f"Taskkill error closing browser {browser}", e)
            continue
            
    if success:
        speak(f"Successfully closed {site_name}")
        log_action("Executor", "close_website", site_name, "success")
    else:
        speak(f"Could not close {site_name}.")
        log_error("Executor", f"Could not close website session for {site_name}")
    return success

def execute_single_action(action_text):
    """Executes a single action."""
    action_lower = action_text.lower().strip()
    log_info("Executor", "Execute single action", action_lower)
    
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
            log_action("Executor", "open_known_site", target, KNOWN_SITES[target])
            return True
        return open_app(target)
    
    elif "search" in action_lower:
        search_query = action_lower.replace("search for", "").replace("search", "").strip()
        if "youtube" in action_lower:
            open_youtube_search(search_query)
            return True
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
        log_info("Executor", "Gemini intent parsed", str(gemini_result))
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

    # Fallback for question-style queries when intent parsing fails
    question_words = ["what", "who", "when", "where", "how", "why", "weather", "news", "define", "explain"]
    if any(word in intent.lower() for word in question_words):
        log_info("Executor", "Fallback to research query for question-style intent", intent)
        summary = research_query(intent)
        speak(summary)
        return

    log_info("Executor", "Falling back to simple action execution", intent)
    print("[Executor] Falling back to execute_single_action")
    result = execute_single_action(intent)
    log_action("Executor", "fallback_action", intent, str(result))
    print(f"[Executor] Single action result: {result}")
