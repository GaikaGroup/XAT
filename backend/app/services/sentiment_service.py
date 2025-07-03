import os
import logging
import pandas as pd
import random
import time
from collections import deque
from typing import Tuple
from textblob import TextBlob

# Configure logging
logger = logging.getLogger(__name__)

# Set the path to the dataset containing Catalan proverbs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.getenv("DATASET_PATH", os.path.join(BASE_DIR, "ml", "datasets", "SentimentLabeledDataset.csv"))

# Global variables
PROVERBS_DF = None
# Track recently used proverbs to avoid repetition
# Store as (proverb_id, sentiment) to track both the proverb and associated sentiment
RECENTLY_USED_PROVERBS = deque(maxlen=50)  # Stores the last 50 used proverbs

def load_proverbs_dataset():
    """Load the proverbs dataset once at application startup"""
    global PROVERBS_DF
    try:
        if os.path.exists(DATASET_PATH):
            PROVERBS_DF = pd.read_csv(DATASET_PATH, encoding="utf-8-sig")
            # Clean up the dataframe
            if "Sentiment" in PROVERBS_DF.columns:
                PROVERBS_DF["Sentiment"] = PROVERBS_DF["Sentiment"].astype(str).str.strip()
            # Add an ID column if it doesn't exist
            if "id" not in PROVERBS_DF.columns:
                PROVERBS_DF["id"] = range(len(PROVERBS_DF))
            logger.info(f"Dataset loaded successfully with {len(PROVERBS_DF)} entries")
        else:
            logger.warning(f"Dataset not found at {DATASET_PATH}. Sentiment analysis will continue without proverbs.")
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")

def analyze_sentiment(text: str) -> str:
    """
    Analyzes sentiment of text and returns "Positive", "Negative", or "Neutral".

    Args:
        text: The text to analyze

    Returns:
        Sentiment category as string
    """
    try:
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity

        if polarity > 0:
            return "Positive"
        elif polarity < 0:
            return "Negative"
        else:
            return "Neutral"
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return "Neutral"  # Default to neutral on error

def get_proverb_by_sentiment(sentiment: str, user_input: str = "") -> Tuple[str, str]:
    """
    Fetch a proverb and its English translation based on sentiment.
    Now ensures variety by tracking previously used proverbs and using user input for additional entropy.
    
    Args:
        sentiment: The sentiment category ("Positive", "Negative", or "Neutral")
        user_input: Optional user input to use as additional entropy for proverb selection
        
    Returns:
        Tuple of (catalan_proverb, english_translation)
    """
    try:
        if PROVERBS_DF is not None and not PROVERBS_DF.empty:
            catalan_col = "Catalan Proverb"
            english_col = "English Translation"
            sentiment_col = "Sentiment"

            # Filter the dataset based on sentiment
            df_filtered = PROVERBS_DF[PROVERBS_DF[sentiment_col].eq(sentiment)]

            if df_filtered.empty:
                logger.warning(f"No proverbs found for sentiment '{sentiment}'. Using random proverb.")
                df_filtered = PROVERBS_DF

            # Get list of recently used proverb IDs for this sentiment
            recently_used_ids = [
                item[0] for item in RECENTLY_USED_PROVERBS
                if item[1] == sentiment
            ]

            # Create a pool of proverbs, preferring those not recently used
            available_proverbs = df_filtered[~df_filtered['id'].isin(recently_used_ids)]

            # If all proverbs for this sentiment have been recently used, reset and use all
            if available_proverbs.empty:
                available_proverbs = df_filtered
                logger.info(
                    f"All proverbs for sentiment '{sentiment}' have been used recently. Resetting selection pool.")

            # Select a random proverb from available ones
            # Use user input string as additional entropy
            random.seed(time.time() + hash(user_input) % 10000)
            selected_row = available_proverbs.sample(n=1).iloc[0]

            # Track this proverb as recently used
            proverb_id = selected_row['id']
            RECENTLY_USED_PROVERBS.append((proverb_id, sentiment))

            logger.info(f"Selected proverb (ID: {proverb_id}) for sentiment '{sentiment}': {selected_row[catalan_col]}")

            catalan_proverb = selected_row[catalan_col]
            english_translation = selected_row[english_col]

            # Ensure a valid proverb is returned
            if not pd.isna(catalan_proverb) and catalan_proverb != "No proverb found":
                return catalan_proverb, english_translation

        # Default proverb if none is found
        return "Fes bé i no facis mal, que altre sermó no et cal.", "Do good and do no harm, for you need no other sermon."
    except Exception as e:
        logger.error(f"Error getting proverb: {e}")
        return "Fes bé i no facis mal, que altre sermó no et cal.", "Do good and do no harm, for you need no other sermon."

# Initialize the dataset when the module is imported
load_proverbs_dataset()