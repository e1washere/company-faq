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

## How it works
1. `reporter.py` runs a parametrised SQL query against BigQuery using the **BigQuery Python client**.
2. Formats the result via a Jinja template (see `prompts/`).
3. Sends the rendered message to Slack via Incoming Webhook.

Run manually or via cron / Cloud Scheduler.

## Run once a day via cron
```
0 8 * * * cd /opt/company-faq/m3-auto-reporter && /usr/bin/python reporter.py --days 1 >> /var/log/auto_reporter.log 2>&1
```

![report screenshot](../../docs/m3_report.png)
