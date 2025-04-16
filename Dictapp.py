import os
import webbrowser
import pyautogui
import pyttsx3
from time import sleep

# Initialize the text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(audio):
    """Convert text to speech."""
    engine.say(audio)
    engine.runAndWait()

dictapp = {
    "command prompt": "cmd",
    "paint": "mspaint",
    "word": "winword",
    "excel": "excel",
    "chrome": "chrome",
    "vs code": "code",
    "powerpoint": "powerpnt",
    "calendar": "outlookcal:",
    "notepad": "notepad",
    "settings": "ms-settings:",
    "camera": "microsoft.windows.camera:",
    "file explorer": "explorer",
    "calculator": "calc",
    "task manager": "taskmgr",
    "control panel": "control"
}

def openappweb(query):
    """Launch application or website based on the query."""
    #speak("Launching, sir")
    query = query.replace("open", "").replace("launch", "").replace("jarvis", "").strip()
    speak("Launching, sir")
    # Check if query is a URL and open in browser
    if any(ext in query for ext in [".com", ".co.in", ".org", ".net"]):
        web_url = query if query.startswith("http") else f"https://{query}"
        webbrowser.open(web_url)
    else:
        # Open application from dictapp if keyword matches
        for app in dictapp:
            if app in query:
                os.system(f"start {dictapp[app]}")
                return
        speak("Application not found")

def closeappweb(query):
    """Close specific application or web tabs based on the query."""
    speak("Closing, sir")

    # Close specific number of tabs based on the query
    if "tab" in query:
        try:
            num_tabs = int(query.split()[0])  # Extracts the number of tabs to close
            for _ in range(num_tabs):
                pyautogui.hotkey("ctrl", "w")
                sleep(0.5)
            speak(f"Closed {num_tabs} tab(s)")
        except (ValueError, IndexError):
            speak("Could not determine the number of tabs to close")
    else:
        # Close application if in dictapp
        for app in dictapp:
            if app in query:
                try:
                    os.system(f"taskkill /f /im {dictapp[app]}.exe")
                    speak(f"{app} closed")
                    return
                except Exception as e:
                    speak("Error closing the application")
                    print(f"Error: {e}")
                    return
        speak("Application not found")