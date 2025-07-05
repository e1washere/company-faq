import os, sys, json, requests
from dotenv import load_dotenv

load_dotenv()

WEBHOOK = os.getenv("SLACK_WEBHOOK")
if not WEBHOOK:
    sys.exit("SLACK_WEBHOOK env var not set")

def send(text: str, channel: str | None = None):
    payload = {"text": text}
    if channel:
        payload["channel"] = channel

    r = requests.post(WEBHOOK, json=payload, timeout=10)
    r.raise_for_status()
    return r.text

if __name__ == "__main__":
    msg = "Auto-reporter test – everything works!"
    print(send(msg))