import subprocess
import time
import webbrowser
import os
import signal
import sys
import pyttsx3
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from execution.voice_engine import listen_continuously, speak
from execution.executor import execute_command
from execution.hud_server import run_hud_server
from dotenv import load_dotenv

load_dotenv()

def run_edith():
    print("Initializing E.D.I.T.H. Deployment...")

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Open the UI in the browser first
    ui_path = os.path.join(base_dir, "edith_ui.html")
    webbrowser.open(f"file://{ui_path}")
    print(f"[Launcher] Opened UI: {ui_path}")

    # Start the Orb WebSocket Server (which handles broadcasting AND the voice loop)
    # We run the main async loop of the orb_server directly
    import asyncio
    from execution.orb_server import main as orb_main
    
    speak("Edith is online. All systems functional.")
    print("\nE.D.I.T.H. is currently running. Say 'Hey Edith' to give commands.")
    print("Press Ctrl+C to terminate.")

    try:
        asyncio.run(orb_main())
    except KeyboardInterrupt:
        print("\n[Launcher] Termination sequence initiated...")
        print("[Launcher] E.D.I.T.H. offline.")

if __name__ == "__main__":
    run_edith()
