import os
import pandas as pd
import logging
from textblob import TextBlob

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get dataset path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.getenv("DATASET_PATH", os.path.join(BASE_DIR, "ml", "datasets", "SentimentLabeledDataset.csv"))

# Check if dataset exists
if not os.path.exists(DATASET_PATH):
    logger.warning(f"Dataset not found at {DATASET_PATH}. Sentiment analysis will continue without proverbs.")
else:
    logger.info(f"Dataset loaded from: {DATASET_PATH}")


def analyze_sentiment(text):
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


def get_proverb_by_sentiment(sentiment):
    """
    Gets a Catalan proverb based on detected sentiment.

    Args:
        sentiment: The sentiment category ("Positive", "Negative", or "Neutral")

    Returns:
        Tuple of (catalan_proverb, english_translation)
    """
    try:
        # If dataset doesn't exist, return default proverbs
        if not os.path.exists(DATASET_PATH):
            logger.error("Dataset file does not exist.")
            default_proverbs = {
                "Positive": ("Qui no arrisca, no pisca.", "Who doesn't take risks, doesn't gain."),
                "Negative": ("A la taula i al llit, al primer crit.", "At the table and in bed, at the first call."),
                "Neutral": ("Cada terra fa sa guerra.", "Each land makes its own war.")
            }
            return default_proverbs.get(sentiment, default_proverbs["Neutral"])

        # Try loading the dataset with different encodings
        try:
            df = pd.read_csv(DATASET_PATH, encoding="utf-8-sig")
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(DATASET_PATH, encoding="latin1")
            except Exception as e:
                logger.error(f"Failed to load dataset with both UTF-8 and Latin1 encodings: {e}")
                return ("Hi ha temps per a tot.", "There is time for everything.")

        # Check for required columns
        catalan_col = "Catalan Proverb"
        english_col = "English Translation"
        sentiment_col = "Sentiment"

        required_columns = [catalan_col, english_col, sentiment_col]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            logger.error(f"Missing columns in dataset: {missing_columns}")
            return ("Fes bé i no facis mal, que altre sermó no et cal.",
                    "Do good and do no harm, for you need no other sermon.")

        # Normalize sentiment values
        df[sentiment_col] = df[sentiment_col].astype(str).str.strip()

        # Filter by sentiment
        sentiment = str(sentiment).strip()
        df_filtered = df[df[sentiment_col].eq(sentiment)]

        # If no matches found, try fallback options
        if df_filtered.empty:
            logger.warning(f"No proverbs found for sentiment '{sentiment}'. Trying fallback options.")

            # Try alternate sentiment spellings/formats
            if sentiment.lower() == "positive":
                alternate_sentiments = ["Positive", "positive", "POSITIVE"]
            elif sentiment.lower() == "negative":
                alternate_sentiments = ["Negative", "negative", "NEGATIVE"]
            else:
                alternate_sentiments = ["Neutral", "neutral", "NEUTRAL"]

            for alt_sentiment in alternate_sentiments:
                df_filtered = df[df[sentiment_col].eq(alt_sentiment)]
                if not df_filtered.empty:
                    break

            # If still empty, try getting any proverb
            if df_filtered.empty:
                logger.warning("Using random proverb as fallback.")
                if not df.empty:
                    df_filtered = df
                else:
                    return ("Feta la llei, feta la trampa.", "Once the law is made, the trick is found.")

        # Select a random proverb
        selected_row = df_filtered.sample(n=1).iloc[0]

        logger.info(f"Selected proverb for sentiment '{sentiment}': {selected_row[catalan_col]}")
        return selected_row[catalan_col], selected_row[english_col]

    except Exception as e:
        logger.error(f"Error getting proverb: {e}")
        # Default fallback proverbs
        fallback_proverbs = {
            "Positive": ("Qui dia passa, any empeny.", "Who passes the day, pushes the year."),
            "Negative": ("Home casat, burro espatllat.", "Married man, broken donkey."),
            "Neutral": ("Qui molt corre, poc pensa.", "Who runs a lot, thinks little.")
        }
        return fallback_proverbs.get(sentiment, fallback_proverbs["Neutral"])