import logging
from app.core.config import settings

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


if __name__ == "__main__":
    logger.info("Starting the application")

    print(settings.DATABASE_URL)