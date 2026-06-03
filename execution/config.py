import json
import os

CONFIG_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "config", "known_resources.json")
)

_DEFAULT_CONFIG = {
    "KNOWN_SITES": {},
    "KNOWN_APPS": {},
    "APP_PROCESS_NAMES": {}
}


def load_config():
    """Loads the dynamic browser/app configuration from JSON."""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            if not isinstance(config, dict):
                raise ValueError("Config file must contain a JSON object.")
            return {**_DEFAULT_CONFIG, **config}
    except FileNotFoundError:
        print(f"[Config] Warning: {CONFIG_FILE} not found. Using defaults.")
        return _DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"[Config] Error loading config: {e}")
        return _DEFAULT_CONFIG.copy()


CONFIG = load_config()


def get_known_sites():
    return CONFIG.get("KNOWN_SITES", {})


def get_known_apps():
    return CONFIG.get("KNOWN_APPS", {})


def get_app_process_names():
    return CONFIG.get("APP_PROCESS_NAMES", {})
