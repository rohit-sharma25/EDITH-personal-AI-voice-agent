import asyncio
import json
import threading
import websockets
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execution.hud_server import broadcast as original_broadcast, CONNECTED_CLIENTS, start_server
import execution.hud_server as hud_server
from execution.voice_engine import listen_continuously, speak

last_response_text = ""

def intercepted_broadcast(msg_type, content):
    global last_response_text
    if msg_type == "edith_output":
        last_response_text = content
        original_broadcast(msg_type, content)
    elif msg_type == "state" and content == "speaking":
        original_broadcast("state", {"state": "speaking", "text": last_response_text})
    else:
        original_broadcast(msg_type, content)

# Monkey-patch the broadcast function so voice_engine uses our interceptor
hud_server.broadcast = intercepted_broadcast

"""
E.D.I.T.H. Orb Server
Protocol:
- Server -> Client (JSON): {"type": "state", "content": "idle" | "listening" | "thinking" | "speaking"}
- Client -> Server (JSON): {"action": "wake"} | {"action": "stop"}
"""

async def message_handler(websocket, path=None):
    """Handles incoming manual actions from the UI."""
    CONNECTED_CLIENTS.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")
            if action == "wake":
                print("[Orb Server] Manual wake triggered via UI")
                if "text" in data:
                    # Execute typed commands directly in a thread without interrupting the voice engine
                    text_cmd = data["text"]
                    def execute_text_cmd():
                        from execution.executor import execute_command
                        import execution.hud_server as hud_server
                        hud_server.broadcast("state", "thinking")
                        try:
                            from execution.voice_engine import classify_command
                            cmd_type = classify_command(text_cmd)
                        except:
                            cmd_type = "unknown"
                        execute_command({"intent": text_cmd, "command_type": cmd_type})
                        hud_server.broadcast("state", "idle")
                        
                    threading.Thread(target=execute_text_cmd, daemon=True).start()
                else:
                    import execution.voice_engine as ve
                    ve.MANUAL_WAKE = True
            elif action == "stop":
                print("[Orb Server] Manual stop triggered via UI")
                hud_server.broadcast("state", "idle")
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        CONNECTED_CLIENTS.remove(websocket)

def start_voice_loop():
    """Background thread for voice interaction."""
    from execution.executor import execute_command
    # This loop blocks, so we run it in its own thread
    for command in listen_continuously():
        print(f"[Voice Loop] Intent detected: {command}")
        if command:
            try:
                execute_command(command)
            except Exception as e:
                print(f"[Orb Server] Error executing command: {e}")

async def main():
    print("[Orb Server] Initializing system...")
    
    # Crucial: Initialize the HUD server's main loop reference for cross-thread broadcasts
    import execution.hud_server as hud_server
    hud_server.MAIN_LOOP = asyncio.get_running_loop()
    
    # Start the voice engine loop in a background thread
    voice_thread = threading.Thread(target=start_voice_loop, daemon=True)
    voice_thread.start()
    
    # Start the WebSocket server on 8765
    async with websockets.serve(message_handler, "localhost", 8765):
        print("[Orb Server] WebSocket link established on ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[Orb Server] System shutting down.")
