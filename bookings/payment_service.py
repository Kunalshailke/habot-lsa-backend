import logging
import uuid

logger = logging.getLogger(__name__)


def process_payment(amount, booking_id):
    """
    Simulated payment service.

    This project does not use a real payment gateway.
    Payment is simulated locally so the API does not depend
    on an external service being available.
    """

    logger.info(
        "Payment processed successfully for booking %s",
        booking_id,
    )

    return {
        "success": True,
        "message": "Payment processed successfully.",
        "transaction_id": str(uuid.uuid4()),
    }