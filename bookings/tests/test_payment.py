from unittest.mock import Mock, patch

import requests

from bookings.payment_service import process_payment


@patch("bookings.payment_service.requests.post")
def test_payment_success(mock_post):
    mock_post.return_value = Mock()

    result = process_payment("500.00", 1)

    assert result["success"] is True
    assert result["message"] == "Payment processed successfully."
    assert "transaction_id" in result


@patch("bookings.payment_service.requests.post")
def test_payment_service_failure(mock_post):
    mock_post.side_effect = requests.exceptions.RequestException()

    result = process_payment("500.00", 1)

    assert result["success"] is False
    assert result["message"] == "Payment service is unavailable."


@patch("bookings.payment_service.requests.post")
def test_payment_service_timeout(mock_post):
    mock_post.side_effect = requests.exceptions.Timeout()

    result = process_payment("500.00", 1)

    assert result["success"] is False
    assert result["message"] == "Payment service timed out."