from __future__ import annotations

import datetime as dt
import json
import logging
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import vertexai
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT   = os.getenv("VERTEX_PROJECT")
LOCATION  = os.getenv("VERTEX_LOCATION", "us-central1")
SLACK_URL = os.getenv("SLACK_WEBHOOK")
LOCAL_CSV = os.getenv("CSV_PATH", "m3-auto-reporter/data/events.csv")

vertexai.init(project=PROJECT, location=LOCATION)
MODEL = GenerativeModel("gemini-2.5-pro")

def fetch_events() -> pd.DataFrame:
    """Берём данные из BigQuery ИЛИ из локального CSV (для демо)."""
    try:
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
            logger.info(f"Fetching events from BigQuery for {yesterday}")
            return client.query(sql).to_dataframe()
        else:
            logger.info(f"Reading events from CSV: {LOCAL_CSV}")
            return pd.read_csv(LOCAL_CSV)
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        # Return empty DataFrame as fallback
        return pd.DataFrame(columns=['user_id', 'event_name', 'created_at'])

def build_prompt(df: pd.DataFrame) -> str:
    top = df.head(20).to_markdown(index=False)
    tpl = Path(__file__).with_name("prompts").joinpath("daily_summary.jinja").read_text()
    return tpl.format(n=len(df), table=top)

def generate_summary(prompt: str) -> str:
    """Generate summary using Vertex AI Gemini model."""
    try:
        logger.info("Generating summary with Vertex AI")
        chat = MODEL.start_chat()
        response = chat.send_message(prompt).text.strip()
        logger.info("Summary generated successfully")
        return response
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return "Error generating summary. Please check the logs."

def send_to_slack(text: str):
    """Send message to Slack webhook or print to console."""
    try:
        if not SLACK_URL:
            logger.info("No Slack webhook configured, printing to console")
            print("=== SUMMARY ===\n", text)
        else:
            logger.info("Sending report to Slack")
            resp = requests.post(SLACK_URL, json={"text": text})
            resp.raise_for_status()
            logger.info("Report sent to Slack successfully")
    except Exception as e:
        logger.error(f"Error sending to Slack: {e}")
        print("=== SUMMARY (Slack failed) ===\n", text)

def save_report_feedback(report_id: str, feedback: dict):
    """Save report feedback for continuous improvement."""
    try:
        feedback_file = Path("feedback") / f"{report_id}_feedback.json"
        feedback_file.parent.mkdir(exist_ok=True)
        
        with open(feedback_file, 'w') as f:
            json.dump(feedback, f, indent=2)
        logger.info(f"Feedback saved for report {report_id}")
    except Exception as e:
        logger.error(f"Failed to save feedback: {e}")

def analyze_feedback_trends():
    """Analyze feedback trends for report improvement."""
    try:
        feedback_dir = Path("feedback")
        if not feedback_dir.exists():
            return {"message": "No feedback data available"}
        
        feedback_files = list(feedback_dir.glob("*_feedback.json"))
        if not feedback_files:
            return {"message": "No feedback files found"}
        
        # Simple analysis of feedback trends
        ratings = []
        comments = []
        
        for file in feedback_files:
            with open(file, 'r') as f:
                data = json.load(f)
                if 'rating' in data:
                    ratings.append(data['rating'])
                if 'comment' in data:
                    comments.append(data['comment'])
        
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        logger.info(f"Average feedback rating: {avg_rating:.2f}")
        
        return {
            "average_rating": avg_rating,
            "total_feedback": len(feedback_files),
            "recent_comments": comments[-5:] if comments else []
        }
        
    except Exception as e:
        logger.error(f"Error analyzing feedback: {e}")
        return {"error": str(e)}

def main() -> None:
    """Enhanced main function with feedback integration."""
    try:
        # Generate unique report ID
        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Starting report generation: {report_id}")
        
        # Analyze previous feedback for improvements
        feedback_analysis = analyze_feedback_trends()
        logger.info(f"Feedback analysis: {feedback_analysis}")
        
        # Generate report
        events = fetch_events()
        prompt = build_prompt(events)
        summary = generate_summary(prompt)
        
        # Enhanced summary with feedback integration
        if feedback_analysis.get("average_rating", 0) < 3.0:
            summary += "\n\n---\n*Note: This report has been enhanced based on previous feedback.*"
        
        send_to_slack(summary)
        
        # Save report metadata for feedback tracking
        report_metadata = {
            "report_id": report_id,
            "timestamp": datetime.now().isoformat(),
            "events_count": len(events),
            "summary_length": len(summary)
        }
        
        metadata_file = Path("reports") / f"{report_id}_metadata.json"
        metadata_file.parent.mkdir(exist_ok=True)
        with open(metadata_file, 'w') as f:
            json.dump(report_metadata, f, indent=2)
        
        logger.info(f"Report {report_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()