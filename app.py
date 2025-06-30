import stripe
import json
from flask import Flask, request, jsonify

# Load API key from file
with open("api_keys.json") as f:
    keys = json.load(f)

stripe.api_key = keys["stripe_secret_key"]

app = Flask(__name__)

@app.route("/verify-key", methods=["POST"])
def verify_key():
    try:
        balance = stripe.Balance.retrieve()
        return jsonify({"status": "success", "balance": balance})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 403

if __name__ == "__main__":
    app.run(debug=True)
