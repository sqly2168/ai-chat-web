import requests
import json
import os
from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO

app = Flask(__name__)
# Az eventlet kell a streaminghez, de a sima is jó lehet
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# Ez a cím a llama-servered címe
LLAMA_SERVER_URL = "http://127.0.0.1:8080/completion"

@app.route("/")
def index():
    return send_from_directory(os.getcwd(), "index.html")

@socketio.on("user_message")
def handle_message(data):
    sid = request.sid
    user_input = data.get("message", "")

    # A Gemma 3 speciális prompt formátuma (amit a logodban is láttunk)
    prompt = f"<start_of_turn>user\n{user_input}<end_of_turn>\n<start_of_turn>model\n"

    payload = {
        "prompt": prompt,
        "stream": True,
        "n_predict": 1024,
        "stop": ["<end_of_turn>", "<eos>", "user:"]
    }

    def stream_to_web():
        try:
            # stream=True, hogy ne várja meg a végét, hanem jöjjenek a tokenek
            r = requests.post(LLAMA_SERVER_URL, json=payload, stream=True, timeout=120)
            
            for line in r.iter_lines():
                if line:
                    # A llama-server "data: {...}" formátumban küldi a választ
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data: "):
                        content_json = json.loads(line_str[6:])
                        token = content_json.get("content", "")
                        
                        if token:
                            socketio.emit("model_response", {"token": token}, room=sid)
                        
                        if content_json.get("stop"):
                            break
            
            socketio.emit("model_done", {}, room=sid)
        except Exception as e:
            print(f"Hiba a streaming közben: {e}")
            socketio.emit("model_response", {"token": f"\n[Hiba: {e}]\n"}, room=sid)
            socketio.emit("model_done", {}, room=sid)

    socketio.start_background_task(stream_to_web)

if __name__ == "__main__":
    # Itt a port 5000, amin a böngészőben eléred
    socketio.run(app, host="0.0.0.0", port=5000)