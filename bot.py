import os
import time

import dotenv 
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import json
import uuid


dotenv.load_dotenv()

app = App(
    token=os.environ["SLACK_BOT_TOKEN"]
)


@app.command("/turnstile-bot-ping")
def ping(command, ack, respond):
    start = time.time()
    ack()
    latency = int((time.time() - start) * 1000)
    respond(text=f"Pong!\nLatency: {latency}ms")


@app.command("/turnstile-bot-help")
def help_command(ack, respond):
    ack()
    respond(
        text=(
            "Available Commands:\n"
            "/turnstile-bot-ping - Check bot latency\n"
            "/turnstile-bot-status - Check if you have been verified with turnstile\n"
            "/turnstile-bot-verify - Verify you with turnstile\n"
            "/turnstile-bot-help - Show this help message"
        )
    )


@app.command("/turnstile-bot-status")
def status(command, ack, respond):
    #With ai
    ack()
    verified = any(
        s["slack_user_id"] == command["user_id"] and s["verified"]
        for s in sessions().values()
    )
    respond(text="Verified" if verified else "Not verified")


def sessions():
    try:
        with open("sessions.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def newsession(data):
    with open("sessions.json", "w") as f:
        json.dump(data, f)


@app.command("/turnstile-bot-verify")
def verify_command(ack, respond, command):
    ack()
    sessions2 = sessions()
    sessionid = str(uuid.uuid4())
    sessions2[sessionid] = {"slack_user_id": command["user_id"], "expires_at": time.time() + 600, "verified": False, "response_url": command["response_url"],}
    newsession(sessions2)
    respond(text=f"Verify link: {os.environ['URL']}/verify/{sessionid}")



SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
print("bot is running!")