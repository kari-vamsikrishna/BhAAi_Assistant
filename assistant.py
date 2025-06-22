from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
import datetime
import pyjokes
import sys
from groq import Groq
from dotenv import load_dotenv
import os
import platform
import webbrowser

# Determine if running locally on Windows (for optional speech)
is_local = platform.system() == "Windows"

load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Optional local-only TTS
def talk(text):
    print("\n🎙️ GIRI:", text)
    if is_local:
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 170)
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[1].id)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print("TTS Error:", e)

# Voice input (only for /giri/voice route)
def take_command():
    listener = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎧 Listening...")
        listener.adjust_for_ambient_noise(source)
        voice = listener.listen(source)
    try:
        command = listener.recognize_google(voice).lower()
        print("🗣️ You said:", command)
        return command
    except sr.UnknownValueError:
        return "Sorry bro, I didn’t catch that."
    except sr.RequestError:
        return "Network issue with Google service."

# Ask Groq LLM
def ask_groq(prompt):
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant named GIRI."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Groq API error:", e)
        return "Sorry, I couldn't get a response from Groq."

# Command handling logic
def process_command(command):
    command = command.lower().strip()

    if "play" in command:
            topic = command.replace("play", "").strip()
            url = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"
    
            if platform.system() == "Windows" or platform.system() == "Darwin":  # Darwin = macOS
                webbrowser.open(url)
                return f"Opening YouTube for: {topic} 🎶"
            else:
                return f"You can watch {topic} here: {url}"

    elif "time" in command:
        return f"It’s {datetime.datetime.now().strftime('%I:%M %p')} ⏰"

    elif "joke" in command:
        return pyjokes.get_joke()

    elif "open chrome" in command:
        path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        if os.path.exists(path):
            os.startfile(path)
            return "Opening Chrome 🚀"
        return "Chrome path not found 😬"

    elif "open code" in command:
        os.system("code")
        return "Opening VS Code 💻"

    elif any(word in command for word in ["exit", "stop", "bye"]):
        return "Okay bro, see you later 👋"

    else:
        return ask_groq(command)

# Homepage route
@app.route("/")
def index():
    return render_template("index.html")

# Handle text command from UI
@app.route("/giri/text", methods=["POST"])
def giri_text():
    data = request.json
    command = data.get("command", "")
    if not command:
        return jsonify({"error": "No command provided"}), 400
    response = process_command(command)
    return jsonify({"response": response})

# Handle voice (mic) command
@app.route("/giri/voice", methods=["GET"])
def giri_voice():
    command = take_command()
    response = process_command(command)
    return jsonify({
        "heard": command,
        "response": response
    })

# Entry point
if __name__ == "__main__":
    print("🚀 GIRI Flask assistant running!")
    if is_local:
        talk("Yo! I'm GIRI – now running as a Flask web assistant 💡")
    app.run(debug=True, port=5000)
