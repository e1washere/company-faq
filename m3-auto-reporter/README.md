# Auto-Reporter Agent (M3)

Periodically queries BigQuery, summarises results and posts to Slack.

## Setup
```bash
pip install -r requirements.txt
export GOOGLE_APPLICATION_CREDENTIALS=$HOME/keys/sa.json
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/…
python reporter.py --days 1
```

Expected: *"Report posted to #data-ops"* appears in console and Slack.
