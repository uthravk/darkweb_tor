# alerting/notifier.py
import os, requests, json
from dotenv import load_dotenv
load_dotenv()

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL","")

def send_slack(alert):
    if not SLACK_WEBHOOK:
        print("Slack webhook not configured. Alert:", alert)
        return False
    payload = {"text": json.dumps(alert, indent=2)}
    r = requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
    return r.status_code == 200
