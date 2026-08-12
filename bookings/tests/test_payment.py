from unittest.mock import Mock, patch

import requests

from bookings.payment_service import process_payment


@patch("bookings.payment_service.requests.post")
def test_payment_success(mock_post):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None

    mock_post.return_value = mock_response

    result = process_payment("500.00", 1)

    assert result["success"] is True
    assert result["message"] == "Payment processed successfully."
    assert "transaction_id" in result

    mock_post.assert_called_once()


@patch("bookings.payment_service.requests.post")
def test_payment_service_failure(mock_post):
    mock_post.side_effect = requests.exceptions.RequestException(
        "External service failed"
    )

    result = process_payment("500.00", 1)

    assert result["success"] is False
    assert result["message"] == "Payment service is unavailable."


@patch("bookings.payment_service.requests.post")
def test_payment_service_timeout(mock_post):
    mock_post.side_effect = requests.exceptions.Timeout()

    result = process_payment("500.00", 1)

    assert result["success"] is False
    assert result["message"] == "Payment service timed out."