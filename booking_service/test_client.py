#!/usr/bin/env python3
"""Quick smoke test for the gRPC BookingService."""

import grpc
import sys
import os

# Add project root to path so imports resolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service.booking_pb2 import BookingRequest, BookingListRequest, BookingListResponse, BookingResponse

LIST_METHOD = "/booking.BookingService/ListBookings"
CREATE_METHOD = "/booking.BookingService/CreateBooking"


def run():
    channel = grpc.insecure_channel("localhost:9090")

    # --- Test ListBookings ---
    print("=== ListBookings ===")
    req = BookingListRequest(user_id="test-user-2")
    resp_bytes = channel.unary_unary(LIST_METHOD)(req.SerializeToString())
    resp = BookingListResponse.FromString(resp_bytes)
    print(f"Total bookings: {len(resp.bookings)}")
    for b in resp.bookings:
        print(f"  id={b.id}, user={b.user_id}, hotel={b.hotel_id}, price={b.price}")

    # --- Test CreateBooking ---
    print("\n=== CreateBooking ===")
    req = BookingRequest(user_id="test-user-2", hotel_id="test-hotel-1", promo_code="TESTCODE1")
    try:
        resp_bytes = channel.unary_unary(CREATE_METHOD)(req.SerializeToString())
        resp = BookingResponse.FromString(resp_bytes)
        print(f"Created: id={resp.id}, price={resp.price}, discount={resp.discount_percent}")
    except grpc.RpcError as e:
        print(f"Error: {e.code()} - {e.details()}")

    channel.close()
    print("\n✅ Service is reachable and responding!")


if __name__ == "__main__":
    run()
