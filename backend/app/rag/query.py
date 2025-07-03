import logging
from typing import List, Dict, Any, Optional
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.node_parser import SentenceSplitter

# Configure logging
logger = logging.getLogger(__name__)

# Import RAG configuration
from services.restaurant_service import RAG_INDEX_PATH, RAG_EMBED_MODEL

# Initialize RAG query engine
try:
    # Load the index
    rag_storage = StorageContext.from_defaults(persist_dir=RAG_INDEX_PATH)
    rag_index = load_index_from_storage(rag_storage, embed_model=RAG_EMBED_MODEL)

    # Create a retriever with appropriate parameters
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
    logger.info("✅ RAG query engine initialized in query.py")
except Exception as e:
    logger.error(f"❌ Failed to initialize RAG query engine in query.py: {e}", exc_info=True)
    rag_query_engine = None

def query_places(user_query: str) -> List[Dict[str, Any]]:
    """
    Query the RAG index for places based on user input

    Args:
        user_query: The user's query string

    Returns:
        A list of dictionaries containing place information
    """
    if rag_query_engine is None:
        logger.error("RAG query engine not initialized")
        return []

    try:
        # Add debug logging
        logger.info(f"Querying RAG index with: {user_query}")

        # Execute query
        response = rag_query_engine.query(user_query)

        # Process results
        results = []
        for node in response.source_nodes:
            doc = node.node
            metadata = doc.metadata

            # Log the metadata structure for debugging
            logger.debug(f"Source node metadata: {metadata}")

            # Extract data with fallbacks for flexibility
            place_info = {
                "name": metadata.get("name", "Unknown"),
                # Support both "category" and "section" fields
                "category": metadata.get("category", metadata.get("section", "")),
                "text": doc.text,  # This is the full text from the document
                "direction": metadata.get("direction", ""),
                "has_booking": metadata.get("has_booking", False),
                "email": metadata.get("email", ""),
                "features": metadata.get("features", {})
            }

            results.append(place_info)

        logger.info(f"RAG query returned {len(results)} results")
        return results

    except Exception as e:
        logger.error(f"Error querying RAG index: {e}", exc_info=True)
        return []
