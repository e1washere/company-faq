import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "m3-auto-reporter"))

from reporter import build_prompt, fetch_events, generate_summary, main, send_to_slack


class TestAutoReporter:
    def test_fetch_events_csv_mode(self):
        """Test fetching events from CSV file."""
        with patch('reporter.os.getenv') as mock_getenv, \
             patch('reporter.pd.read_csv') as mock_read_csv:
            
            # Setup mocks
            mock_getenv.side_effect = lambda key: None if key == "USE_BIGQUERY" else "test.csv"
            mock_df = pd.DataFrame({
                'user_id': [1, 2, 3],
                'event_name': ['login', 'purchase', 'logout'],
                'created_at': ['2023-01-01', '2023-01-02', '2023-01-03']
            })
            mock_read_csv.return_value = mock_df
            
            result = fetch_events()
            
            mock_read_csv.assert_called_once_with("test.csv")
            assert result.equals(mock_df)

    @patch('reporter.os.getenv')
    @patch('reporter.bigquery')
    def test_fetch_events_bigquery_mode(self, mock_bigquery, mock_getenv):
        """Test fetching events from BigQuery."""
        # Setup environment variables
        mock_getenv.side_effect = lambda key: {
            "USE_BIGQUERY": "true",
            "VERTEX_PROJECT": "test-project"
        }.get(key)
        
        # Mock BigQuery client
        mock_client = MagicMock()
        mock_bigquery.Client.return_value = mock_client
        
        mock_df = pd.DataFrame({
            'user_id': [1, 2],
            'event_name': ['login', 'purchase'],
            'created_at': ['2023-01-01', '2023-01-02']
        })
        mock_client.query.return_value.to_dataframe.return_value = mock_df
        
        result = fetch_events()
        
        mock_bigquery.Client.assert_called_once_with(project="test-project")
        mock_client.query.assert_called_once()
        assert result.equals(mock_df)

    def test_build_prompt(self):
        """Test building prompt from DataFrame."""
        # Create test DataFrame
        df = pd.DataFrame({
            'user_id': [1, 2, 3],
            'event_name': ['login', 'purchase', 'logout'],
            'created_at': ['2023-01-01', '2023-01-02', '2023-01-03']
        })
        
        # Mock the template file
        with patch('reporter.Path') as mock_path:
            mock_template = "Events found: {n}\n\nData:\n{table}"
            mock_path.return_value.with_name.return_value.joinpath.return_value.read_text.return_value = mock_template
            
            result = build_prompt(df)
            
            assert "Events found: 3" in result
            assert "user_id" in result
            assert "event_name" in result
            assert "created_at" in result

    @patch('reporter.MODEL')
    def test_generate_summary(self, mock_model):
        """Test generating summary from prompt."""
        mock_chat = MagicMock()
        mock_model.start_chat.return_value = mock_chat
        mock_chat.send_message.return_value.text = "  Summary response  "
        
        result = generate_summary("Test prompt")
        
        mock_model.start_chat.assert_called_once()
        mock_chat.send_message.assert_called_once_with("Test prompt")
        assert result == "Summary response"

    @patch('reporter.SLACK_URL', 'https://hooks.slack.com/test')
    @patch('reporter.requests.post')
    def test_send_to_slack_with_webhook(self, mock_post):
        """Test sending to Slack with webhook URL."""
        mock_response = MagicMock()
        mock_post.return_value = mock_response
        
        send_to_slack("Test message")
        
        mock_post.assert_called_once_with(
            'https://hooks.slack.com/test',
            json={"text": "Test message"}
        )
        mock_response.raise_for_status.assert_called_once()

    @patch('reporter.SLACK_URL', None)
    @patch('builtins.print')
    def test_send_to_slack_no_webhook(self, mock_print):
        """Test sending to Slack without webhook URL (prints instead)."""
        send_to_slack("Test message")
        
        mock_print.assert_called_with("=== SUMMARY ===\n", "Test message")

    @patch('reporter.fetch_events')
    @patch('reporter.build_prompt')
    @patch('reporter.generate_summary')
    @patch('reporter.send_to_slack')
    def test_main_function(self, mock_send_slack, mock_generate, mock_build, mock_fetch):
        """Test the main function integration."""
        # Setup mocks
        mock_df = pd.DataFrame({'test': [1, 2, 3]})
        mock_fetch.return_value = mock_df
        mock_build.return_value = "Test prompt"
        mock_generate.return_value = "Test summary"
        
        main()
        
        # Verify call chain
        mock_fetch.assert_called_once()
        mock_build.assert_called_once_with(mock_df)
        mock_generate.assert_called_once_with("Test prompt")
        mock_send_slack.assert_called_once_with("Test summary")

    def test_environment_variables(self):
        """Test environment variable usage."""
        with patch('reporter.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: {
                "VERTEX_PROJECT": "test-project",
                "VERTEX_LOCATION": "us-central1", 
                "SLACK_WEBHOOK": "https://hooks.slack.com/test",
                "CSV_PATH": "test.csv"
            }.get(key, default)
            
            # Re-import to get updated environment variables
            import importlib

            import reporter
            importlib.reload(reporter)
            
            assert reporter.PROJECT == "test-project"
            assert reporter.LOCATION == "us-central1"
            assert reporter.SLACK_URL == "https://hooks.slack.com/test"
            assert reporter.LOCAL_CSV == "test.csv" 