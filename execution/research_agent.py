import glob
import json
import os
import re
import time
import datetime
import urllib.parse
import requests
from bs4 import BeautifulSoup
import schedule
import google.generativeai as genai
from dotenv import load_dotenv

from execution.voice_engine import speak
from execution.logger import log_error, log_info

# Load environment variables
load_dotenv()

SCRAPING_API_KEY = os.getenv("SCRAPING_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini (replacing OpenAI per previous instructions)
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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
        log_error("ResearchAgent", error)
        return []
        
    log_info("ResearchAgent", "Scraping search query", query)
    
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
        log_error("ResearchAgent", error, e)
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
    log_info("ResearchAgent", "Starting research and summary", query)
    
    results = scrape_with_api(query)
    
    internal_matches = search_internal_context(query)
    local_context = ""
    if internal_matches:
        local_context = "Internal EDITH context matches:\n"
        for match in internal_matches:
            local_context += f"File: {match['file']}\nSnippet: {match['snippet']}\n\n"

    if not results and not internal_matches:
        return f"I couldn't find any external or internal information for {query}."

    if not GEMINI_API_KEY:
        summary_parts = []
        if internal_matches:
            summary_parts.append("I found some internal EDITH notes and logs relevant to that question:")
            for match in internal_matches:
                summary_parts.append(f"From {match['file']}: {match['snippet']}")
        if results:
            summary_parts.append("I also found these web search snippets:")
            for res in results[:3]:
                summary_parts.append(f"{res['title']}: {res['snippet']} ({res['url']})")
        return "\n".join(summary_parts)
        
    # Format the scraped results for the LLM
    context = ""
    for i, res in enumerate(results, 1):
        context += f"Result {i}:\nTitle: {res['title']}\nSnippet: {res['snippet']}\nURL: {res['url']}\n\n"
        
    prompt = (
        f"You are EDITH, an intelligent assistant. Answer the user's question in a concise, spoken style. "
        f"If internal EDITH documents or logs are relevant, mention that you're using them as a source. "
        f"Include a short summary with 2 or 3 clear points and keep it natural.\n\n"
        f"Question: {query}\n\n"
    )
    if local_context:
        prompt += f"{local_context}\n"
    prompt += f"Search Results:\n{context}"
    
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
        log_error("ResearchAgent", error, e)
        return "I encountered an error while trying to summarise the research."

def search_internal_context(query: str, max_results: int = 3) -> list[dict]:
    """Search EDITH local files for relevant internal context."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    query_lower = query.lower()
    terms = [term for term in re.split(r"\W+", query_lower) if term]
    if not terms:
        return []

    candidate_files = [
        os.path.join(root_dir, "history.md"),
        os.path.join(root_dir, "scratch", "browser_log.txt")
    ]
    candidate_files.extend(glob.glob(os.path.join(root_dir, "planning", "*.md")))
    candidate_files.extend(glob.glob(os.path.join(root_dir, "config", "*.json")))

    matches = []
    for path in candidate_files:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            continue

        content_lower = content.lower()
        score = sum(1 for term in terms if term in content_lower)
        if score == 0:
            continue

        snippet = ""
        for term in terms:
            idx = content_lower.find(term)
            if idx >= 0:
                start = max(0, idx - 80)
                end = min(len(content), idx + 220)
                snippet = content[start:end].replace("\n", " ").strip()
                break

        if not snippet:
            snippet = content[:300].replace("\n", " ").strip()

        matches.append({
            "file": os.path.relpath(path, root_dir),
            "score": score,
            "snippet": snippet
        })

    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches[:max_results]


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
        log_info("ResearchAgent", "Saved research log", f"topic={topic}; file={log_file}")
    except Exception as e:
        log_error("ResearchAgent", f"Failed to save research log for {topic}", e)
        
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
