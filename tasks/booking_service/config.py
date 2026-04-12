import os


class Settings:
    # Database
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5433"))
    DB_USER: str = os.getenv("DB_USER", "booking")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "booking")
    DB_NAME: str = os.getenv("DB_NAME", "booking_service")

    # External service URLs
    USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://localhost:8084/api/users")
    HOTEL_SERVICE_URL: str = os.getenv("HOTEL_SERVICE_URL", "http://localhost:8084/api/hotels")
    REVIEW_SERVICE_URL: str = os.getenv("REVIEW_SERVICE_URL", "http://localhost:8084/api/reviews")
    PROMO_SERVICE_URL: str = os.getenv("PROMO_SERVICE_URL", "http://localhost:8084/api/promos")

    # Kafka settings
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_BOOKING_TOPIC: str = os.getenv("KAFKA_BOOKING_TOPIC", "booking-events")

    # App settings
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "9090"))

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
