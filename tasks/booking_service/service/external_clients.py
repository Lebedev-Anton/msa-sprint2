import logging
from typing import Optional

import requests

from booking_service import config

logger = logging.getLogger(__name__)


class ExternalServiceError(Exception):
    """Raised when an external service call fails."""

    pass


class UserClient:
    """Client for AppUserService REST API calls."""

    @staticmethod
    def _parse_bool(resp_json) -> bool:
        """Handle both JSON bool and string responses."""
        if isinstance(resp_json, bool):
            return resp_json
        return resp_json.strip().lower() == "true"

    def is_user_active(self, user_id: str) -> bool:
        resp = requests.get(f"{config.settings.USER_SERVICE_URL}/{user_id}/active", timeout=10)
        resp.raise_for_status()
        return self._parse_bool(resp.json())

    def is_user_blacklisted(self, user_id: str) -> bool:
        resp = requests.get(f"{config.settings.USER_SERVICE_URL}/{user_id}/blacklisted", timeout=10)
        resp.raise_for_status()
        return self._parse_bool(resp.json())

    @staticmethod
    def get_user_status(user_id: str) -> Optional[str]:
        try:
            resp = requests.get(f"{config.settings.USER_SERVICE_URL}/{user_id}/status", timeout=10)
            resp.raise_for_status()
            return resp.text
        except requests.HTTPError:
            return None


class HotelClient:
    """Client for HotelService REST API calls."""

    @staticmethod
    def _parse_bool(resp_json) -> bool:
        if isinstance(resp_json, bool):
            return resp_json
        return resp_json.strip().lower() == "true"

    def is_hotel_operational(self, hotel_id: str) -> bool:
        resp = requests.get(f"{config.settings.HOTEL_SERVICE_URL}/{hotel_id}/operational", timeout=10)
        resp.raise_for_status()
        return self._parse_bool(resp.json())

    def is_hotel_fully_booked(self, hotel_id: str) -> bool:
        resp = requests.get(f"{config.settings.HOTEL_SERVICE_URL}/{hotel_id}/fully-booked", timeout=10)
        resp.raise_for_status()
        return self._parse_bool(resp.json())


class ReviewClient:
    """Client for ReviewService REST API calls."""

    @staticmethod
    def _parse_bool(resp_json) -> bool:
        if isinstance(resp_json, bool):
            return resp_json
        return resp_json.strip().lower() == "true"

    def is_trusted_hotel(self, hotel_id: str) -> bool:
        resp = requests.get(f"{config.settings.REVIEW_SERVICE_URL}/hotel/{hotel_id}/trusted", timeout=10)
        resp.raise_for_status()
        return self._parse_bool(resp.json())


class PromoClient:
    """Client for PromoCodeService REST API calls."""

    @staticmethod
    def validate_promo(promo_code: str, user_id: str) -> Optional[dict]:
        """
        Validate promo code for a user.
        Returns the promo code dict if valid, None otherwise.
        Mirrors PromoCodeService.validate() logic.
        """
        try:
            resp = requests.post(
                f"{config.settings.PROMO_SERVICE_URL}/validate",
                params={"code": promo_code, "userId": user_id},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError:
            logger.info("Promo code '%s' is invalid or not applicable for user %s", promo_code, user_id)
            return None
