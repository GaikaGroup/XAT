import os
import logging
from app_factory import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



# Create the Flask app using the factory function
app = create_app()







if __name__ == "__main__":
    logger.info("🚀 HugDimon Flask Server is starting...")
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    try:
        app.run(
            host="0.0.0.0",
            port=int(os.getenv("PORT", 5000)),
            debug=debug_mode,
            threaded=True
        )
    except Exception as e:
        logger.critical(f"Failed to start server: {e}", exc_info=True)
