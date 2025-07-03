import sys
import os
import logging
from typing import Optional
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

from utils.logging_config import configure_logging
from utils.middleware import register_middleware

# Configure basic logging for startup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app() -> Flask:
    """
    Application factory function that creates and configures the Flask app.

    Returns:
        Flask: The configured Flask application
    """
    # Load environment variables
    load_dotenv()

    # Setup path for imports
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))
    DIALOGS_DIR = os.path.abspath(os.path.join(ROOT_DIR, "dialogs"))

    if DIALOGS_DIR not in sys.path:
        sys.path.insert(0, DIALOGS_DIR)

    # Add project root to path
    if ROOT_DIR not in sys.path:
        sys.path.insert(0, ROOT_DIR)

    # Add app directory to path
    APP_DIR = os.path.abspath(os.path.join(ROOT_DIR, "app"))
    if APP_DIR not in sys.path:
        sys.path.insert(0, APP_DIR)

    # Initialize Flask app
    app = Flask(__name__)
    app.json.ensure_ascii = False

    # Configure logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    configure_logging(app, log_level)

    # Register middleware
    register_middleware(app)

    # Define allowed origins for CORS
    allowed_origins = [
        "http://localhost:5173",
        "http://localhost:5000",
        "http://192.168.1.130:5173",
        "http://35.181.170.203:5173"
    ]

    # Configure CORS
    CORS(
        app,
        resources={r"/*": {"origins": allowed_origins}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "OPTIONS"]
    )

    # Configure rate limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )

    # Initialize services
    from services.restaurant_service import RESTAURANT_KEYWORDS_BY_LANG
    from services.sentiment_service import load_proverbs_dataset

    logger.info("Initializing application...")
    load_proverbs_dataset()

    # Initialize RAG query engine
    try:
        from llama_index.core import StorageContext, load_index_from_storage
        from llama_index.core.query_engine import RetrieverQueryEngine
        from llama_index.core.retrievers import VectorIndexRetriever
        from llama_index.core.node_parser import SentenceSplitter
        from services.restaurant_service import RAG_INDEX_PATH, RAG_EMBED_MODEL
        import services.restaurant_service

        if os.path.exists(RAG_INDEX_PATH):
            logger.info("Loading RAG index and initializing query engine...")
            rag_storage = StorageContext.from_defaults(persist_dir=RAG_INDEX_PATH)
            rag_index = load_index_from_storage(rag_storage, embed_model=RAG_EMBED_MODEL)

            # Create a more sophisticated retriever with better parameters
            retriever = VectorIndexRetriever(
                index=rag_index,
                similarity_top_k=30,
                filters=None,
                alpha=0.5,
            )

            # Create a query engine with the custom retriever
            rag_query_engine = RetrieverQueryEngine.from_args(
                retriever=retriever,
                node_parser=SentenceSplitter(chunk_size=512, chunk_overlap=50),
                response_mode="compact",
            )

            # Update the global rag_query_engine
            services.restaurant_service.rag_query_engine = rag_query_engine
            logger.info("✅ RAG query engine initialized successfully")
        else:
            logger.warning("⚠️ RAG index not found, query engine not initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG query engine: {e}", exc_info=True)

    logger.info("Application initialized successfully")

    # Register blueprints
    from routes.chat_routes import chat_bp
    from routes.health_routes import health_bp
    from routes.guide_routes import guide_bp
    from routes.metrics_routes import metrics_bp
    from routes.feedback_routes import feedback_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(chat_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(guide_bp)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(admin_bp)

    # Apply rate limits to specific routes
    limiter.limit("20 per minute")(chat_bp)
    limiter.limit("20 per minute")(guide_bp)
    limiter.limit("5 per hour")(admin_bp)

    return app
