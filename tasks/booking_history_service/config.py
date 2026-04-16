import os


class Settings:
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5434"))
    DB_USER: str = os.getenv("DB_USER", "booking_history")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "booking_history")
    DB_NAME: str = os.getenv("DB_NAME", "booking_history_service")

    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    KAFKA_BOOKING_TOPIC: str = os.getenv("KAFKA_BOOKING_TOPIC", "booking-events")
    KAFKA_CONSUMER_GROUP: str = os.getenv("KAFKA_CONSUMER_GROUP", "booking-history-service")

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
