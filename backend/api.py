# api.py

from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import main  # MT5 logic

app = Flask(__name__)
CORS(app)

bot_thread = None
bot_running = False

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"running": bot_running})

@app.route("/start", methods=["POST"])
def start_bot():
    global bot_thread, bot_running
    if not bot_running:
        def run_bot():
            global bot_running
            bot_running = True
            try:
                main.run_strategy()
            finally:
                bot_running = False

        bot_thread = threading.Thread(target=run_bot)
        bot_thread.start()
        return jsonify({"message": "Bot started"})
    else:
        return jsonify({"message": "Bot already running"})

@app.route("/stop", methods=["POST"])
def stop_bot():
    global bot_running
    bot_running = False
    main.stop_strategy()
    return jsonify({"message": "Stop signal sent"})

if __name__ == "__main__":
    app.run(port=5000)
