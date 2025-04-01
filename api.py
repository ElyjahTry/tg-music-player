from flask import Flask, jsonify, redirect
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

# Используй тот же токен, что и в боте
BOT_TOKEN = "7653784788:AAHeNQqdYB95aeuGCcVmHl_ytTsRvFvzkk8"

@app.route('/tracks')
def get_tracks():
    path = os.path.join(os.path.dirname(__file__), "data.json")
    if not os.path.exists(path):
        return jsonify({"tracks": [], "error": "data.json not found"}), 404
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"tracks": [], "error": str(e)}), 500

@app.route('/audio/<file_id>')
def get_audio(file_id):
    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}")
    result = response.json()
    if not result.get("ok"):
        return jsonify({"error": "File not found"}), 404
    file_path = result["result"]["file_path"]
    return redirect(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}")

@app.route('/cover/<file_id>')
def get_cover(file_id):
    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}")
    result = response.json()
    if not result.get("ok"):
        return jsonify({"error": "File not found"}), 404
    file_path = result["result"]["file_path"]
    return redirect(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5050)
