from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
import datetime
import pyjokes
import os
import platform
import webbrowser
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder="templates")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

def process_command(command):
    command = command.lower().strip()

    if "play" in command:
        topic = command.replace("play", "").strip()
        url = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}"
        if platform.system() in ["Windows", "Darwin"]:  # Darwin = macOS
            try:
                webbrowser.open(url)
            except:
                pass
        return f"You can watch {topic} here: {url}"

    elif "time" in command:
        return f"It’s {datetime.datetime.now().strftime('%I:%M %p')} ⏰"

    elif "joke" in command:
        return pyjokes.get_joke()


    elif any(word in command for word in ["exit", "stop", "bye"]):
        return "Okay bro, see you later 👋"

    else:
        return ask_groq(command)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/giri/text", methods=["POST"])
def giri_text():
    data = request.json
    command = data.get("command", "")
    if not command:
        return jsonify({"error": "No command provided"}), 400
    response = process_command(command)
    return jsonify({"response": response})

@app.route("/giri/voice", methods=["GET"])
def giri_voice():
    # Only for local use
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎧 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        voice = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(voice).lower()
        print("🗣️ You said:", command)
    except:
        command = "Sorry, could not understand."
    response = process_command(command)
    return jsonify({
        "heard": command,
        "response": response
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
