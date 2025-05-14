# api.py
from flask import Flask, jsonify, redirect
from flask_cors import CORS
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()  # загружаем BOT_TOKEN из .env

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

BOT_TOKEN = os.getenv("BOT_TOKEN")

@app.route('/tracks')
def get_tracks():
    path = os.path.join(os.path.dirname(__file__), "data.json")
    if not os.path.exists(path):
        return jsonify({"tracks": [], "error": "data.json not found"}), 404
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/audio/<file_id>')
def get_audio(file_id):
    r = requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}",
        timeout=5
    )
    rj = r.json()
    if not rj.get("ok"):
        return jsonify({"error": "File not found"}), 404
    file_path = rj["result"]["file_path"]
    return redirect(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}")

@app.route('/cover/<file_id>')
def get_cover(file_id):
    r = requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}",
        timeout=5
    )
    rj = r.json()
    if not rj.get("ok"):
        return jsonify({"error": "File not found"}), 404
    file_path = rj["result"]["file_path"]
    return redirect(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}")

if __name__ == '__main__':
    # для локального теста можно оставить 0.0.0.0
    app.run(host='0.0.0.0', port=5050)
