import pytest
import json
from unittest.mock import patch, MagicMock

@pytest.mark.integration
class TestAdminRoutes:
    """Integration tests for the admin routes."""

    @patch('backend.app.routes.admin_routes.refresh_index')
    @patch('backend.app.routes.admin_routes.rag_query_cache')
    @patch('backend.app.routes.admin_routes.load_index_from_storage')
    @patch('backend.app.routes.admin_routes.StorageContext')
    @patch('backend.app.routes.admin_routes.RetrieverQueryEngine')
    @patch('backend.app.routes.admin_routes.VectorIndexRetriever')
    @patch('backend.app.routes.admin_routes.SentenceSplitter')
    def test_refresh_rag_index_success(self, mock_splitter, mock_retriever_class, mock_engine_class, 
                                      mock_storage_context, mock_load_index, mock_cache, mock_refresh_index, 
                                      client, monkeypatch):
        """Test the refresh RAG index endpoint with successful refresh and reload."""
        # Mock the environment variable for admin token
        monkeypatch.setenv("ADMIN_TOKEN", "test-admin-token")
        
        # Mock the refresh_index function to return True (success)
        mock_refresh_index.return_value = True
        
        # Mock the cache
        mock_cache.clear = MagicMock()
        
        # Mock the index loading
        mock_storage = MagicMock()
        mock_storage_context.from_defaults.return_value = mock_storage
        mock_index = MagicMock()
        mock_load_index.return_value = mock_index
        
        # Mock the retriever
        mock_retriever = MagicMock()
        mock_retriever_class.return_value = mock_retriever
        
        # Mock the query engine
        mock_engine = MagicMock()
        mock_engine_class.from_args.return_value = mock_engine
        
        # Send the request with the correct authorization header
        response = client.post("/admin/refresh-rag", headers={"Authorization": "Bearer test-admin-token"})
        
        # Verify the response
        assert response.status_code == 200
        assert "status" in response.json
        assert response.json["status"] == "success"
        assert "message" in response.json
        assert "RAG index refreshed and query engine reloaded successfully" in response.json["message"]
        assert "timestamp" in response.json
        
        # Verify that the refresh_index function was called
        mock_refresh_index.assert_called_once()
        
        # Verify that the cache was cleared
        mock_cache.clear.assert_called_once()
        
        # Verify that the index was loaded
        mock_storage_context.from_defaults.assert_called_once()
        mock_load_index.assert_called_once()
        
        # Verify that the retriever and query engine were created
        mock_retriever_class.assert_called_once()
        mock_engine_class.from_args.assert_called_once()

    def test_refresh_rag_index_unauthorized(self, client, monkeypatch):
        """Test the refresh RAG index endpoint with unauthorized access."""
        # Mock the environment variable for admin token
        monkeypatch.setenv("ADMIN_TOKEN", "test-admin-token")
        
        # Send the request without authorization header
        response = client.post("/admin/refresh-rag")
        
        # Verify the response
        assert response.status_code == 401
        assert "error" in response.json
        assert response.json["error"] == "Unauthorized access"
        
        # Send the request with incorrect authorization header
        response = client.post("/admin/refresh-rag", headers={"Authorization": "Bearer wrong-token"})
        
        # Verify the response
        assert response.status_code == 401
        assert "error" in response.json
        assert response.json["error"] == "Unauthorized access"

    @patch('backend.app.routes.admin_routes.refresh_index')
    def test_refresh_rag_index_refresh_failure(self, mock_refresh_index, client, monkeypatch):
        """Test the refresh RAG index endpoint with refresh failure."""
        # Mock the environment variable for admin token
        monkeypatch.setenv("ADMIN_TOKEN", "test-admin-token")
        
        # Mock the refresh_index function to return False (failure)
        mock_refresh_index.return_value = False
        
        # Send the request with the correct authorization header
        response = client.post("/admin/refresh-rag", headers={"Authorization": "Bearer test-admin-token"})
        
        # Verify the response
        assert response.status_code == 500
        assert "status" in response.json
        assert response.json["status"] == "error"
        assert "message" in response.json
        assert "Failed to refresh RAG index" in response.json["message"]
        assert "timestamp" in response.json
        
        # Verify that the refresh_index function was called
        mock_refresh_index.assert_called_once()

    @patch('backend.app.routes.admin_routes.refresh_index')
    @patch('backend.app.routes.admin_routes.rag_query_cache')
    @patch('backend.app.routes.admin_routes.load_index_from_storage')
    def test_refresh_rag_index_reload_failure(self, mock_load_index, mock_cache, mock_refresh_index, 
                                             client, monkeypatch):
        """Test the refresh RAG index endpoint with reload failure."""
        # Mock the environment variable for admin token
        monkeypatch.setenv("ADMIN_TOKEN", "test-admin-token")
        
        # Mock the refresh_index function to return True (success)
        mock_refresh_index.return_value = True
        
        # Mock the cache
        mock_cache.clear = MagicMock()
        
        # Mock the index loading to raise an exception
        mock_load_index.side_effect = Exception("Test reload error")
        
        # Send the request with the correct authorization header
        response = client.post("/admin/refresh-rag", headers={"Authorization": "Bearer test-admin-token"})
        
        # Verify the response
        assert response.status_code == 500
        assert "status" in response.json
        assert response.json["status"] == "partial_success"
        assert "message" in response.json
        assert "RAG index refreshed but query engine reload failed" in response.json["message"]
        assert "error" in response.json
        assert "Test reload error" in response.json["error"]
        assert "timestamp" in response.json
        
        # Verify that the refresh_index function was called
        mock_refresh_index.assert_called_once()
        
        # Verify that the cache was cleared
        mock_cache.clear.assert_called_once()
        
        # Verify that the index loading was attempted
        mock_load_index.assert_called_once()

    @patch('backend.app.routes.admin_routes.refresh_index', side_effect=ImportError("Test import error"))
    def test_refresh_rag_index_import_error(self, mock_refresh_index, client, monkeypatch):
        """Test the refresh RAG index endpoint with import error."""
        # Mock the environment variable for admin token
        monkeypatch.setenv("ADMIN_TOKEN", "test-admin-token")
        
        # Send the request with the correct authorization header
        response = client.post("/admin/refresh-rag", headers={"Authorization": "Bearer test-admin-token"})
        
        # Verify the response
        assert response.status_code == 500
        assert "error" in response.json
        assert response.json["error"] == "RAG module not available"
        assert "message" in response.json
        assert "The RAG ingest module could not be imported" in response.json["message"]
        
        # Verify that the refresh_index function was called
        mock_refresh_index.assert_called_once()

    @patch('backend.app.routes.admin_routes.refresh_index', side_effect=Exception("Test general error"))
    def test_refresh_rag_index_general_error(self, mock_refresh_index, client, monkeypatch):
        """Test the refresh RAG index endpoint with general error."""
        # Mock the environment variable for admin token
        monkeypatch.setenv("ADMIN_TOKEN", "test-admin-token")
        
        # Send the request with the correct authorization header
        response = client.post("/admin/refresh-rag", headers={"Authorization": "Bearer test-admin-token"})
        
        # Verify the response
        assert response.status_code == 500
        assert "error" in response.json
        assert response.json["error"] == "Internal server error"
        assert "message" in response.json
        assert "Test general error" in response.json["message"]
        
        # Verify that the refresh_index function was called
        mock_refresh_index.assert_called_once()