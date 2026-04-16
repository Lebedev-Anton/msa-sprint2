from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, BigInteger, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Booking(Base):
    __tablename__ = "booking"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=True)
    hotel_id = Column(String, nullable=True)
    promo_code = Column(String, nullable=True)
    discount_percent = Column(Float, nullable=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
