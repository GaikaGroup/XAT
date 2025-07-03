import pytest
import json

@pytest.mark.integration
class TestHealthRoutes:
    """Integration tests for the health routes."""

    def test_health_check(self, client):
        """Test the health check endpoint."""
        # Send a GET request to the health endpoint
        response = client.get("/health")
        
        # Verify the response
        assert response.status_code == 200
        assert "status" in response.json
        assert response.json["status"] == "ok"
        assert "version" in response.json
        assert "timestamp" in response.json
        
        # Verify the timestamp is a number
        assert isinstance(response.json["timestamp"], (int, float))

    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        # Send a GET request to the root endpoint
        response = client.get("/")
        
        # Verify the response
        assert response.status_code == 200
        assert "message" in response.json
        assert "Welcome to HugDimon API!" in response.json["message"]
        assert "status" in response.json
        assert response.json["status"] == "online"
        assert "endpoints" in response.json
        assert "version" in response.json
        
        # Verify the endpoints information
        endpoints = response.json["endpoints"]
        assert "/chat" in endpoints
        assert "/guide" in endpoints
        assert "/health" in endpoints
        assert "/metrics" in endpoints
        assert "/feedback/rag" in endpoints
        assert "/admin/refresh-rag" in endpoints