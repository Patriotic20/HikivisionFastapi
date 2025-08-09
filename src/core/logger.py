import logging

# Configure logging once here
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("hikvision_events.log", encoding="utf-8")
    ]
)

# Create a global logger with a consistent name
logger = logging.getLogger("hikvision")
