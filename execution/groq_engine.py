import os
from dotenv import load_dotenv

load_dotenv()

# OWNER: Intent parsing — uses Groq (Llama 3.1 8B) to classify what the user wants to DO (open/close/search/question).
# Called by executor.py on EVERY command. NOT used for answering questions or web search.

class GroqEngine:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            print("[GroqEngine] Groq initialized successfully.")
        else:
            print("[GroqEngine] Warning: GROQ_API_KEY not found in .env")
            self.client = None

    def get_intent(self, text):
        """Uses Groq (Llama) to parse intent, target, and parameters from a natural language command."""
        if not self.client:
            return None

        prompt = f"""
Analyze the following user command for a voice assistant named Edith:
"{text}"

Return a JSON object with:
- "intent": The primary action (open, search, close, question, automate)
- "type": The target category (website, application, information, task)
- "target": The specific name of the site or app
- "parameters": Any extra search terms or details

Examples:
"open youtube" -> {{"intent": "open", "type": "website", "target": "youtube", "parameters": ""}}
"search for quantum physics" -> {{"intent": "search", "type": "information", "target": "google", "parameters": "quantum physics"}}
"what is the capital of France" -> {{"intent": "question", "type": "information", "target": "france capital", "parameters": ""}}

Only return the JSON, no markdown.
"""

        try:
            chat_completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            response_text = chat_completion.choices[0].message.content

            import json
            import re
            clean_json = re.sub(r'```json|```', '', response_text).strip()
            return json.loads(clean_json)
        except Exception as e:
            print(f"[GroqEngine] Error getting intent: {e}")
            return None

groq_engine = GroqEngine()
