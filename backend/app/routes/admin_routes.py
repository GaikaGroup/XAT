from flask import Blueprint, request, jsonify
import logging
import os
import time

from services.restaurant_service import rag_query_cache

# Configure logging
logger = logging.getLogger(__name__)

# Create a Blueprint for admin routes
admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/admin/refresh-rag", methods=["POST"])
def refresh_rag_index():
    """
    Admin endpoint to manually refresh the RAG index.
    
    Returns:
        JSON response with status information
    """
    try:
        # Import the refresh function from ingest module
        from rag.ingest import refresh_index

        # Check for admin authorization (simple token-based auth)
        auth_header = request.headers.get('Authorization')
        admin_token = os.getenv("ADMIN_TOKEN", "admin-secret-token")  # Default token if not set

        if not auth_header or auth_header != f"Bearer {admin_token}":
            return jsonify({"error": "Unauthorized access"}), 401

        # Trigger the refresh
        success = refresh_index()

        if success:
            # Clear the RAG query cache to ensure fresh results
            rag_query_cache.clear()

            # Reload the RAG query engine
            from llama_index.core import StorageContext, load_index_from_storage
            from llama_index.core.query_engine import RetrieverQueryEngine
            from llama_index.core.retrievers import VectorIndexRetriever
            from llama_index.core.node_parser import SentenceSplitter
            from services.restaurant_service import RAG_INDEX_PATH, RAG_EMBED_MODEL

            try:
                # Load the refreshed index
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
                import services.restaurant_service
                services.restaurant_service.rag_query_engine = rag_query_engine

                logger.info("✅ RAG query engine reloaded successfully after refresh")

                return jsonify({
                    "status": "success",
                    "message": "RAG index refreshed and query engine reloaded successfully",
                    "timestamp": time.time()
                }), 200

            except Exception as e:
                logger.error(f"❌ Failed to reload RAG query engine after refresh: {e}")
                return jsonify({
                    "status": "partial_success",
                    "message": "RAG index refreshed but query engine reload failed",
                    "error": str(e),
                    "timestamp": time.time()
                }), 500
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to refresh RAG index",
                "timestamp": time.time()
            }), 500

    except ImportError:
        return jsonify({
            "error": "RAG module not available",
            "message": "The RAG ingest module could not be imported"
        }), 500
    except Exception as e:
        logger.error(f"Error refreshing RAG index: {e}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500