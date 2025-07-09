from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from frontend

# Hardcoded credentials and redirect URL
VALID_USERNAME = "admin"
VALID_PASSWORD = "2025"
DASHBOARD_URL = "http://coffee1.prudex.net/ui/#!/0?socketid=qGlusxSlu8VwRw7rAAAN"

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username == VALID_USERNAME and password == VALID_PASSWORD:
        return jsonify({"success": True, "dashboard_url": DASHBOARD_URL})
    else:
        return jsonify({"success": False}), 401

@app.route('/update_credentials', methods=['POST'])
def update_credentials():
    data = request.get_json()
    old_username = data.get("old_username")
    old_password = data.get("old_password")
    new_username = data.get("new_username")
    new_password = data.get("new_password")

    if old_username == VALID_USERNAME and old_password == VALID_PASSWORD:
        return jsonify({"success": False, "message": "Static credentials cannot be changed in this mode"}), 400
    else:
        return jsonify({"success": False, "message": "Invalid old credentials"}), 401

@app.route('/')
def home():
    return "Backend is working."

# ✅ Add this route to test backend status
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "connected"})


