import logging

logger = logging.getLogger("myapp")
logger.setLevel(logging.ERROR)  # Set default level here

def setup_logging():
    # Only sets up logging once for the root logger
    logging.basicConfig(
        level=logging.ERROR,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]  # ensures only one handler
    )

# Set up logger only if it has no handlers (prevents duplicates)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
