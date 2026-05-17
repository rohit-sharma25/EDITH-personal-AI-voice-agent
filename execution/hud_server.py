import asyncio
import json
import websockets
import threading
from queue import Queue

# Global set to store connected clients
CONNECTED_CLIENTS = set()

# Command queue for receiving commands from UI
COMMAND_QUEUE = Queue()

async def handler(websocket):
    """Handles new WebSocket connections."""
    CONNECTED_CLIENTS.add(websocket)
    print(f"[HUD Server] Client connected. Total: {len(CONNECTED_CLIENTS)}")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get("action")
                text = data.get("text", "")

                if action == "wake":
                    print(f"[HUD Server] Wake command received: {text}")
                    if text:
                        COMMAND_QUEUE.put({"intent": text, "command_type": "text_input"})
                    else:
                        COMMAND_QUEUE.put({"intent": "manual_wake", "command_type": "wake"})
                elif action == "sleep":
                    print(f"[HUD Server] Sleep command received")
                    import execution.voice_engine as ve
                    ve.FORCE_SLEEP = True
                    ve.MANUAL_WAKE = False
                elif action == "command":
                    COMMAND_QUEUE.put({"intent": text, "command_type": "text_input"})
            except json.JSONDecodeError:
                pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        CONNECTED_CLIENTS.remove(websocket)
        print(f"[HUD Server] Client disconnected. Total: {len(CONNECTED_CLIENTS)}")

async def broadcast_async(message_dict):
    """Internal async broadcast function."""
    if not CONNECTED_CLIENTS:
        return
    
    message = json.dumps(message_dict)
    # Use asyncio.gather to send to all clients concurrently
    await asyncio.gather(
        *[client.send(message) for client in CONNECTED_CLIENTS],
        return_exceptions=True
    )

def broadcast(type, content):
    """
    Public thread-safe broadcast function.
    Usage: broadcast("user_input", "Hello Edith")
    """
    message = {"type": type, "content": content}
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            asyncio.run_coroutine_threadsafe(broadcast_async(message), loop)
        else:
            asyncio.run(broadcast_async(message))
    except Exception as e:
        print(f"[HUD Server] Broadcast error: {e}")

async def start_server():
    """Starts the WebSocket server."""
    print("[HUD Server] Starting WebSocket server on localhost:8765...")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever

def run_hud_server():
    """Helper to run the server in a background thread."""
    thread = threading.Thread(target=lambda: asyncio.run(start_server()), daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    # Test execution
    asyncio.run(start_server())
