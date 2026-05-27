import os, webbrowser, subprocess
from datetime import datetime
from core.speak import speak

def open_youtube():   webbrowser.open("https://youtube.com"); speak("Opening YouTube.")
def open_google():    webbrowser.open("https://google.com"); speak("Opening Google.")
def open_chrome():    subprocess.Popen(["start","chrome"], shell=True); speak("Opening Chrome.")
def open_notepad():   subprocess.Popen(["notepad.exe"]); speak("Opening Notepad.")
def open_vscode():    subprocess.Popen(["code"], shell=True); speak("Opening VS Code.")
def open_explorer():  subprocess.Popen(["explorer.exe"]); speak("Opening Explorer.")
def lock_pc():        os.system("rundll32.exe user32.dll,LockWorkStation"); speak("Locking PC.")
def shutdown():       speak("Shutting down!"); os.system("shutdown /s /t 3")
def restart():        speak("Restarting!"); os.system("shutdown /r /t 3")
def volume_up():      os.system("nircmd.exe changesysvolume 5000"); speak("Volume up.")
def volume_down():    os.system("nircmd.exe changesysvolume -5000"); speak("Volume down.")

def tell_time():
    now = datetime.now()
    speak(f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d')}.")