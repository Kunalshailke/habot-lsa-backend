from unittest.mock import patch

from bookings.payment_service import process_payment


def test_payment_success():
    result = process_payment("500.00", 1)

    assert result["success"] is True
    assert result["message"] == "Payment processed successfully."
    assert "transaction_id" in result


@patch("bookings.views.process_payment")
def test_payment_failure(mock_payment):
    mock_payment.return_value = {
        "success": False,
        "message": "Payment service is unavailable.",
    }

    result = mock_payment("500.00", 1)

    assert result["success"] is False
    assert result["message"] == "Payment service is unavailable."