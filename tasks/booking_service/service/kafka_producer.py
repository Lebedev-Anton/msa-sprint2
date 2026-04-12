"""
Kafka producer utility for sending booking events.
"""

import json
import logging
import time
from typing import Any, Dict, Optional

from kafka import KafkaProducer
from kafka.errors import KafkaError

from booking_service.config import settings

logger = logging.getLogger(__name__)


class BookingKafkaProducer:
    """Singleton Kafka producer for sending booking events with lazy initialization."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._producer: Optional[KafkaProducer] = None
            cls._instance._initialized = False
        return cls._instance

    def _get_producer(self) -> Optional[KafkaProducer]:
        """Get or create Kafka producer with lazy initialization."""
        if self._producer is not None:
            return self._producer

        max_retries = 5
        retry_delay = 2

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    "Initializing Kafka producer (attempt %d/%d), servers=%s",
                    attempt, max_retries, settings.KAFKA_BOOTSTRAP_SERVERS
                )
                self._producer = KafkaProducer(
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda v: v.encode('utf-8') if v else None,
                    acks='all',
                    retries=3,
                    max_block_ms=5000,
                )
                self._initialized = True
                logger.info("Kafka producer initialized successfully")
                return self._producer
            except KafkaError as e:
                logger.warning(
                    "Failed to initialize Kafka producer (attempt %d/%d): %s",
                    attempt, max_retries, e
                )
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    logger.error(
                        "Failed to initialize Kafka producer after %d attempts. "
                        "Booking events will not be sent to Kafka.",
                        max_retries
                    )
                    self._initialized = True
                    return None

        return None

    def send_booking_event(self, booking_data: Dict[str, Any]) -> bool:
        """Send booking event to Kafka topic.
        
        Args:
            booking_data: Dictionary containing booking information.
            
        Returns:
            True if message was sent successfully, False otherwise.
        """
        producer = self._get_producer()
        if not producer:
            logger.warning("Kafka producer not available, skipping booking event")
            return False

        try:
            booking_id = booking_data.get("id", "unknown")
            future = producer.send(
                settings.KAFKA_BOOKING_TOPIC,
                key=booking_id,
                value=booking_data,
            )
            record_metadata = future.get(timeout=10)
            logger.info(
                "Booking event sent to topic=%s partition=%s offset=%s",
                record_metadata.topic,
                record_metadata.partition,
                record_metadata.offset,
            )
            return True
        except KafkaError as e:
            logger.error("Failed to send booking event to Kafka: %s", e)
            # Reset producer to allow reconnection on next attempt
            self._producer = None
            return False
        except Exception as e:
            logger.error("Unexpected error sending booking event to Kafka: %s", e)
            return False

    def close(self):
        """Close the Kafka producer."""
        if self._producer:
            try:
                self._producer.flush()
                self._producer.close()
                logger.info("Kafka producer closed")
            except Exception as e:
                logger.error("Error closing Kafka producer: %s", e)
            self._producer = None


# Global instance
kafka_producer = BookingKafkaProducer()
