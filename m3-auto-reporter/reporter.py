from __future__ import annotations
import os, datetime as dt, pandas as pd, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT   = os.getenv("VERTEX_PROJECT")
LOCATION  = os.getenv("VERTEX_LOCATION", "us-central1")
SLACK_URL = os.getenv("SLACK_WEBHOOK")
LOCAL_CSV = os.getenv("CSV_PATH", "m3-auto-reporter/data/events.csv")

import vertexai
from vertexai.generative_models import GenerativeModel
vertexai.init(project=PROJECT, location=LOCATION)
MODEL = GenerativeModel("gemini-2.5-pro")

def fetch_events() -> pd.DataFrame:
    """Берём данные из BigQuery ИЛИ из локального CSV (для демо)."""
    if os.getenv("USE_BIGQUERY"):
        from google.cloud import bigquery
        client = bigquery.Client(project=PROJECT)
        yesterday = (dt.date.today() - dt.timedelta(days=1)).isoformat()
        sql = f"""
          SELECT user_id,event_name,created_at
          FROM  `my_ds.events`
          WHERE DATE(created_at) = '{yesterday}'
          LIMIT 500
        """
        return client.query(sql).to_dataframe()
    else:
        return pd.read_csv(LOCAL_CSV)

def build_prompt(df: pd.DataFrame) -> str:
    top = df.head(20).to_markdown(index=False)
    tpl = Path(__file__).with_name("prompts").joinpath("daily_summary.jinja").read_text()
    return tpl.format(n=len(df), table=top)

def generate_summary(prompt: str) -> str:
    chat = MODEL.start_chat()
    return chat.send_message(prompt).text.strip()

def send_to_slack(text: str):
    if not SLACK_URL:
        print("=== SUMMARY ===\n", text)
    else:
        resp = requests.post(SLACK_URL, json={"text": text})
        resp.raise_for_status()

def main() -> None:
    events  = fetch_events()
    prompt  = build_prompt(events)
    summary = generate_summary(prompt)
    send_to_slack(summary)

if __name__ == "__main__":
    main()