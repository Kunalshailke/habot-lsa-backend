from unittest.mock import patch

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from bookings.models import (
    Booking,
    BookingRequest,
    LSAProfile,
    Parent,
    Payment,
    Skill,
)


class BookingAPITests(APITestCase):

    def setUp(self):
        self.parent = Parent.objects.create(
            name="Test Parent",
            email="parent@example.com",
            phone="9999999999",
        )

        self.skill = Skill.objects.create(name="Python")

        user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )

        token = Token.objects.create(user=user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def create_lsa(self, available=True):
        lsa = LSAProfile.objects.create(
            name="Test LSA",
            email="lsa@example.com",
            phone="8888888888",
            is_available=available,
        )
        lsa.skills.add(self.skill)
        return lsa

    def create_request(self, lsa):
        return BookingRequest.objects.create(
            parent=self.parent,
            required_skill=self.skill,
            preferred_lsa=lsa,
            start_time="2026-08-20T10:00:00Z",
            end_time="2026-08-20T12:00:00Z",
        )

    def test_create_booking_request(self):
        response = self.client.post(
            "/api/v1/bookings/",
            {
                "parent": self.parent.id,
                "required_skill": self.skill.id,
                "start_time": "2026-08-20T10:00:00Z",
                "end_time": "2026-08-20T12:00:00Z",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_invalid_booking_time(self):
        response = self.client.post(
            "/api/v1/bookings/",
            {
                "parent": self.parent.id,
                "required_skill": self.skill.id,
                "start_time": "2026-08-20T12:00:00Z",
                "end_time": "2026-08-20T10:00:00Z",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_lsa_search_by_skill(self):
        self.create_lsa()

        response = self.client.get(
            "/api/v1/lsas/search/?skill=Python"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)

    def test_unavailable_lsa_is_not_returned(self):
        self.create_lsa(available=False)

        response = self.client.get(
            "/api/v1/lsas/search/?skill=Python"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 0)

    @patch("bookings.views.process_payment")
    def test_confirm_booking_creates_payment(self, mock_payment):
        mock_payment.return_value = {
            "success": True,
            "message": "Payment processed successfully.",
            "transaction_id": "txn-test-123",
        }

        lsa = self.create_lsa()
        booking_request = self.create_request(lsa)

        response = self.client.post(
            f"/api/v1/booking-requests/{booking_request.id}/confirm/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        booking = Booking.objects.get(
            booking_request=booking_request
        )

        payment = Payment.objects.get(booking=booking)

        self.assertEqual(payment.status, "SUCCESS")
        self.assertEqual(
            payment.transaction_id,
            "txn-test-123",
        )

        booking_request.refresh_from_db()
        self.assertEqual(booking_request.status, "ACCEPTED")

    def test_booking_conflict_is_rejected(self):
        lsa = self.create_lsa()

        first_request = self.create_request(lsa)

        Booking.objects.create(
            booking_request=first_request,
            parent=self.parent,
            lsa=lsa,
            start_time="2026-08-20T10:00:00Z",
            end_time="2026-08-20T12:00:00Z",
            status="CONFIRMED",
        )

        second_request = BookingRequest.objects.create(
            parent=self.parent,
            required_skill=self.skill,
            preferred_lsa=lsa,
            start_time="2026-08-20T11:00:00Z",
            end_time="2026-08-20T13:00:00Z",
        )

        response = self.client.post(
            f"/api/v1/booking-requests/{second_request.id}/confirm/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_payment_webhook_success(self):
        lsa = self.create_lsa()
        booking_request = self.create_request(lsa)
        booking_request.status = "ACCEPTED"
        booking_request.save()

        booking = Booking.objects.create(
            booking_request=booking_request,
            parent=self.parent,
            lsa=lsa,
            start_time=booking_request.start_time,
            end_time=booking_request.end_time,
            status="CONFIRMED",
        )

        payment = Payment.objects.create(
            booking=booking,
            amount="500.00",
            status="PENDING",
        )

        response = self.client.post(
            "/api/v1/payments/webhook/",
            {
                "booking_id": booking.id,
                "status": "SUCCESS",
                "transaction_id": "webhook-123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        payment.refresh_from_db()

        self.assertEqual(payment.status, "SUCCESS")
        self.assertEqual(
            payment.transaction_id,
            "webhook-123",
        )

    def test_payment_webhook_failure(self):
        lsa = self.create_lsa()
        booking_request = self.create_request(lsa)
        booking_request.status = "ACCEPTED"
        booking_request.save()

        booking = Booking.objects.create(
            booking_request=booking_request,
            parent=self.parent,
            lsa=lsa,
            start_time=booking_request.start_time,
            end_time=booking_request.end_time,
            status="CONFIRMED",
        )

        Payment.objects.create(
            booking=booking,
            amount="500.00",
            status="PENDING",
        )

        response = self.client.post(
            "/api/v1/payments/webhook/",
            {
                "booking_id": booking.id,
                "status": "FAILED",
                "transaction_id": "webhook-failed",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        booking.refresh_from_db()

        payment = Payment.objects.get(booking=booking)

        self.assertEqual(payment.status, "FAILED")
        self.assertEqual(booking.status, "CANCELLED")

    def test_booking_requires_authentication(self):
        self.client.credentials()

        response = self.client.post(
            "/api/v1/bookings/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )