from flask import Flask, request, jsonify, render_template
import datetime
import pyjokes
import os
import requests
from dotenv import load_dotenv
from groq import Groq

# Load .env variables
load_dotenv()

app = Flask(__name__, template_folder="templates")

# Initialize API clients
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def ask_groq(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful assistant named GIRI."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Groq API error:", e)
        return "Sorry, I couldn't get a response from Groq."

def get_youtube_video_id(query):
    try:
        url = (
            f"https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&type=video&maxResults=1&q={query}&key={YOUTUBE_API_KEY}"
        )
        response = requests.get(url)
        data = response.json()
        if "items" in data and data["items"]:
            return data["items"][0]["id"]["videoId"]
    except Exception as e:
        print("YouTube API error:", e)
    return None

def process_command(command):
    command = command.lower().strip()

    if "play" in command:
        topic = command.replace("play", "").strip()
        video_id = get_youtube_video_id(topic)
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
        else:
            return "Sorry, I couldn’t find a video for that."

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
    data = request.get_json()
    command = data.get("command", "")
    if not command:
        return jsonify({"response": "No command received."})

    response = process_command(command)
    return jsonify({"response": response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
