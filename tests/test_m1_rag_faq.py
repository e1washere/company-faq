import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "m1-rag-faq"))
sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "m7-vector-swap"))

from rag_demo import ingest_docs, load_vectordb, single_query


class TestRAGDemo:
    def test_ingest_docs_mock(self):
        """Test document ingestion with mocked components."""
        with patch('rag_demo.TextLoader') as mock_loader, \
             patch('rag_demo.RecursiveCharacterTextSplitter') as mock_splitter, \
             patch('rag_demo.Chroma') as mock_chroma, \
             patch('rag_demo.OpenAIEmbeddings') as mock_embeddings:
            
            # Mock the loader
            mock_doc = MagicMock()
            mock_loader.return_value.load.return_value = [mock_doc]
            
            # Mock the splitter
            mock_chunks = [MagicMock(), MagicMock()]
            mock_splitter.return_value.split_documents.return_value = mock_chunks
            
            # Mock Chroma
            mock_vectordb = MagicMock()
            mock_chroma.from_documents.return_value = mock_vectordb
            
            # Test function
            result = ingest_docs(Path("test.md"))
            
            # Assertions
            mock_loader.assert_called_once_with("test.md", encoding="utf-8")
            mock_splitter.assert_called_once_with(chunk_size=1_000, chunk_overlap=200)
            mock_chroma.from_documents.assert_called_once()
            assert result == mock_vectordb

    def test_load_vectordb_mock(self):
        """Test loading existing vector database."""
        with patch('rag_demo.Chroma') as mock_chroma, \
             patch('rag_demo.OpenAIEmbeddings') as mock_embeddings:
            
            mock_vectordb = MagicMock()
            mock_chroma.return_value = mock_vectordb
            
            result = load_vectordb()
            
            mock_chroma.assert_called_once()
            assert result == mock_vectordb

    def test_single_query_mock(self):
        """Test single query execution."""
        with patch('rag_demo.ConversationalRetrievalChain') as mock_chain:
            mock_vectordb = MagicMock()
            mock_chain_instance = MagicMock()
            mock_chain.from_llm.return_value = mock_chain_instance
            mock_chain_instance.invoke.return_value = {"answer": "Test response"}
            
            result = single_query("test query", mock_vectordb)
            
            mock_chain.from_llm.assert_called_once()
            mock_chain_instance.invoke.assert_called_once_with({
                "question": "test query",
                "chat_history": []
            })
            assert result == "Test response"

    def test_single_query_with_history(self):
        """Test single query with chat history."""
        with patch('rag_demo.ConversationalRetrievalChain') as mock_chain:
            mock_vectordb = MagicMock()
            mock_chain_instance = MagicMock()
            mock_chain.from_llm.return_value = mock_chain_instance
            mock_chain_instance.invoke.return_value = {"answer": "Test response"}
            
            history = [("prev q", "prev a")]
            result = single_query("test query", mock_vectordb, history)
            
            mock_chain_instance.invoke.assert_called_once_with({
                "question": "test query",
                "chat_history": history
            })
            assert result == "Test response"

    def test_file_paths(self):
        """Test file path handling."""
        from rag_demo import COLLECTION, DEFAULT_SOURCE, PERSIST_DIR
        
        assert DEFAULT_SOURCE == Path("data/faq.md")
        assert PERSIST_DIR == "vector_store"
        assert COLLECTION == "company_faq_demo" 