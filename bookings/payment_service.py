import logging

import requests


logger = logging.getLogger(__name__)
MOCK_PAYMENT_URL = "https://httpbin.org/post"

def process_payment(amount, booking_id):
    payload = {
        "amount": str(amount),
        "booking_id": booking_id,
    }

    try:
        response = requests.post(
            MOCK_PAYMENT_URL,
            json=payload,
            timeout=5,
        )

        response.raise_for_status()

        logger.info(
            "Payment request successful for booking %s",
            booking_id,
        )

        return {
            "success": True,
            "message": "Payment processed successfully.",
        }

    except requests.exceptions.Timeout:
        logger.error(
            "Payment request timed out for booking %s",
            booking_id,
        )

        return {
            "success": False,
            "message": "Payment service timed out.",
        }

    except requests.exceptions.RequestException as exc:
        logger.error(
            "Payment request failed for booking %s: %s",
            booking_id,
            exc,
        )

        return {
            "success": False,
            "message": "Payment service is unavailable.",
        }