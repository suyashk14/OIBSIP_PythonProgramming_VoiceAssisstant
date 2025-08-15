import tkinter as tk
from tkinter import scrolledtext
import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import threading
import wikipedia
import requests
import os
import json
import random

CHAT_HISTORY_FILE = "chat_history.json"

engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    chat_log.insert(tk.END, f"Assistant: {text}\n", "assistant")
    chat_log.yview(tk.END)
    engine.say(text)
    engine.runAndWait()
    save_chat("Assistant", text)

recognizer = sr.Recognizer()

def listen():
    with sr.Microphone() as source:
        speak("Listening...")
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio).lower()
        chat_log.insert(tk.END, f"You: {query}\n", "user")
        chat_log.yview(tk.END)
        save_chat("You", query)
        process_command(query)
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
    except sr.RequestError:
        speak("Speech recognition service unavailable.")

def save_chat(sender, message):
    history = []
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as f:
            history = json.load(f)
    history.append({"sender": sender, "message": message})
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def load_chat():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, "r") as f:
            history = json.load(f)
        for entry in history:
            tag = "user" if entry["sender"] == "You" else "assistant"
            chat_log.insert(tk.END, f"{entry['sender']}: {entry['message']}\n", tag)

def process_command(query):
    if any(greet in query for greet in ["hello", "hi", "hey"]):
        speak("Hello! How can I assist you?")
    elif "time" in query:
        speak(f"The time is {datetime.datetime.now().strftime('%H:%M')}")
    elif "date" in query:
        speak(f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}")
    elif "search" in query:
        search_term = query.replace("search", "").strip()
        if search_term:
            speak(f"Searching for {search_term}")
            webbrowser.open(f"https://www.google.com/search?q={search_term}")
        else:
            speak("What should I search for?")
    elif "wikipedia" in query:
        topic = query.replace("wikipedia", "").strip()
        if topic:
            try:
                summary = wikipedia.summary(topic, sentences=2)
                speak(summary)
            except wikipedia.exceptions.DisambiguationError:
                speak("That topic has multiple meanings, please be more specific.")
            except wikipedia.exceptions.PageError:
                speak("Sorry, I couldn't find information on that.")
        else:
            speak("Please provide a topic to search on Wikipedia.")
    elif "weather" in query:
        speak("Fetching weather... Please tell me your city in the format 'weather in cityname'.")
        if "weather in" in query:
            city = query.split("weather in")[-1].strip()
            get_weather(city)
    elif "joke" in query:
        jokes = [
            "Why did the computer go to the doctor? Because it caught a virus!",
            "Why do Java developers wear glasses? Because they don't see sharp!",
            "I told my computer I needed a break, and now it won't stop sending me KitKat ads."
        ]
        speak(random.choice(jokes))
    elif "exit" in query or "quit" in query:
        speak("Goodbye!")
        root.quit()
    else:
        speak("I am not sure how to respond to that yet.")

def get_weather(city):
    api_key = "YOUR_OPENWEATHERMAP_API_KEY"
    if not api_key or api_key == "YOUR_OPENWEATHERMAP_API_KEY":
        speak("Weather API key not set.")
        return
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        data = requests.get(url).json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            speak(f"The temperature in {city} is {temp}°C with {desc}.")
        else:
            speak("City not found.")
    except Exception as e:
        speak("Could not fetch weather right now.")

def start_listening():
    threading.Thread(target=listen).start()

def send_text():
    query = entry.get().strip()
    if query:
        chat_log.insert(tk.END, f"You: {query}\n", "user")
        chat_log.yview(tk.END)
        save_chat("You", query)
        process_command(query.lower())
        entry.delete(0, tk.END)

root = tk.Tk()
root.title("Intermediate Voice Assistant")
root.geometry("500x550")

chat_log = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='normal')
chat_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
chat_log.tag_config("user", foreground="blue")
chat_log.tag_config("assistant", foreground="green")

frame = tk.Frame(root)
frame.pack(pady=5)

entry = tk.Entry(frame, width=40)
entry.pack(side=tk.LEFT, padx=5)

send_btn = tk.Button(frame, text="Send", command=send_text)
send_btn.pack(side=tk.LEFT, padx=5)

voice_btn = tk.Button(root, text="🎤 Speak", command=start_listening)
voice_btn.pack(pady=5)

load_chat()
root.mainloop()
