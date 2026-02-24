from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os

app = Flask(__name__)

MODEL_PATH = "/home/sqly/Llama/models/google_gemma-3-12b-it-Q4_K_M.gguf"
LLAMA_BIN = "/home/sqly/Llama/llama.cpp/build/bin/llama-simple-chat"

@app.route("/")
def index():
    return send_from_directory(os.getcwd(), "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    try:
        result = subprocess.run(
            [LLAMA_BIN, "-m", MODEL_PATH],
            input=user_message.encode("utf-8"),
            capture_output=True,
            #timeout=120
        )
        response = result.stdout.decode("utf-8").strip()
    except subprocess.TimeoutExpired:
        response = "Timeout."
    except Exception as e:
        response = f"Hiba: {str(e)}"

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)