import os
import uuid

import requests


MOCK_PAYMENT_URL = os.getenv(
    "MOCK_PAYMENT_URL",
    "http://127.0.0.1:8000/api/v1/payments/mock/",
)


def process_payment(amount, booking_id):
    try:
        response = requests.post(
            MOCK_PAYMENT_URL,
            json={
                "amount": str(amount),
                "booking_id": booking_id,
            },
            timeout=5,
        )

        response.raise_for_status()

        return {
            "success": True,
            "message": "Payment processed successfully.",
            "transaction_id": str(uuid.uuid4()),
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "Payment service timed out.",
        }

    except requests.exceptions.RequestException:
        return {
            "success": False,
            "message": "Payment service is unavailable.",
        }