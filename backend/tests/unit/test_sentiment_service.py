import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from collections import deque

from app.services.sentiment_service import (
    analyze_sentiment,
    get_proverb_by_sentiment,
    load_proverbs_dataset,
    RECENTLY_USED_PROVERBS
)

@pytest.mark.unit
class TestSentimentService:
    """Tests for the sentiment_service module."""

    def test_analyze_sentiment_positive(self):
        """Test analyzing positive sentiment."""
        text = "I love this product, it's amazing!"
        result = analyze_sentiment(text)
        assert result == "Positive"

    def test_analyze_sentiment_negative(self):
        """Test analyzing negative sentiment."""
        text = "I hate this product, it's terrible!"
        result = analyze_sentiment(text)
        assert result == "Negative"

    def test_analyze_sentiment_neutral(self):
        """Test analyzing neutral sentiment."""
        text = "This is a product."
        result = analyze_sentiment(text)
        assert result == "Neutral"

    @patch('app.services.sentiment_service.TextBlob')
    def test_analyze_sentiment_exception(self, mock_textblob):
        """Test handling of exceptions in sentiment analysis."""
        mock_textblob.side_effect = Exception("Test exception")
        
        text = "This should raise an exception"
        result = analyze_sentiment(text)
        assert result == "Neutral"  # Default to neutral on error

    @patch('app.services.sentiment_service.PROVERBS_DF')
    def test_get_proverb_by_sentiment_found(self, mock_df):
        """Test getting a proverb by sentiment when proverbs are found."""
        # Create a mock DataFrame with test data
        mock_df.__bool__.return_value = True  # Make the DataFrame evaluate to True
        mock_df.empty = False
        
        # Create a sample DataFrame
        sample_data = {
            'id': [1, 2, 3],
            'Catalan Proverb': ['Proverb 1', 'Proverb 2', 'Proverb 3'],
            'English Translation': ['Translation 1', 'Translation 2', 'Translation 3'],
            'Sentiment': ['Positive', 'Negative', 'Neutral']
        }
        sample_df = pd.DataFrame(sample_data)
        
        # Mock the filtering and sampling operations
        mock_df.__getitem__.return_value = MagicMock()
        mock_df.__getitem__().eq.return_value = MagicMock()
        mock_df[mock_df['Sentiment'].eq('Positive')] = sample_df[sample_df['Sentiment'] == 'Positive']
        mock_df[~mock_df['id'].isin([])].empty = False
        mock_df[~mock_df['id'].isin([])].sample.return_value = sample_df[sample_df['Sentiment'] == 'Positive']
        
        # Reset the recently used proverbs
        global RECENTLY_USED_PROVERBS
        RECENTLY_USED_PROVERBS = deque(maxlen=50)
        
        # Test getting a positive proverb
        catalan, english = get_proverb_by_sentiment("Positive", "test input")
        assert catalan == "Proverb 1"
        assert english == "Translation 1"

    @patch('app.services.sentiment_service.PROVERBS_DF')
    def test_get_proverb_by_sentiment_not_found(self, mock_df):
        """Test getting a proverb by sentiment when no proverbs are found."""
        # Create a mock DataFrame that's empty
        mock_df.__bool__.return_value = True  # Make the DataFrame evaluate to True
        mock_df.empty = False
        
        # Mock the filtering operation to return an empty DataFrame
        mock_df.__getitem__.return_value = MagicMock()
        mock_df.__getitem__().eq.return_value = MagicMock()
        mock_df[mock_df['Sentiment'].eq('Unknown')] = pd.DataFrame()  # Empty DataFrame
        
        # Test getting a proverb with an unknown sentiment
        catalan, english = get_proverb_by_sentiment("Unknown", "test input")
        assert catalan == "Fes bé i no facis mal, que altre sermó no et cal."
        assert english == "Do good and do no harm, for you need no other sermon."

    @patch('app.services.sentiment_service.PROVERBS_DF')
    def test_get_proverb_by_sentiment_df_none(self, mock_df):
        """Test getting a proverb by sentiment when the DataFrame is None."""
        # Set the mock DataFrame to None
        mock_df.__bool__.return_value = False
        
        # Test getting a proverb when the DataFrame is None
        catalan, english = get_proverb_by_sentiment("Positive", "test input")
        assert catalan == "Fes bé i no facis mal, que altre sermó no et cal."
        assert english == "Do good and do no harm, for you need no other sermon."

    @patch('app.services.sentiment_service.PROVERBS_DF')
    def test_get_proverb_by_sentiment_exception(self, mock_df):
        """Test handling of exceptions in get_proverb_by_sentiment."""
        # Make the DataFrame raise an exception when accessed
        mock_df.__bool__.side_effect = Exception("Test exception")
        
        # Test getting a proverb when an exception is raised
        catalan, english = get_proverb_by_sentiment("Positive", "test input")
        assert catalan == "Fes bé i no facis mal, que altre sermó no et cal."
        assert english == "Do good and do no harm, for you need no other sermon."

    @patch('app.services.sentiment_service.pd.read_csv')
    @patch('app.services.sentiment_service.os.path.exists')
    def test_load_proverbs_dataset_success(self, mock_exists, mock_read_csv):
        """Test loading the proverbs dataset successfully."""
        # Mock os.path.exists to return True
        mock_exists.return_value = True
        
        # Create a mock DataFrame
        mock_df = pd.DataFrame({
            'Catalan Proverb': ['Proverb 1', 'Proverb 2'],
            'English Translation': ['Translation 1', 'Translation 2'],
            'Sentiment': ['Positive', 'Negative']
        })
        mock_read_csv.return_value = mock_df
        
        # Call the function
        load_proverbs_dataset()
        
        # Verify that read_csv was called
        mock_read_csv.assert_called_once()

    @patch('app.services.sentiment_service.os.path.exists')
    def test_load_proverbs_dataset_file_not_found(self, mock_exists):
        """Test loading the proverbs dataset when the file is not found."""
        # Mock os.path.exists to return False
        mock_exists.return_value = False
        
        # Call the function
        load_proverbs_dataset()
        
        # No assertions needed, just checking that the function doesn't raise an exception

    @patch('app.services.sentiment_service.pd.read_csv')
    @patch('app.services.sentiment_service.os.path.exists')
    def test_load_proverbs_dataset_exception(self, mock_exists, mock_read_csv):
        """Test handling of exceptions in load_proverbs_dataset."""
        # Mock os.path.exists to return True
        mock_exists.return_value = True
        
        # Make read_csv raise an exception
        mock_read_csv.side_effect = Exception("Test exception")
        
        # Call the function
        load_proverbs_dataset()
        
        # No assertions needed, just checking that the function doesn't raise an exception