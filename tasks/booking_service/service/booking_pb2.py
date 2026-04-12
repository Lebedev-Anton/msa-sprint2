# -*- coding: utf-8 -*-
"""
Hand-crafted protobuf serialization/deserialization for booking.proto messages.
Uses proper binary wire format (varint, length-delimited, double as fixed64).
"""

import struct
from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------------------
# Wire-format helpers (proto3)
# ---------------------------------------------------------------------------

def _varint_encode(value: int) -> bytes:
    out = bytearray()
    while value > 0x7F:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value & 0x7F)
    return bytes(out)


def _varint_decode(data: bytes, offset: int):
    result = 0
    shift = 0
    while True:
        b = data[offset]
        result |= (b & 0x7F) << shift
        offset += 1
        shift += 7
        if not (b & 0x80):
            break
    return result, offset


def _tag(field_number: int, wire_type: int) -> bytes:
    return _varint_encode((field_number << 3) | wire_type)


TAG_WIRE_VARINT = 0
TAG_WIRE_FIXED64 = 1
TAG_WIRE_LEN = 2

# Field numbers from booking.proto
# BookingRequest: user_id=1, hotel_id=2, promo_code=3
# BookingResponse: id=1, user_id=2, hotel_id=3, promo_code=4,
#                  discount_percent=5, price=6, created_at=7
# BookingListRequest: user_id=1
# BookingListResponse: bookings=1


# ---------------------------------------------------------------------------
# Message classes
# ---------------------------------------------------------------------------

@dataclass
class BookingRequest:
    user_id: str = ""
    hotel_id: str = ""
    promo_code: str = ""

    def SerializeToString(self) -> bytes:
        out = bytearray()
        if self.user_id:
            enc = self.user_id.encode("utf-8")
            out += _tag(1, TAG_WIRE_LEN) + _varint_encode(len(enc)) + enc
        if self.hotel_id:
            enc = self.hotel_id.encode("utf-8")
            out += _tag(2, TAG_WIRE_LEN) + _varint_encode(len(enc)) + enc
        if self.promo_code:
            enc = self.promo_code.encode("utf-8")
            out += _tag(3, TAG_WIRE_LEN) + _varint_encode(len(enc)) + enc
        return bytes(out)

    @classmethod
    def FromString(cls, data: bytes) -> "BookingRequest":
        obj = cls()
        offset = 0
        while offset < len(data):
            tag_val, offset = _varint_decode(data, offset)
            field_num = tag_val >> 3
            wire_type = tag_val & 0x07
            if wire_type == TAG_WIRE_LEN:
                length, offset = _varint_decode(data, offset)
                value = data[offset:offset + length].decode("utf-8")
                offset += length
                if field_num == 1:
                    obj.user_id = value
                elif field_num == 2:
                    obj.hotel_id = value
                elif field_num == 3:
                    obj.promo_code = value
            else:
                raise ValueError(f"Unexpected wire type {wire_type}")
        return obj


@dataclass
class BookingResponse:
    id: str = ""
    user_id: str = ""
    hotel_id: str = ""
    promo_code: str = ""
    discount_percent: float = 0.0
    price: float = 0.0
    created_at: str = ""

    def SerializeToString(self) -> bytes:
        out = bytearray()
        if self.id:
            enc = self.id.encode("utf-8")
            out += _tag(1, TAG_WIRE_LEN) + _varint_encode(len(enc)) + enc
        if self.user_id:
            enc = self.user_id.encode("utf-8")
            out += _tag(2, TAG_WIRE_LEN) + _varint_encode(len(enc)) + enc
        if self.hotel_id:
            enc = self.hotel_id.encode("utf-8")
            out += _tag(3, TAG_WIRE_LEN) + _varint_encode(len(enc)) + enc
        if self.promo_code:
            enc = self.promo_code.encode("utf-8")
            out += _tag(4, TAG_WIRE_LEN) + _varint_encode(len(enc)) + enc
        if self.discount_percent != 0.0:
            out += _tag(5, TAG_WIRE_FIXED64) + struct.pack("<d", self.discount_percent)
        if self.price != 0.0:
            out += _tag(6, TAG_WIRE_FIXED64) + struct.pack("<d", self.price)
        if self.created_at:
            enc = self.created_at.encode("utf-8")
            out += _tag(7, TAG_WIRE_LEN) + _varint_encode(len(enc)) + enc
        return bytes(out)

    @classmethod
    def FromString(cls, data: bytes) -> "BookingResponse":
        obj = cls()
        offset = 0
        while offset < len(data):
            tag_val, offset = _varint_decode(data, offset)
            field_num = tag_val >> 3
            wire_type = tag_val & 0x07
            if wire_type == TAG_WIRE_LEN:
                length, offset = _varint_decode(data, offset)
                value = data[offset:offset + length].decode("utf-8")
                offset += length
                if field_num == 1:
                    obj.id = value
                elif field_num == 2:
                    obj.user_id = value
                elif field_num == 3:
                    obj.hotel_id = value
                elif field_num == 4:
                    obj.promo_code = value
                elif field_num == 7:
                    obj.created_at = value
            elif wire_type == TAG_WIRE_FIXED64:
                value = struct.unpack("<d", data[offset:offset + 8])[0]
                offset += 8
                if field_num == 5:
                    obj.discount_percent = value
                elif field_num == 6:
                    obj.price = value
            else:
                raise ValueError(f"Unexpected wire type {wire_type}")
        return obj


@dataclass
class BookingListRequest:
    user_id: str = ""

    def SerializeToString(self) -> bytes:
        out = bytearray()
        if self.user_id:
            enc = self.user_id.encode("utf-8")
            out += _tag(1, TAG_WIRE_LEN) + _varint_encode(len(enc)) + enc
        return bytes(out)

    @classmethod
    def FromString(cls, data: bytes) -> "BookingListRequest":
        obj = cls()
        offset = 0
        while offset < len(data):
            tag_val, offset = _varint_decode(data, offset)
            field_num = tag_val >> 3
            wire_type = tag_val & 0x07
            if wire_type == TAG_WIRE_LEN:
                length, offset = _varint_decode(data, offset)
                obj.user_id = data[offset:offset + length].decode("utf-8")
                offset += length
        return obj


@dataclass
class BookingListResponse:
    bookings: List["BookingResponse"] = field(default_factory=list)

    def SerializeToString(self) -> bytes:
        out = bytearray()
        for booking in self.bookings:
            inner = booking.SerializeToString()
            out += _tag(1, TAG_WIRE_LEN) + _varint_encode(len(inner)) + inner
        return bytes(out)

    @classmethod
    def FromString(cls, data: bytes) -> "BookingListResponse":
        obj = cls()
        offset = 0
        while offset < len(data):
            tag_val, offset = _varint_decode(data, offset)
            field_num = tag_val >> 3
            wire_type = tag_val & 0x07
            if wire_type == TAG_WIRE_LEN:
                length, offset = _varint_decode(data, offset)
                inner_data = data[offset:offset + length]
                offset += length
                if field_num == 1:
                    obj.bookings.append(BookingResponse.FromString(inner_data))
        return obj


# ---------------------------------------------------------------------------
# gRPC Servicer
# ---------------------------------------------------------------------------

import grpc as _grpc


class BookingServiceServicer:
    """Must be subclassed to implement CreateBooking and ListBookings."""

    def CreateBooking(self, request: BookingRequest, context):
        context.set_code(_grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("UNIMPLEMENTED")
        return BookingResponse()

    def ListBookings(self, request: BookingListRequest, context):
        context.set_code(_grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("UNIMPLEMENTED")
        return BookingListResponse()


def add_BookingServiceServicer_to_server(servicer, server):
    """Register the servicer with the gRPC server."""

    rpc_method_handlers = {
        "CreateBooking": _grpc.unary_unary_rpc_method_handler(
            servicer.CreateBooking,
            request_deserializer=BookingRequest.FromString,
            response_serializer=BookingResponse.SerializeToString,
        ),
        "ListBookings": _grpc.unary_unary_rpc_method_handler(
            servicer.ListBookings,
            request_deserializer=BookingListRequest.FromString,
            response_serializer=BookingListResponse.SerializeToString,
        ),
    }
    generic_handler = _grpc.method_handlers_generic_handler(
        "booking.BookingService", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))
