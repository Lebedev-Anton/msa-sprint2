"""
gRPC server for BookingService.
Implements the BookingService defined in booking.proto.
"""

import logging
import sys
import os
from concurrent import futures

# Add parent directory to path so booking_service package can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

import grpc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from booking_service.config import settings
from booking_service.service.booking_pb2 import (
    BookingServiceServicer,
    add_BookingServiceServicer_to_server,
)
from booking_service.service.models import Base
from booking_service.service.service import BookingService

logger = logging.getLogger(__name__)

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)


class BookingServicer(BookingServiceServicer):
    """gRPC servicer that delegates to BookingService business logic."""

    def _get_db_session(self):
        return SessionLocal()

    def CreateBooking(self, request, context):
        logger.info("Received CreateBooking request")
        session = self._get_db_session()
        try:
            booking_svc = BookingService(session)
            result = booking_svc.create_booking(request, context)
            logger.info("CreateBooking completed successfully")
            return result
        except ValueError as exc:
            logger.error("CreateBooking failed: %s", exc)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(exc))
            from tasks.booking_service.service.booking_pb2 import BookingResponse
            return BookingResponse()
        finally:
            session.close()

    def ListBookings(self, request, context):
        logger.info("Received ListBookings request")
        session = self._get_db_session()
        try:
            booking_svc = BookingService(session)
            result = booking_svc.list_bookings(request, context)
            logger.info("ListBookings completed successfully")
            return result
        finally:
            session.close()


def serve():
    logger.info("Creating database tables if they don't exist")
    Base.metadata.create_all(engine)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_BookingServiceServicer_to_server(BookingServicer(), server)
    server.add_insecure_port(f"[::]:{settings.APP_PORT}")

    logger.info("Starting gRPC BookingService on port %s", settings.APP_PORT)
    server.start()
    logger.info("gRPC server is running and accepting requests")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
