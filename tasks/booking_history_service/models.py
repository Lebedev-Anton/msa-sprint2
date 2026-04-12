"""
Database models for BookingHistoryService.
"""

from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BookingHistory(Base):
    __tablename__ = "booking_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    hotel_id = Column(String, nullable=False)
    promo_code = Column(String, nullable=True)
    discount_percent = Column(Float, default=0.0)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    saved_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (
            f"<BookingHistory(booking_id={self.booking_id}, "
            f"user_id={self.user_id}, hotel_id={self.hotel_id}, "
            f"price={self.price})>"
        )
