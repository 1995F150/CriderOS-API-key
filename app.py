from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Load API keys from JSON file
def load_keys():
    try:
        with open("api_keys.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

@app.route("/verify-key", methods=["POST"])
def verify_key():
    data = request.json
    user_key = data.get("key")

    keys = load_keys()
    if user_key in keys:
        return jsonify({"valid": True})
    else:
        return jsonify({"valid": False}), 401

# Deployment-safe run block
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
