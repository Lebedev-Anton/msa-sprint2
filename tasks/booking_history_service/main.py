"""
Main entry point for BookingHistoryService.
Reads booking events from Kafka and saves them to the database.
"""

import logging
import os
import signal
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from booking_history_service.config import settings
from booking_history_service.consumer import BookingKafkaConsumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    logger.info("Starting BookingHistoryService")
    logger.info("Kafka servers: %s", settings.KAFKA_BOOTSTRAP_SERVERS)
    logger.info("Kafka topic: %s", settings.KAFKA_BOOKING_TOPIC)
    logger.info("Consumer group: %s", settings.KAFKA_CONSUMER_GROUP)

    consumer = BookingKafkaConsumer()

    def shutdown_handler(signum, frame):
        logger.info("Received signal %s, shutting down...", signum)
        consumer.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        consumer.initialize()
        consumer.consume()
    except Exception as e:
        logger.error("Fatal error in BookingHistoryService: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
