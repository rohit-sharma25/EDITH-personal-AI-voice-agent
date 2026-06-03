import os
import re
import datetime
from execution.voice_engine import listen_continuously, speak
from execution.browser_control import open_url, youtube_top_result_url
from execution.research_agent import research_and_summarise, timed_research_loop
from execution.logger import log_info, log_error


def log_error_to_history(component: str, issue: str, resolution: str, insight: str):
    """Appends an error log to history.md in the required format."""
    log_error(component, issue, details=f"{resolution}; {insight}")

def read_planning_doc(command_type: str):
    """Reads the correct planning document into memory based on command type."""
    doc_map = {
        "open": "browser_control.md",
        "research": "research.md",
        "automate": "browser_control.md"
    }
    
    filename = doc_map.get(command_type)
    if filename:
        filepath = os.path.join(os.path.dirname(__file__), "planning", filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                log_info("Coordinator", f"Loaded planning document: {filename}", f"len={len(content)}")
        except Exception as e:
            log_error("Coordinator", f"Could not read planning doc {filename}", e)

def execute_intent(command_dict):
    """Routes the intent to the correct execution function."""
    intent = command_dict.get("intent", "").lower()
    command_type = command_dict.get("command_type", "unknown")
    
    log_info("Coordinator", "Processing intent", f"intent={intent}; type={command_type}")
    
    # 2. Read the appropriate planning doc
    read_planning_doc(command_type)
    
    # 3. Call the right execution function
    
    # Check for scheduled interval loops first
    match = re.search(r'every (\d+) minutes', intent)
    if match:
        interval = int(match.group(1))
        # Extract the topic by removing the time phrase and commands
        topic = re.sub(r'every \d+ minutes', '', intent).replace('research', '').replace('search for', '').strip()
        speak(f"Setting up scheduled research for {topic} every {interval} minutes.")
        timed_research_loop(topic, interval)
        return

    # Check for Youtube specific queries
    if "youtube" in intent:
        # E.g. "search for cute cats on youtube" -> "cute cats"
        query = intent.replace("open", "").replace("search for", "").replace("search", "").replace("youtube", "").replace("on", "").strip()
        
        if query:
            speak(f"Finding top YouTube video for {query}")
            url = youtube_top_result_url(query)
            if url:
                speak("Opening the video now.")
                open_url(url)
            else:
                speak("I couldn't find a top video for that query.")
        else:
            speak("Opening YouTube")
            open_url("https://www.youtube.com")
            
    # Check for standard open URLs
    elif "open" in intent:
        target = intent.replace("open", "").strip()
        target_clean = target.replace(" ", "")
        if target_clean == "google":
            url = "https://www.google.com"
        else:
            url = f"https://www.{target_clean}.com"
            
        speak(f"Opening {target}")
        open_url(url)
        
    # Check for research queries
    elif "research" in intent or "search" in intent:
        query = intent.replace("research", "").replace("search for", "").replace("search", "").strip()
        speak(f"Researching {query} now. One moment.")
        
        # 4. Speak result back
        summary = research_and_summarise(query)
        speak(summary)
        
    elif command_type == "automate":
        speak("Automation layer is currently under construction.")
        
    else:
        speak("I am not sure how to handle that intent.")

def main():
    print("=======================================")
    print("      EDITH COORDINATION LAYER         ")
    print("=======================================")
    
    speak("Edith online. Say Hey Edith to begin.")
    
    try:
        # 1 & 6. Call voice_engine and loop continuously
        for command in listen_continuously():
            if not command:
                continue
                
            attempts = 0
            success = False
            
            # 5. On any exception, retry once, log to history
            while attempts < 2 and not success:
                try:
                    execute_intent(command)
                    success = True
                except Exception as e:
                    attempts += 1
                    issue_msg = str(e)
                    print(f"\n[!] Exception Caught: {issue_msg}")
                    
                    if attempts == 1:
                        speak("I encountered an error, checking my logs.")
                        log_error_to_history(
                            component="Coordinator",
                            issue=issue_msg,
                            resolution="Retrying execution command.",
                            insight="Unexpected exception during intent routing."
                        )
                    else:
                        speak("The error persists. I am cancelling this task.")
                        log_error_to_history(
                            component="Coordinator",
                            issue=issue_msg,
                            resolution="Gave up after 2 attempts.",
                            insight="Fatal exception requiring manual debugging."
                        )
                        
    except KeyboardInterrupt:
        # Keyboard interrupt handler
        speak("Edith shutting down")
        print("\n[Shutting down Coordinator safely...]")

if __name__ == "__main__":
    main()
