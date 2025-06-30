from flask import Flask, request, jsonify, send_file
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

# New route to deliver key file based on plan name
@app.route("/success")
def success():
    plan = request.args.get('keypack', 'basic')  # e.g. 'basic', 'pro', etc.
    filename = f'keys/{plan}_key.txt'

    if os.path.exists(filename):
        return send_file(filename, as_attachment=True)
    else:
        return jsonify({"error": "Key file not found"}), 404

# Deployment-safe run block
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
