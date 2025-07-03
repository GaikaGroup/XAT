import os
import json
import time
from datetime import datetime
from llama_index.core import VectorStoreIndex, Document, StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
import logging

# === Setup logging ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "..", "cadaques_catalog.json")
STORAGE_PATH = os.path.join(BASE_DIR, "index")
INDEX_METADATA_PATH = os.path.join(BASE_DIR, "index_metadata.json")
EMBEDDING_MODEL = "text-embedding-3-small"
EMAIL_DEFAULT = "1@gaikagroup.com"

# === Global variables ===
embed_model = OpenAIEmbedding(model=EMBEDDING_MODEL)

# === Index metadata for tracking freshness ===
def get_index_metadata():
    """Get metadata about the current index"""
    if os.path.exists(INDEX_METADATA_PATH):
        try:
            with open(INDEX_METADATA_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading index metadata: {e}")

    # Default metadata if file doesn't exist or can't be read
    return {
        "last_updated": None,
        "document_count": 0,
        "source_file": JSON_PATH,
        "source_last_modified": None
    }

def save_index_metadata(metadata):
    """Save metadata about the current index"""
    try:
        with open(INDEX_METADATA_PATH, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Index metadata saved to {INDEX_METADATA_PATH}")
    except Exception as e:
        logger.error(f"Error saving index metadata: {e}")

def is_index_stale():
    """Check if the index needs to be refreshed based on source file changes"""
    metadata = get_index_metadata()

    # If source file modification time is newer than our last update, index is stale
    if os.path.exists(JSON_PATH):
        source_mtime = os.path.getmtime(JSON_PATH)
        source_mtime_str = datetime.fromtimestamp(source_mtime).isoformat()

        if metadata["source_last_modified"] is None:
            return True

        if source_mtime_str > metadata["source_last_modified"]:
            logger.info(f"Source file modified: {metadata['source_last_modified']} -> {source_mtime_str}")
            return True

    return False

def load_json_data():
    """Load and parse the JSON data file"""
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # Check the structure to handle both formats
        if "sections" in raw_data:
            # Format: {"sections": [...]}
            catalog_sections = raw_data["sections"]
            logger.info(f"Found JSON with 'sections' array containing {len(catalog_sections)} sections")
        elif "section" in raw_data and "places" in raw_data:
            # Format: {"section": "...", "places": [...]}
            catalog_sections = [raw_data]  # Wrap single section in array
            logger.info(f"Found JSON with single section: {raw_data['section']}")
        else:
            # Try treating as array of sections
            if isinstance(raw_data, list):
                catalog_sections = raw_data
                logger.info(f"Found JSON with array of {len(catalog_sections)} sections")
            else:
                raise ValueError("Unrecognized JSON structure. Expected 'sections' array or single section object.")

        return catalog_sections
    except Exception as e:
        logger.error(f"Error loading JSON: {e}")
        raise

def process_data(catalog_sections):
    """Process the catalog sections into documents"""
    documents = []

    try:
        for section in catalog_sections:
            category = section.get("section", "Unknown")
            places = section.get("places", [])

            logger.info(f"Processing section '{category}' with {len(places)} places")

            for place in places:
                name = place.get("name", "Unknown")
                description = place.get("description", "")
                direction = place.get("direction", "")

                # Handle both possible structures for booking info
                booking_data = place.get("booking", {})
                has_booking = False
                booking_email = EMAIL_DEFAULT

                if isinstance(booking_data, dict):
                    has_booking = booking_data.get("has_booking", False)
                    booking_email = booking_data.get("email", EMAIL_DEFAULT)
                elif isinstance(booking_data, bool):
                    has_booking = booking_data

                # Handle features with flexible structure
                features_data = place.get("features", {})

                # Standardize features
                features = {
                    "has_terrace": features_data.get("has_terrace", False),
                    "sea_view": features_data.get("sea_view", False),
                    "booking": features_data.get("booking", has_booking)
                }

                # Create searchable text
                full_text = f"{name}\n{description}\nUbicación: {direction}"
                if features["has_terrace"]:
                    full_text += "\nTiene terraza."
                if features["sea_view"]:
                    full_text += "\nTiene vista al mar."
                if features["booking"] or has_booking:
                    full_text += "\nSe puede reservar."

                # Create consistent metadata
                metadata = {
                    "category": category,  # Store original category
                    "section": category,  # Also store as section for compatibility
                    "name": name,
                    "direction": direction,
                    "has_booking": has_booking,
                    "email": booking_email,
                    "features": features
                }

                documents.append(Document(text=full_text, metadata=metadata))
                logger.info(f"Added document for place: {name}")

        logger.info(f"Processed {len(documents)} documents total")
        return documents

    except Exception as e:
        logger.error(f"Error during processing: {e}", exc_info=True)
        raise

def create_index(documents):
    """Create and save the index from documents"""
    try:
        # Log start time for performance tracking
        start_time = time.time()

        # Create index with batch processing for better performance
        # The batch size controls how many documents are processed at once
        # This reduces memory usage and can speed up embedding generation
        batch_size = 32  # Adjust based on available memory and document size

        if len(documents) > batch_size:
            logger.info(f"Processing {len(documents)} documents in batches of {batch_size}")

            # Process documents in batches
            # We'll create a single index and add documents in batches
            from llama_index.core import Settings

            # Configure global settings for the index
            Settings.embed_model = embed_model

            # Create an empty index first
            from llama_index.core import ServiceContext
            service_context = ServiceContext.from_defaults(embed_model=embed_model)
            storage_context = StorageContext.from_defaults()

            # Process and add documents in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                batch_num = i//batch_size + 1
                total_batches = (len(documents)-1)//batch_size + 1
                logger.info(f"Processing batch {batch_num}/{total_batches} with {len(batch)} documents")

                # For the first batch, create the index
                if i == 0:
                    index = VectorStoreIndex.from_documents(
                        batch, 
                        storage_context=storage_context,
                        service_context=service_context
                    )
                # For subsequent batches, insert into existing index
                else:
                    index.insert_nodes(
                        [index.ingestion_pipeline.run(document=doc) for doc in batch]
                    )
        else:
            # For small document sets, process all at once
            logger.info(f"Processing all {len(documents)} documents at once")
            index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

        # Save index
        os.makedirs(STORAGE_PATH, exist_ok=True)
        index.storage_context.persist(STORAGE_PATH)

        # Update metadata
        source_mtime = os.path.getmtime(JSON_PATH)
        source_mtime_str = datetime.fromtimestamp(source_mtime).isoformat()

        # Calculate processing time
        elapsed_time = time.time() - start_time

        metadata = {
            "last_updated": datetime.now().isoformat(),
            "document_count": len(documents),
            "source_file": JSON_PATH,
            "source_last_modified": source_mtime_str,
            "processing_time_seconds": round(elapsed_time, 2)
        }
        save_index_metadata(metadata)

        logger.info(f"Index saved to {STORAGE_PATH} with {len(documents)} documents in {elapsed_time:.2f} seconds")
        return index
    except Exception as e:
        logger.error(f"Error creating index: {e}", exc_info=True)
        raise

def refresh_index():
    """Refresh the RAG index with the latest data"""
    try:
        logger.info("Starting index refresh...")

        # Load and process data
        catalog_sections = load_json_data()
        documents = process_data(catalog_sections)

        # Create and save index
        index = create_index(documents)

        logger.info("Index refresh completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error refreshing index: {e}", exc_info=True)
        return False

# Initialize the index if it doesn't exist or is stale
if not os.path.exists(STORAGE_PATH) or is_index_stale():
    try:
        logger.info("Initializing RAG index...")
        refresh_index()
    except Exception as e:
        logger.error(f"Error during initial index creation: {e}", exc_info=True)
