from flask import Flask, request, jsonify
import stripe
import uuid
import json
import os

app = Flask(__name__)

# === Stripe Config ===
stripe.api_key = 'sk_test_your_secret_here'  # Replace with your Stripe Secret Key
endpoint_secret = 'whsec_your_webhook_secret'  # Replace with your Webhook Secret

KEYS_FILE = 'api_keys.json'

# Load existing or create new key store
if os.path.exists(KEYS_FILE):
    with open(KEYS_FILE, 'r') as f:
        api_keys = json.load(f)
else:
    api_keys = {}

def save_keys():
    with open(KEYS_FILE, 'w') as f:
        json.dump(api_keys, f, indent=2)

@app.route('/generate-key', methods=['POST'])
def generate_key():
    name = request.json.get('name', 'anonymous')
    max_uses = request.json.get('max_uses', 5)
    new_key = str(uuid.uuid4())
    api_keys[new_key] = {
        'name': name,
        'usage_count': 0,
        'max_uses': max_uses,
        'active': True
    }
    save_keys()
    return jsonify({'api_key': new_key, 'max_uses': max_uses})

@app.route('/verify-key', methods=['POST'])
def verify_key():
    key = request.json.get('api_key')
    key_data = api_keys.get(key)

    if not key_data or not key_data['active']:
        return jsonify({'valid': False, 'message': 'Invalid or inactive key'}), 403

    if key_data['usage_count'] >= key_data['max_uses']:
        return jsonify({'valid': False, 'message': 'Key usage limit reached'}), 403

    api_keys[key]['usage_count'] += 1
    save_keys()
    return jsonify({'valid': True, 'message': 'Key accepted'})

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_email = session.get('customer_email', 'unknown')
        new_key = str(uuid.uuid4())
        api_keys[new_key] = {
            'name': customer_email,
            'usage_count': 0,
            'max_uses': 5,
            'active': True
        }
        save_keys()
        print(f"[✅] API Key for {customer_email}: {new_key}")

    return '', 200

@app.route('/list-keys', methods=['GET'])
def list_keys():
    return jsonify(api_keys)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)