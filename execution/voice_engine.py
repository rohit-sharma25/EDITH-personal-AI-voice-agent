"""
Voice Engine Module for E.D.I.T.H.

This module handles continuous microphone listening, wake word detection,
and lore-accurate personality implementation.
"""

import os
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
from execution.hud_server import broadcast

load_dotenv()

# Identity Configuration
AUTHORIZED_USER = os.getenv("AUTHORIZED_USER", "Boss")
WAKE_PHRASE = os.getenv("WAKE_PHRASE", "Hey Edith")
# Common mishearings of "Edith"
WAKE_VARIATIONS = ["edith", "edit", "aditya", "adith", "eddy", "eddie", "idith"]

# Global flags for manual triggering via UI
MANUAL_WAKE = False
MANUAL_TEXT = None
FORCE_SLEEP = False

def speak(text):
    """Speaks the given text and broadcasts to HUD."""
    print(f"[Edith] {text}")
    broadcast("edith_output", text)
    broadcast("state", "speaking")
    try:
        engine = pyttsx3.init()
        rate = int(os.getenv("EDITH_VOICE_RATE", 165))
        volume = float(os.getenv("EDITH_VOICE_VOLUME", 0.9))
        engine.setProperty('rate', rate)
        engine.setProperty('volume', volume)
        
        # Set a slightly more robotic/precise voice if available
        voices = engine.getProperty('voices')
        for voice in voices:
            if "Zira" in voice.name or "David" in voice.name:
                engine.setProperty('voice', voice.id)
                break
        
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[Speaker Error] {e}")
    finally:
        broadcast("state", "idle")

def classify_command(text):
    """Classifies the transcribed command into a command type."""
    text_lower = text.lower()
    
    if any(phrase in text_lower for phrase in ["what does edith stand for", "what is edith", "meaning of your name"]):
        return "system_acronym"
    
    if "open " in text_lower or any(keyword in text_lower for keyword in ["play", "show me", "launch"]):
        return "open"
    elif any(keyword in text_lower for keyword in ["search", "find", "what is", "research", "tell me about"]):
        return "research"
    elif any(keyword in text_lower for keyword in ["close", "exit", "quit", "stop"]):
        return "close"
    elif any(keyword in text_lower for keyword in ["automate", "fill", "download"]):
        return "automate"
    else:
        return "unknown"

def listen_continuously():
    """
    Runs a continuous loop listening for E.D.I.T.H.'s wake phrase.
    """
    global MANUAL_WAKE, FORCE_SLEEP
    recognizer = sr.Recognizer()
    # Increase sensitivity
    recognizer.dynamic_energy_threshold = True
    
    try:
        microphone = sr.Microphone()
    except OSError as e:
        print(f"Microphone Error: {e}")
        return

    print("Calibrating sensors...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

    print(f"E.D.I.T.H. monitoring for '{WAKE_PHRASE}'...")
    awake = False

    while True:
        try:
            if not awake:
                with microphone as source:
                    # Use a short timeout so we can check the MANUAL_WAKE flag frequently
                    try:
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    except sr.WaitTimeoutError:
                        if MANUAL_WAKE:
                            MANUAL_WAKE = False
                            print("Manual wake triggered.")
                            broadcast("state", "listening")
                            speak(f"Online, {AUTHORIZED_USER}.")
                            awake = True
                            yield None
                        continue
                
                try:
                    text = recognizer.recognize_google(audio).lower()
                    print(f"[Debug] Detected: '{text}'")
                    broadcast("user_input", text)
                    
                    # Check for any wake word variation
                    found_wake = False
                    trigger_word = ""
                    for var in WAKE_VARIATIONS:
                        if var in text:
                            found_wake = True
                            trigger_word = var
                            break
                    
                    if found_wake:
                        print("Authorization confirmed.")
                        broadcast("state", "listening")
                        
                        # Check if there's a command after the wake word in the same sentence
                        parts = text.split(trigger_word, 1)
                        command_after = parts[1].strip(" ,.")
                        
                        if command_after:
                            # Direct command execution
                            print(f"Direct command detected: {command_after}")
                            broadcast("state", "thinking")
                            yield {
                                "intent": command_after,
                                "command_type": classify_command(command_after)
                            }
                            awake = True
                        else:
                            speak(f"E.D.I.T.H. online. Good evening, {AUTHORIZED_USER}. Interface initialized.")
                            awake = True
                    continue
                except sr.UnknownValueError:
                    continue
                
            # Active Session
            if FORCE_SLEEP:
                FORCE_SLEEP = False
                speak(f"Going to sleep, {AUTHORIZED_USER}. Say '{WAKE_PHRASE}' to wake me.")
                broadcast("state", "idle")
                awake = False
                continue

            with microphone as source:
                print("\n[Debug] Awaiting instructions...")
                broadcast("state", "listening")
                command_audio = recognizer.listen(source, timeout=None, phrase_time_limit=8)
                    
            try:
                broadcast("state", "thinking")
                command_text = recognizer.recognize_google(command_audio).lower()
                print(f"Input: {command_text}")
                broadcast("user_input", command_text)
                
                if any(phrase in command_text for phrase in ["sleep", "stop listening", "go to sleep", "shut down"]):
                    speak(f"Going to sleep. Just say '{WAKE_PHRASE}' if you need me again, {AUTHORIZED_USER}.")
                    broadcast("state", "idle")
                    awake = False
                    continue
                    
                command_type = classify_command(command_text)
                
                if command_type == "system_acronym":
                    speak("Even Dead, I'm The Hero. Mr. Stark loved his acronyms.")
                    continue

                yield {
                    "intent": command_text,
                    "command_type": command_type
                }
                # Keep listening after command (don't go to sleep)
                
            except sr.UnknownValueError:
                # Keep listening even if speech not understood
                pass
            except sr.RequestError as e:
                print(f"Network error: {e}")
                speak(f"I'm experiencing some interference, {AUTHORIZED_USER}.")
                
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Satellite link unstable: {e}")
        except KeyboardInterrupt:
            print("Shutting down E.D.I.T.H...")
            break
        except Exception as e:
            print(f"Internal interference: {e}")
            # Reset state on error
            awake = False

if __name__ == "__main__":
    for command in listen_continuously():
        print(f"Main loop received: {command}")
