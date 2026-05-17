import os
import logging
import urllib.parse
import re
import requests
import webbrowser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

TAB_CLOSE_TIMEOUT = 5

_driver = None
_browser_type = None


def get_browser_driver():
    """Returns the global browser driver instance, creating one if needed."""
    global _driver, _browser_type

    if _driver is not None:
        try:
            _driver.current_url
            return _driver
        except:
            _driver = None

    def get_chrome_type(attr):
        try:
            return getattr(ChromeType, attr)
        except AttributeError:
            # Fallback for common variations
            for fallback in ["GOOGLE", "CHROME", "CHROMIUM"]:
                try:
                    return getattr(ChromeType, fallback)
                except AttributeError:
                    continue
            return "google" # last resort string fallback

    browsers = [
        ("brave", get_chrome_type("BRAVE")),
        ("chrome", get_chrome_type("GOOGLE")),
    ]

    for browser_name, chrome_type in browsers:
        browser_path = find_browser_path(browser_name)
        if not browser_path:
            continue

        try:
            options = Options()
            options.add_argument("--remote-debugging-port=9222")
            options.binary_location = browser_path
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            # Check if this is the standard Google Chrome type
            is_google = (chrome_type == get_chrome_type("GOOGLE"))
            if not is_google:
                options.set_capability("chrome.binary", browser_name)

            _driver = webdriver.Chrome(options=options)
            _browser_type = browser_name
            logging.info(f"Started managed browser: {browser_name}")
            return _driver
        except Exception as e:
            logging.debug(f"Could not start {browser_name}: {e}")
            continue

    return None

# Setup logging to scratch/browser_log.txt
log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scratch", "browser_log.txt")
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def open_youtube_search(query: str) -> str:
    """
    Opens YouTube search results in the system's default browser.

    Args:
        query (str): The search term to look for on YouTube.

    Returns:
        str: The URL of the YouTube search page that was opened.
    """
    try:
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        logging.info(f"Opening YouTube search for query: '{query}'")
        webbrowser.open(url)
        logging.info(f"Successfully opened YouTube search: {url}")
        return url
    except Exception as e:
        error_msg = f"Error opening YouTube search for '{query}': {e}"
        logging.error(error_msg)
        print(error_msg)
        return ""


def open_url(url: str):
    """
    Opens any given URL in the system's default browser.

    Args:
        url (str): The URL to open in the browser.
    """
    print(f"[Browser] Opening URL: {url}")
    try:
        logging.info(f"Attempting to open URL: {url}")
        webbrowser.open(url)
        logging.info(f"Opened URL in default browser: {url}")
        print(f"[Browser] Successfully opened: {url}")

    except Exception as e:
        error_msg = f"Error opening URL '{url}': {e}"
        logging.error(error_msg)
        print(error_msg)


def get_page_text(url: str) -> str:
    """
    Uses requests + BeautifulSoup to fetch and parse visible text from any URL.
    Strips scripts, styles, and navigation elements.
    
    Args:
        url (str): The URL to scrape text from.
        
    Returns:
        str: Cleaned plain text from the webpage, truncated to a maximum of 3000 characters.
    """
    try:
        logging.info(f"Fetching page text from: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Strip away unwanted HTML elements that don't contain core content
        for element in soup(["script", "style", "nav", "header", "footer", "noscript", "aside"]):
            element.decompose()
            
        # Get raw text and clean up whitespace
        text = soup.get_text(separator=' ', strip=True)
        cleaned_text = ' '.join(text.split())
        
        # Truncate to 3000 characters
        if len(cleaned_text) > 3000:
            cleaned_text = cleaned_text[:3000] + "..."
            
        logging.info(f"Successfully scraped text from {url}. Length: {len(cleaned_text)} characters.")
        return cleaned_text
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Request failed for {url}: {e}"
        logging.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error scraping {url}: {e}"
        logging.error(error_msg)
        return error_msg


def youtube_top_result_url(query: str) -> str:
    """
    Scrapes the YouTube search page for the first video link using Requests.
    
    Args:
        query (str): The search term for the YouTube video.
        
    Returns:
        str: The full watch URL of the top result, or an empty string if an error occurs.
    """
    try:
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        logging.info(f"Scraping top YouTube result for: '{query}'")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # YouTube injects video data dynamically into the "ytInitialData" javascript object.
        # We use regex to find the first video URL ID from this JSON-like structure.
        match = re.search(r'"url":"(/watch\?v=[a-zA-Z0-9_-]+)"', response.text)
        
        if match:
            # Reconstruct the absolute URL
            video_url = f"https://www.youtube.com{match.group(1)}"
            
            # Sanitize extra unicode parameters if present (e.g. \u0026pp=...)
            video_url = video_url.split('\\u0026')[0]
            
            logging.info(f"Found top YouTube result URL: {video_url}")
            return video_url

        logging.warning(f"No video link found in YouTube search results for '{query}'.")
        return ""

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error while scraping YouTube for '{query}': {e}")
        return ""
    except Exception as e:
        logging.error(f"Unexpected error finding top YouTube result for '{query}': {e}")
        return ""


def close_browser_tab(website_name: str) -> bool:
    """
    Closes a specific browser tab for a website without closing the entire browser.
    Uses the managed browser session.
    """
    global _driver

    if _driver is None:
        try:
            _driver = get_browser_driver()
        except:
            pass

    if _driver is None:
        logging.info("No managed browser available")
        return False

    site_lower = website_name.lower().strip()

    domain_map = {
        "youtube": "youtube.com",
        "google": "google.com",
        "linkedin": "linkedin.com",
        "instagram": "instagram.com",
        "facebook": "facebook.com",
        "twitter": "twitter.com",
        "x": "x.com",
        "github": "github.com",
    }

    target_domain = domain_map.get(site_lower)
    if not target_domain:
        target_domain = f"{site_lower}.com"

    try:
        handles = _driver.window_handles

        for handle in handles:
            _driver.switch_to.window(handle)
            current_url = _driver.current_url.lower()

            if target_domain in current_url:
                _driver.close()
                logging.info(f"Closed tab for {target_domain}")
                return True

        logging.info(f"No tab found for {target_domain}")
        return False

    except Exception as e:
        logging.error(f"Error closing tab for {website_name}: {e}")
        return False


def close_browser():
    """Closes the managed browser entirely."""
    global _driver
    if _driver:
        try:
            _driver.quit()
            _driver = None
            logging.info("Closed managed browser")
        except Exception as e:
            logging.error(f"Error closing browser: {e}")


def find_browser_path(browser_name: str) -> str:
    """Finds the browser executable path."""
    paths = {
        "chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ],
        "brave": [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ],
        "chromium": [
            r"C:\Program Files\Chromium\chromium.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Chromium\Application\chromium.exe"),
        ],
    }

    for path in paths.get(browser_name, []):
        if os.path.exists(path):
            return path
    return ""


def open_browser_with_debugging():
    """Opens browser with remote debugging enabled (call this before opening browsers)."""
    import subprocess

    browser_paths = [
        (r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe", ["--remote-debugging-port=9222"]),
        (r"C:\Program Files\Google\Chrome\Application\chrome.exe", ["--remote-debugging-port=9222"]),
    ]

    for path, args in browser_paths:
        if os.path.exists(path):
            try:
                subprocess.Popen([path] + args)
                logging.info(f"Opened {path} with debugging port")
                return True
            except Exception as e:
                logging.debug(f"Could not open {path}: {e}")
    return False
