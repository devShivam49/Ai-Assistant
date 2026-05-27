import webbrowser, urllib.parse
from core.speak import speak

def search_google(query: str):
    if not query: speak("What should I search?"); return
    speak(f"Searching for {query}")
    webbrowser.open("https://google.com/search?q=" + urllib.parse.quote(query))

def search_youtube(query: str):
    if not query: open_youtube(); return
    speak(f"Searching YouTube for {query}")
    webbrowser.open("https://youtube.com/results?search_query=" + urllib.parse.quote(query))