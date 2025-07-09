from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

CREDENTIALS_FILE = '/home/Prudexbackend/prudex/test/credentials.json'

# Initialize credentials file if not exists
if not os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump({
            "username": "admin",
            "password": "2025",
            "dashboard_url": "http://coffee1.prudex.net/ui/#!/0?socketid=qGlusxSlu8VwRw7rAAAN"
        }, f)

def load_credentials():
    with open(CREDENTIALS_FILE, 'r') as f:
        return json.load(f)

def save_credentials(data):
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    creds = load_credentials()
    if username == creds["username"] and password == creds["password"]:
        return jsonify({"success": True, "dashboard_url": creds["dashboard_url"]})
    else:
        return jsonify({"success": False}), 401

@app.route('/update_credentials', methods=['POST'])
def update_credentials():
    data = request.get_json()
    old_username = data.get("old_username")
    old_password = data.get("old_password")
    new_username = data.get("new_username")
    new_password = data.get("new_password")

    creds = load_credentials()
    if old_username == creds["username"] and old_password == creds["password"]:
        creds["username"] = new_username
        creds["password"] = new_password
        save_credentials(creds)
        return jsonify({"success": True, "message": "Credentials updated successfully"})
    else:
        return jsonify({"success": False, "message": "Invalid old credentials"}), 401

@app.route('/')
def home():
    return "Backend is working."

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "connected"})
