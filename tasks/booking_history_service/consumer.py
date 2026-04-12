"""
Kafka consumer for reading booking events and saving to database.
"""

import json
import logging
import time

from kafka import KafkaConsumer
from kafka.errors import KafkaError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from booking_history_service.config import settings
from booking_history_service.models import Base, BookingHistory

logger = logging.getLogger(__name__)


class BookingKafkaConsumer:
    """Consumes booking events from Kafka and saves them to the database."""

    def __init__(self):
        self.engine = create_engine(settings.database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.consumer = None
        self._running = False

    def initialize(self):
        """Create database tables and initialize Kafka consumer."""
        # Create database tables
        logger.info("Creating database tables if they don't exist")
        Base.metadata.create_all(self.engine)

        # Initialize Kafka consumer
        max_retries = 5
        retry_delay = 3

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    "Initializing Kafka consumer (attempt %d/%d), servers=%s, topic=%s",
                    attempt, max_retries,
                    settings.KAFKA_BOOTSTRAP_SERVERS,
                    settings.KAFKA_BOOKING_TOPIC,
                )
                self.consumer = KafkaConsumer(
                    settings.KAFKA_BOOKING_TOPIC,
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    group_id=settings.KAFKA_CONSUMER_GROUP,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    key_deserializer=lambda m: m.decode('utf-8') if m else None,
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    consumer_timeout_ms=1000,
                )
                self._running = True
                logger.info("Kafka consumer initialized successfully")
                return
            except KafkaError as e:
                logger.warning(
                    "Failed to initialize Kafka consumer (attempt %d/%d): %s",
                    attempt, max_retries, e
                )
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    logger.error(
                        "Failed to initialize Kafka consumer after %d attempts",
                        max_retries
                    )
                    raise

    def consume(self):
        """Main loop to consume messages from Kafka."""
        if not self.consumer:
            logger.error("Kafka consumer not initialized")
            return

        logger.info("Starting to consume booking events from Kafka...")

        try:
            while self._running:
                # poll returns immediately with available messages
                messages = self.consumer.poll(timeout_ms=1000)

                for topic_partition, records in messages.items():
                    for record in records:
                        self._process_message(record.value)

        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error("Error in consume loop: %s", e)
        finally:
            self.stop()

    def _process_message(self, booking_data: dict):
        """Process a single booking message and save to database."""
        try:
            logger.info("Processing booking event: %s", booking_data)

            booking_id = booking_data.get("id")
            if not booking_id:
                logger.warning("Received booking event without id, skipping")
                return

            session = self.SessionLocal()
            try:
                # Check if booking already exists (idempotency)
                existing = (
                    session.query(BookingHistory)
                    .filter(BookingHistory.booking_id == booking_id)
                    .first()
                )

                if existing:
                    logger.info("Booking %s already exists in history, skipping", booking_id)
                    return

                booking_history = BookingHistory(
                    booking_id=booking_id,
                    user_id=booking_data.get("user_id", ""),
                    hotel_id=booking_data.get("hotel_id", ""),
                    promo_code=booking_data.get("promo_code"),
                    discount_percent=booking_data.get("discount_percent", 0.0),
                    price=booking_data.get("price", 0.0),
                    created_at=booking_data.get("created_at"),
                )

                session.add(booking_history)
                session.commit()
                logger.info(
                    "Booking %s saved to history successfully",
                    booking_id
                )

            except Exception as e:
                session.rollback()
                logger.error("Failed to save booking %s to history: %s", booking_id, e)
                raise
            finally:
                session.close()

        except Exception as e:
            logger.error("Error processing booking event: %s", e)

    def stop(self):
        """Stop the consumer and cleanup."""
        self._running = False
        if self.consumer:
            try:
                self.consumer.close()
                logger.info("Kafka consumer closed")
            except Exception as e:
                logger.error("Error closing Kafka consumer: %s", e)
