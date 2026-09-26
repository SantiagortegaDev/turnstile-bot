# code from https://developers.cloudflare.com/turnstile/get-started/server-side-validation/
import requests
import dotenv
from flask import Flask, request, jsonify
dotenv.load_dotenv()
import os

app = Flask(__name__)

def validate_turnstile(token, secret, remoteip=None):
    url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'

    data = {
        'secret': secret,
        'response': token
    }

    if remoteip:
        data['remoteip'] = remoteip

    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Turnstile validation error: {e}")
        return {'success': False, 'error-codes': ['internal-error']}


@app.route("/verify", methods=["POST"])
def verify():
    body = request.get_json(silent=True) or {}
    token = body.get("token")

    if not token:
        return jsonify({"success": False, "error-codes": ["missing-input-response"]}), 400

    result = validate_turnstile(
        token=token,
        secret=os.environ["TURNSTILE_SECRET"],
        remoteip=request.headers.get("CF-Connecting-IP", request.remote_addr)
    )

    status_code = 200 if result.get("success") else 401
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)