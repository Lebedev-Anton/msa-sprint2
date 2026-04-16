import logging
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from booking_service.service.booking_pb2 import (
    BookingRequest,
    BookingResponse,
    BookingListRequest,
    BookingListResponse,
)
from booking_service.service.external_clients import HotelClient, PromoClient, ReviewClient, UserClient
from booking_service.service.models import Booking
from booking_service.service.kafka_producer import kafka_producer

logger = logging.getLogger(__name__)

# Price constants matching the Java implementation
VIP_BASE_PRICE = 80.0
STANDARD_BASE_PRICE = 100.0


class BookingService:
    """
    Python port of the Java BookingService.
    All dependencies (PromoCodeService, ReviewService, AppUserService, HotelService)
    are replaced with REST API calls via external_clients module.
    Operates on protobuf messages for gRPC communication.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.user_client = UserClient()
        self.hotel_client = HotelClient()
        self.review_client = ReviewClient()
        self.promo_client = PromoClient()

    # ------------------------------------------------------------------
    # gRPC handlers
    # ------------------------------------------------------------------

    def create_booking(self, request: BookingRequest, context) -> BookingResponse:
        logger.info("Creating booking: userId=%s, hotelId=%s, promoCode=%s",
                     request.user_id, request.hotel_id, request.promo_code)

        self._validate_user(request.user_id)
        self._validate_hotel(request.hotel_id)

        base_price = self._resolve_base_price(request.user_id)
        discount = self._resolve_promo_discount(request.promo_code or None, request.user_id)

        final_price = base_price - discount
        logger.info("Final price calculated: base=%s, discount=%s, final=%s",
                     base_price, discount, final_price)

        booking = Booking(
            user_id=request.user_id,
            hotel_id=request.hotel_id,
            promo_code=request.promo_code or None,
            discount_percent=discount,
            price=final_price,
        )

        self.db_session.add(booking)
        self.db_session.commit()
        self.db_session.refresh(booking)

        # Send booking event to Kafka
        booking_data = {
            "id": str(booking.id),
            "user_id": booking.user_id or "",
            "hotel_id": booking.hotel_id or "",
            "promo_code": booking.promo_code or "",
            "discount_percent": booking.discount_percent or 0.0,
            "price": booking.price,
            "created_at": booking.created_at.isoformat() if booking.created_at else "",
        }
        
        kafka_producer.send_booking_event(booking_data)

        return BookingResponse(
            id=str(booking.id),
            user_id=booking.user_id or "",
            hotel_id=booking.hotel_id or "",
            promo_code=booking.promo_code or "",
            discount_percent=booking.discount_percent or 0.0,
            price=booking.price,
            created_at=booking.created_at.isoformat() if booking.created_at else "",
        )

    def list_bookings(self, request: BookingListRequest, context) -> BookingListResponse:
        user_id = request.user_id or None
        if user_id is not None:
            bookings = self.db_session.query(Booking).filter(Booking.user_id == user_id).all()
        else:
            bookings = self.db_session.query(Booking).all()

        responses = []
        for b in bookings:
            responses.append(BookingResponse(
                id=str(b.id),
                user_id=b.user_id or "",
                hotel_id=b.hotel_id or "",
                promo_code=b.promo_code or "",
                discount_percent=b.discount_percent or 0.0,
                price=b.price,
                created_at=b.created_at.isoformat() if b.created_at else "",
            ))
        return BookingListResponse(bookings=responses)

    # ------------------------------------------------------------------
    # Internal validation / business logic (same as original Java)
    # ------------------------------------------------------------------

    def _validate_user(self, user_id: str) -> None:
        if not self.user_client.is_user_active(user_id):
            logger.warning("User %s is inactive", user_id)
            raise ValueError("User is inactive")

        if self.user_client.is_user_blacklisted(user_id):
            logger.warning("User %s is blacklisted", user_id)
            raise ValueError("User is blacklisted")

    def _validate_hotel(self, hotel_id: str) -> None:
        if not self.hotel_client.is_hotel_operational(hotel_id):
            logger.warning("Hotel %s is not operational", hotel_id)
            raise ValueError("Hotel is not operational")

        if not self.review_client.is_trusted_hotel(hotel_id):
            logger.warning("Hotel %s is not trusted", hotel_id)
            raise ValueError("Hotel is not trusted based on reviews")

        if self.hotel_client.is_hotel_fully_booked(hotel_id):
            logger.warning("Hotel %s is fully booked", hotel_id)
            raise ValueError("Hotel is fully booked")

    def _resolve_base_price(self, user_id: str) -> float:
        status = self.user_client.get_user_status(user_id)
        if status is not None:
            is_vip = status.strip().upper() == "VIP"
            logger.debug("User %s has status '%s', base price is %s",
                         user_id, status, VIP_BASE_PRICE if is_vip else STANDARD_BASE_PRICE)
            return VIP_BASE_PRICE if is_vip else STANDARD_BASE_PRICE

        logger.debug("User %s has unknown status, default base price %s",
                     user_id, STANDARD_BASE_PRICE)
        return STANDARD_BASE_PRICE

    def _resolve_promo_discount(self, promo_code: Optional[str], user_id: str) -> float:
        if promo_code is None:
            return 0.0

        promo = self.promo_client.validate_promo(promo_code, user_id)
        if promo is None:
            logger.info("Promo code '%s' is invalid or not applicable for user %s",
                        promo_code, user_id)
            return 0.0

        discount = promo.get("discount", 0.0)
        logger.debug("Promo code '%s' applied with discount %s", promo_code, discount)
        return discount
