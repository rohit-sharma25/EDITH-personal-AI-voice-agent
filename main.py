from execution.voice_engine import listen_continuously, speak, MANUAL_WAKE
import execution.voice_engine as ve
from execution.executor import execute_command
import os
from dotenv import load_dotenv
from execution.hud_server import run_hud_server, COMMAND_QUEUE
import threading
import time

load_dotenv()

AUTHORIZED_USER = os.getenv("AUTHORIZED_USER", "Boss")

def run_agent():
    print("--- Starting E.D.I.T.H. PCE Agent ---")
    run_hud_server()

    speak(f"E.D.I.T.H. online. Good evening, {AUTHORIZED_USER}. All systems nominal. How can I assist?")

    def voice_loop():
        for command in listen_continuously():
            if command:
                execute_command(command)

    voice_thread = threading.Thread(target=voice_loop, daemon=True)
    voice_thread.start()

    try:
        while True:
            if not COMMAND_QUEUE.empty():
                command = COMMAND_QUEUE.get()
                print(f"[Main] Got command from UI: {command}")
                if command:
                    if command.get("intent") == "manual_wake":
                        ve.MANUAL_WAKE = True
                    else:
                        execute_command(command)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nShutting down E.D.I.T.H...")

if __name__ == "__main__":
    run_agent()
