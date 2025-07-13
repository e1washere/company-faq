import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "m2-api-gateway"))

from api_gateway import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    Provider,
    _call_openai,
    _call_vertex,
    app,
)
from fastapi.testclient import TestClient


class TestAPIGateway:
    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)

    def test_provider_enum(self):
        """Test Provider enum values."""
        assert Provider.openai == "openai"
        assert Provider.vertex == "vertex"

    def test_chat_message_model(self):
        """Test ChatMessage model."""
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_chat_request_model(self):
        """Test ChatRequest model."""
        messages = [ChatMessage(role="user", content="Hello")]
        req = ChatRequest(messages=messages)
        assert len(req.messages) == 1
        assert req.messages[0].role == "user"

    def test_chat_response_model(self):
        """Test ChatResponse model."""
        resp = ChatResponse(
            provider=Provider.openai,
            model="gpt-3.5-turbo",
            content="Hello back"
        )
        assert resp.provider == Provider.openai
        assert resp.model == "gpt-3.5-turbo"
        assert resp.content == "Hello back"

    @patch('api_gateway.OPENAI_API_KEY', 'test-key')
    @patch('api_gateway.openai.OpenAI')
    def test_call_openai_success(self, mock_openai_class):
        """Test successful OpenAI API call."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        result = _call_openai("gpt-3.5-turbo", messages)
        
        assert result == "Test response"
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0
        )

    @patch('api_gateway.VERTEX_PROJECT', 'test-project')
    @patch('api_gateway.vertexai')
    @patch('api_gateway.GenerativeModel')
    def test_call_vertex_success(self, mock_model_class, mock_vertexai):
        """Test successful Vertex AI API call."""
        mock_model = MagicMock()
        mock_model_class.return_value = mock_model
        
        mock_response = MagicMock()
        mock_response.text = "Test response"
        mock_model.generate_content.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        result = _call_vertex("gemini-pro", messages)
        
        assert result == "Test response"
        mock_vertexai.init.assert_called_once()
        mock_model.generate_content.assert_called_once()

    @patch('api_gateway.OPENAI_API_KEY', 'test-key')
    @patch('api_gateway._call_openai')
    def test_chat_endpoint_openai(self, mock_call_openai):
        """Test chat endpoint with OpenAI provider."""
        mock_call_openai.return_value = "OpenAI response"
        
        request_data = {
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        response = self.client.post(
            "/chat?provider=openai&model=gpt-3.5-turbo",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "openai"
        assert data["model"] == "gpt-3.5-turbo"
        assert data["content"] == "OpenAI response"

    @patch('api_gateway.VERTEX_PROJECT', 'test-project')
    @patch('api_gateway._call_vertex')
    def test_chat_endpoint_vertex(self, mock_call_vertex):
        """Test chat endpoint with Vertex AI provider."""
        mock_call_vertex.return_value = "Vertex response"
        
        request_data = {
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        response = self.client.post(
            "/chat?provider=vertex&model=gemini-pro",
            json=request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "vertex"
        assert data["model"] == "gemini-pro"
        assert data["content"] == "Vertex response"

    @patch('api_gateway.OPENAI_API_KEY', None)
    def test_chat_endpoint_openai_no_key(self):
        """Test chat endpoint with OpenAI provider but no API key."""
        request_data = {
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        response = self.client.post(
            "/chat?provider=openai&model=gpt-3.5-turbo",
            json=request_data
        )
        
        assert response.status_code == 500
        assert "OPENAI_API_KEY not configured" in response.json()["detail"]

    @patch('api_gateway.VERTEX_PROJECT', None)
    def test_chat_endpoint_vertex_no_project(self):
        """Test chat endpoint with Vertex AI provider but no project."""
        request_data = {
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        response = self.client.post(
            "/chat?provider=vertex&model=gemini-pro",
            json=request_data
        )
        
        assert response.status_code == 500
        assert "VERTEX_PROJECT env var not set" in response.json()["detail"]

    def test_chat_endpoint_default_params(self):
        """Test chat endpoint with default parameters."""
        with patch('api_gateway.VERTEX_PROJECT', 'test-project'), \
             patch('api_gateway._call_vertex') as mock_call_vertex:
            
            mock_call_vertex.return_value = "Default response"
            
            request_data = {
                "messages": [{"role": "user", "content": "Hello"}]
            }
            
            response = self.client.post("/chat", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["provider"] == "vertex"
            assert data["model"] == "gemini-2.5-pro"  # DEFAULT_MODEL 