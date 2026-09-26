# code from https://fastapi.tiangolo.com/advanced/templates
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException
import requests
import json
import time
import os
import dotenv
app = FastAPI()

dotenv.load_dotenv()


templates = Jinja2Templates(directory="templates")

def sessions():
    try:
        with open("sessions.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

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

def newsession(data):
    with open("sessions.json", "w") as f:
        json.dump(data, f)

def update_slack_message(response_url, text):
    try:
        requests.post(
            response_url,
            json={"replace_original": True, "text": text},
            timeout=10,
        )
    except requests.RequestException as e:
        print(f"Slack update error: {e}")

@app.get("/verify/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    data = sessions()
    session = data.get(id)
    if session is None:
        raise HTTPException(404, "session not found")
    if time.time() > session["expires_at"] and not session["verified"]:
        raise HTTPException(410, "expired session")
    return templates.TemplateResponse(request=request, name="index.html", context={"id": id})

@app.post("/verify/{id}")
async def verify(id: str, request: Request):
    body = await request.json()
    token = body.get("token")
    data = sessions()
    session = data.get(id)

    if session is None:
        raise HTTPException(404, "session not found")
    if session["verified"]:
        return {"success": True}
    if time.time() > session["expires_at"]:
        raise HTTPException(410, "expired session")
    if not token:
        raise HTTPException(400, "missing token")

    result = validate_turnstile(token, os.environ["TURNSTILE_SECRET"])

    if result.get("success"):
        session["verified"] = True
        newsession(data)
        if session.get("response_url"):
         try:
             requests.post(
                 session["response_url"],
                 json={"replace_original": True, "text": "Yes! You are a human"},
                 timeout=10,
             )
         except requests.RequestException as e:
             print(f"Slack update error: {e}")
        return {"success": True}
    raise HTTPException(401, "verification failed")
