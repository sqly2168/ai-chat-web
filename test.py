import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

@app.route("/")
def index():
    return """
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script>
        const socket = io();
        socket.on("test", data => {
            document.body.innerHTML += "<p>" + data.msg + "</p>";
        });
    </script>
    <body></body>
    """

def background():
    time.sleep(3)
    while True:
        socketio.emit("test", {"msg": "hello a threadből"})
        time.sleep(2)

threading.Thread(target=background, daemon=True).start()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
