import os
import time
import datetime
import urllib.parse
import requests
from bs4 import BeautifulSoup
import schedule
import google.generativeai as genai
from dotenv import load_dotenv

from execution.voice_engine import speak

# Load environment variables
load_dotenv()

SCRAPING_API_KEY = os.getenv("SCRAPING_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini (replacing OpenAI per previous instructions)
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def log_error_to_history(error_msg: str):
    """Logs errors to history.md in the root directory."""
    history_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "history.md")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(history_path, "a", encoding="utf-8") as f:
        f.write(f"\n- **[ERROR] {timestamp}**: {error_msg}\n")

def scrape_with_api(query: str) -> list[dict]:
    """
    Calls ScraperAPI to proxy a Google search and bypass captchas.
    Parses the top 5 result titles, snippets, and URLs using BeautifulSoup.
    
    Args:
        query (str): The search query.
        
    Returns:
        list[dict]: List of up to 5 dictionaries containing {title, snippet, url}
    """
    if not SCRAPING_API_KEY:
        error = "SCRAPING_API_KEY is not set in .env. Cannot proxy search request."
        print(f"Error: {error}")
        log_error_to_history(error)
        return []
        
    print(f"Scraping Google search for: '{query}' via API...")
    
    google_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    # Standard ScraperAPI endpoint formatting
    api_url = f"http://api.scraperapi.com?api_key={SCRAPING_API_KEY}&url={urllib.parse.quote(google_url)}"
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Google search results are generally wrapped in div tags with class 'g'
        for g in soup.find_all('div', class_='g'):
            if len(results) >= 5:
                break
                
            title_tag = g.find('h3')
            link_tag = g.find('a')
            
            # Google's snippet classes change, VwiC3b is highly common for the text block
            snippet_div = g.find('div', {'style': '-webkit-line-clamp:2'}) or g.find('div', class_='VwiC3b')
            
            if title_tag and link_tag:
                title = title_tag.get_text(strip=True)
                url = link_tag.get('href', '')
                snippet = snippet_div.get_text(strip=True) if snippet_div else "No description available."
                
                if url.startswith('/'):
                    continue  # Skip internal Google links
                    
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "url": url
                })
                
        print(f"Found {len(results)} results via Scraping API.")
        return results

    except Exception as e:
        error = f"Failed to scrape with API for '{query}': {e}"
        print(error)
        log_error_to_history(error)
        return []

def research_and_summarise(query: str) -> str:
    """
    Calls scrape_with_api() to get raw results, formats them, and passes them
    to Gemini to summarise into 3 clear bullet points for a voice response.
    
    Args:
        query (str): The research topic.
        
    Returns:
        str: A summary string ready to be spoken.
    """
    print(f"Starting research and summary for: '{query}'")
    
    results = scrape_with_api(query)
    
    if not results:
        return f"I couldn't find any results for {query}."
        
    if not GEMINI_API_KEY:
        error = "GEMINI_API_KEY is not set in .env. Cannot summarise."
        print(error)
        log_error_to_history(error)
        return "I found results, but my AI summariser is not configured yet."
        
    # Format the scraped results for the LLM
    context = ""
    for i, res in enumerate(results, 1):
        context += f"Result {i}:\nTitle: {res['title']}\nSnippet: {res['snippet']}\nURL: {res['url']}\n\n"
        
    prompt = (
        f"Summarise these search results about '{query}' in 3 clear, concise bullet points "
        f"for a voice assistant response. Make it conversational and easy to listen to.\n\n"
        f"Search Results:\n{context}"
    )
    
    try:
        # Using Gemini instead of OpenAI GPT-3.5 as requested previously
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        summary = response.text.strip()
        
        # Remove markdown symbols for better text-to-speech output
        summary = summary.replace("*", "").replace("#", "")
        
        print(f"Generated Summary:\n{summary}")
        return summary
    except Exception as e:
        error = f"Gemini API summarisation failed for '{query}': {e}"
        print(error)
        log_error_to_history(error)
        return "I encountered an error while trying to summarise the research."

def _run_research_task(topic: str):
    """Internal task runner called automatically by the schedule library."""
    print(f"\n--- Running scheduled research for: {topic} ---")
    summary = research_and_summarise(topic)
    
    # Save the output to scratch/research_log_{topic}_{date}.txt
    date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_topic = "".join(c if c.isalnum() else "_" for c in topic)
    log_file = f"research_log_{safe_topic}_{date_str}.txt"
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scratch", log_file)
    
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"Topic: {topic}\n")
            f.write(f"Date: {date_str}\n\n")
            f.write(summary)
        print(f"Saved research log to: {log_path}")
    except Exception as e:
        log_error_to_history(f"Failed to save research log for {topic}: {e}")
        
    # Speak the summary aloud using pyttsx3
    speak(f"I have a research update on {topic}.")
    speak(summary)
    print("--- Scheduled research complete ---\n")

def timed_research_loop(topic: str, interval_minutes: int):
    """
    Uses the schedule library to run research_and_summarise every N minutes automatically.
    
    Args:
        topic (str): The research query to track.
        interval_minutes (int): How often to run the research (in minutes).
    """
    print(f"Setting up scheduled research for '{topic}' every {interval_minutes} minutes.")
    
    # Schedule the task
    schedule.every(interval_minutes).minutes.do(_run_research_task, topic=topic)
    
    # Run it once immediately so the user doesn't have to wait for the first interval
    _run_research_task(topic)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Stopping timed research loop.")

# Alias for executor compatibility
research_query = research_and_summarise
