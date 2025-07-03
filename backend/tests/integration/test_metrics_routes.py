import pytest
import json
from unittest.mock import patch, MagicMock
from collections import deque

@pytest.mark.integration
class TestMetricsRoutes:
    """Integration tests for the metrics routes."""

    @patch('backend.app.routes.metrics_routes.get_metrics_snapshot')
    @patch('backend.app.routes.metrics_routes.get_session_snapshot')
    @patch('backend.app.routes.metrics_routes.response_cache')
    @patch('backend.app.routes.metrics_routes.translation_cache')
    @patch('backend.app.routes.metrics_routes.PROVERBS_DF')
    @patch('backend.app.routes.metrics_routes.RECENTLY_USED_PROVERBS')
    def test_metrics_endpoint(self, mock_recently_used_proverbs, mock_proverbs_df, 
                             mock_translation_cache, mock_response_cache, 
                             mock_get_session_snapshot, mock_get_metrics_snapshot, client):
        """Test the metrics endpoint."""
        # Mock the get_metrics_snapshot function
        mock_get_metrics_snapshot.return_value = {
            "gpt_requests_total": 100,
            "gpt_tokens_total": 5000,
            "rag_queries_total": 50,
            "translation_requests_total": 200
        }
        
        # Mock the get_session_snapshot function
        mock_get_session_snapshot.return_value = {
            "active_sessions": 10,
            "total_sessions": 100,
            "avg_messages_per_session": 5.5
        }
        
        # Mock the caches
        mock_response_cache.__len__.return_value = 20
        mock_translation_cache.__len__.return_value = 30
        
        # Mock the proverbs data
        mock_proverbs_df.__bool__.return_value = True
        mock_proverbs_df.__len__.return_value = 100
        
        # Mock the recently used proverbs
        mock_recently_used_proverbs.__len__.return_value = 15
        
        # Send the request
        response = client.get("/metrics")
        
        # Verify the response
        assert response.status_code == 200
        
        # Verify the metrics data
        metrics = response.json
        
        # GPT and RAG metrics
        assert metrics["gpt_requests_total"] == 100
        assert metrics["gpt_tokens_total"] == 5000
        assert metrics["rag_queries_total"] == 50
        assert metrics["translation_requests_total"] == 200
        
        # Session metrics
        assert metrics["active_sessions"] == 10
        assert metrics["total_sessions"] == 100
        assert metrics["avg_messages_per_session"] == 5.5
        
        # Cache metrics
        assert metrics["response_cache_size"] == 20
        assert metrics["translation_cache_size"] == 30
        
        # Proverbs metrics
        assert metrics["proverbs_loaded"] is True
        assert metrics["proverb_count"] == 100
        assert metrics["recent_proverbs_tracked"] == 15
        
        # Verify that the functions were called
        mock_get_metrics_snapshot.assert_called_once()
        mock_get_session_snapshot.assert_called_once()

    @patch('backend.app.routes.metrics_routes.get_metrics_snapshot')
    @patch('backend.app.routes.metrics_routes.get_session_snapshot')
    @patch('backend.app.routes.metrics_routes.response_cache')
    @patch('backend.app.routes.metrics_routes.translation_cache')
    @patch('backend.app.routes.metrics_routes.PROVERBS_DF')
    @patch('backend.app.routes.metrics_routes.RECENTLY_USED_PROVERBS')
    def test_metrics_endpoint_no_proverbs(self, mock_recently_used_proverbs, mock_proverbs_df, 
                                         mock_translation_cache, mock_response_cache, 
                                         mock_get_session_snapshot, mock_get_metrics_snapshot, client):
        """Test the metrics endpoint when no proverbs are loaded."""
        # Mock the get_metrics_snapshot function
        mock_get_metrics_snapshot.return_value = {
            "gpt_requests_total": 100,
            "gpt_tokens_total": 5000,
            "rag_queries_total": 50,
            "translation_requests_total": 200
        }
        
        # Mock the get_session_snapshot function
        mock_get_session_snapshot.return_value = {
            "active_sessions": 10,
            "total_sessions": 100,
            "avg_messages_per_session": 5.5
        }
        
        # Mock the caches
        mock_response_cache.__len__.return_value = 20
        mock_translation_cache.__len__.return_value = 30
        
        # Mock the proverbs data (None)
        mock_proverbs_df.__bool__.return_value = False
        mock_proverbs_df.__len__.return_value = 0
        
        # Mock the recently used proverbs
        mock_recently_used_proverbs.__len__.return_value = 0
        
        # Send the request
        response = client.get("/metrics")
        
        # Verify the response
        assert response.status_code == 200
        
        # Verify the metrics data
        metrics = response.json
        
        # Proverbs metrics
        assert metrics["proverbs_loaded"] is False
        assert metrics["proverb_count"] == 0
        assert metrics["recent_proverbs_tracked"] == 0