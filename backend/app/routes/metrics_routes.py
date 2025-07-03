from flask import Blueprint, jsonify
import logging

from metrics.inference_metrics import get_metrics_snapshot
from metrics.session_metrics import get_session_snapshot
from services.chatgpt_service import response_cache
from services.translation_service import translation_cache
from services.sentiment_service import PROVERBS_DF, RECENTLY_USED_PROVERBS

# Configure logging
logger = logging.getLogger(__name__)

# Create a Blueprint for metrics routes
metrics_bp = Blueprint('metrics', __name__)

@metrics_bp.route("/metrics", methods=["GET"])
def metrics():
    """
    Return all metrics including GPT, RAG, and session stats.

    Returns:
        JSON response with metrics data
    """
    return jsonify({
        **get_metrics_snapshot(),       # GPT + RAG + Translation metrics
        **get_session_snapshot(),       # Session metrics (per session ID)
        "response_cache_size": len(response_cache),
        "translation_cache_size": len(translation_cache),
        "proverbs_loaded": PROVERBS_DF is not None and len(PROVERBS_DF) > 0,
        "proverb_count": len(PROVERBS_DF) if PROVERBS_DF is not None else 0,
        "recent_proverbs_tracked": len(RECENTLY_USED_PROVERBS)
    }), 200
