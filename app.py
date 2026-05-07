import requests
import json
import os
from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")


LLAMA_SERVER_URL = "http://127.0.0.1:8080/completion"

#chat history - resets when the model is reloaded
chat_history = {}

def build_prompt(history):
    system_prompt = (
        "You are a cool, funny uncle who loves to give advice to the user. "
        "Answer with humor and do not repeat yourself."
    )

    prompt = f"<start_of_turn>system\n{system_prompt}<end_of_turn>\n"

    for msg in history:
        role = msg["role"]
        content = msg["content"]

        if role == "user":
            prompt += f"<start_of_turn>user\n{content}<end_of_turn>\n"
        elif role == "assistant":
            prompt += f"<start_of_turn>model\n{content}<end_of_turn>\n"

    prompt += "<start_of_turn>model\n"
    return prompt

@app.route("/")
def index():
    return send_from_directory(os.getcwd(), "index.html")

@socketio.on("user_message")
def handle_message(data):
    sid = request.sid
    user_input = data.get("message", "").strip()

    if not user_input:
        return

    if sid not in chat_history:
        chat_history[sid] = []

    chat_history[sid].append({
        "role": "user",
        "content": user_input
    })

    prompt = build_prompt(chat_history[sid])

    payload = {
        "prompt": prompt,
        "stream": True,
        "n_predict": 1024,
        "stop": ["<end_of_turn>", "<eos>", "user:"]
    }

    def stream_to_web():
        full_response = ""

        try:
            r = requests.post(LLAMA_SERVER_URL, json=payload, stream=True, timeout=120)

            for line in r.iter_lines():
                if line:
                    line_str = line.decode("utf-8")

                    if line_str.startswith("data: "):
                        content_json = json.loads(line_str[6:])
                        token = content_json.get("content", "")

                        if token:
                            full_response += token
                            socketio.emit("model_response", {"token": token}, room=sid)

                        if content_json.get("stop"):
                            break

            # assistant answer save to history
            chat_history[sid].append({
                "role": "assistant",
                "content": full_response
            })

            socketio.emit("model_done", {}, room=sid)

        except Exception as e:
            print(f"Hiba a streaming közben: {e}")
            socketio.emit("model_response", {"token": f"\n[Hiba: {e}]\n"}, room=sid)
            socketio.emit("model_done", {}, room=sid)

    socketio.start_background_task(stream_to_web)


@app.route("/clear", methods=["POST"])
def clear_chat():
    sid = request.json.get("sid", "")
    if sid in chat_history:
        chat_history[sid] = []
    return {"status": "cleared"}

if __name__ == "__main__":
    # http://ipv4:5000/
    socketio.run(app, host="0.0.0.0", port=5000)
