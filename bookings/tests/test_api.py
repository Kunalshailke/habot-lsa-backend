from rest_framework.test import APITestCase
from rest_framework import status

from bookings.models import Parent, Skill, LSAProfile, BookingRequest, Booking, Payment

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from unittest.mock import patch

class BookingAPITests(APITestCase):

    def test_create_booking_success(self):
        data = {
            "parent": self.parent.id,
            "required_skill": self.skill.id,
            "start_time": "2026-08-20T10:00:00Z",
            "end_time": "2026-08-20T12:00:00Z",
        }

        response = self.client.post(
            "/api/v1/bookings/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_create_booking_validation_failure(self):
        data = {
            "parent": self.parent.id,
            "required_skill": self.skill.id,
            "start_time": "2026-08-20T12:00:00Z",
            "end_time": "2026-08-20T10:00:00Z",
        }

        response = self.client.post(
            "/api/v1/bookings/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_lsa_search_by_skill(self):
        lsa = LSAProfile.objects.create(
            name="Test LSA",
            email="testlsa@example.com",
            phone="8888888888",
            is_available=True,
        )

        lsa.skills.add(self.skill)

        response = self.client.get(
            "/api/v1/lsas/search/?skill=Python"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_unavailable_lsa_not_returned(self):
        lsa = LSAProfile.objects.create(
            name="Unavailable LSA",
            email="unavailable@example.com",
            phone="7777777777",
            is_available=False,
        )

        lsa.skills.add(self.skill)

        response = self.client.get(
            "/api/v1/lsas/search/?skill=Python"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            0,
        )


    @patch("bookings.views.process_payment")
    def test_confirm_booking_request_success(self, mock_payment):
        mock_payment.return_value = {
            "success": True,
            "message": "Payment processed successfully.",
            "transaction_id": "txn-test-123",
        }

        parent = Parent.objects.create(
            name="Test Parent",
            email="confirm@example.com",
            phone="1234567890",
        )

        skill = Skill.objects.create(
            name="ConfirmationSkill"
        )

        lsa = LSAProfile.objects.create(
            name="Test LSA",
            email="confirm-lsa@example.com",
            phone="9876543210",
            is_available=True,
        )

        lsa.skills.add(skill)

        booking_request = BookingRequest.objects.create(
            parent=parent,
            required_skill=skill,
            preferred_lsa=lsa,
            start_time="2026-08-15T10:00:00Z",
            end_time="2026-08-15T12:00:00Z",
        )

        response = self.client.post(
            f"/api/v1/booking-requests/{booking_request.id}/confirm/"
        )

        self.assertEqual(response.status_code, 201)

        booking_request.refresh_from_db()

        self.assertEqual(
            booking_request.status,
            "ACCEPTED",
        )

        self.assertEqual(
            response.data["lsa"],
            lsa.id,
        )


    def test_confirm_booking_request_unavailable_lsa(self):

        parent = Parent.objects.create(
            name="Unavailable Parent",
            email="unavailable@example.com",
            phone="1234567890",
        )

        skill = Skill.objects.create(
            name="UnavailableSkill"
        )

        lsa = LSAProfile.objects.create(
            name="Unavailable LSA",
            email="unavailable-lsa@example.com",
            phone="9876543210",
            is_available=False,
        )

        lsa.skills.add(skill)

        booking_request = BookingRequest.objects.create(
            parent=parent,
            required_skill=skill,
            preferred_lsa=lsa,
            start_time="2026-08-15T10:00:00Z",
            end_time="2026-08-15T12:00:00Z",
        )

        response = self.client.post(
            f"/api/v1/booking-requests/{booking_request.id}/confirm/"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("unavailable", response.data["error"].lower())


    def test_confirm_booking_request_missing_skill(self):

        parent = Parent.objects.create(
            name="Skill Parent",
            email="skill@example.com",
            phone="1234567890",
        )

        required_skill = Skill.objects.create(
            name="RequiredSkill"
        )

        other_skill = Skill.objects.create(
            name="OtherSkill"
        )

        lsa = LSAProfile.objects.create(
            name="Wrong Skill LSA",
            email="wrong-skill@example.com",
            phone="9876543210",
            is_available=True,
        )

        lsa.skills.add(other_skill)

        booking_request = BookingRequest.objects.create(
            parent=parent,
            required_skill=required_skill,
            preferred_lsa=lsa,
            start_time="2026-08-16T10:00:00Z",
            end_time="2026-08-16T12:00:00Z",
        )

        response = self.client.post(
            f"/api/v1/booking-requests/{booking_request.id}/confirm/"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("required skill", response.data["error"].lower())


    def test_confirm_booking_request_booking_conflict(self):

        parent = Parent.objects.create(
            name="Conflict Parent",
            email="conflict@example.com",
            phone="1234567890",
        )

        skill = Skill.objects.create(
            name="ConflictSkill"
        )

        lsa = LSAProfile.objects.create(
            name="Conflict LSA",
            email="conflict-lsa@example.com",
            phone="9876543210",
            is_available=True,
        )

        lsa.skills.add(skill)

        existing_request = BookingRequest.objects.create(
            parent=parent,
            required_skill=skill,
            preferred_lsa=lsa,
            start_time="2026-08-17T10:00:00Z",
            end_time="2026-08-17T12:00:00Z",
        )

        Booking.objects.create(
            booking_request=existing_request,
            parent=parent,
            lsa=lsa,
            start_time="2026-08-17T10:00:00Z",
            end_time="2026-08-17T12:00:00Z",
            status="CONFIRMED",
        )

        new_request = BookingRequest.objects.create(
            parent=parent,
            required_skill=skill,
            preferred_lsa=lsa,
            start_time="2026-08-17T11:00:00Z",
            end_time="2026-08-17T13:00:00Z",
        )

        response = self.client.post(
            f"/api/v1/booking-requests/{new_request.id}/confirm/"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("overlapping", response.data["error"].lower())



    def setUp(self):
        self.parent = Parent.objects.create(
            name="Test Parent",
            email="testparent@example.com",
            phone="9999999999",
        )

        self.skill = Skill.objects.create(
            name="Python",
        )

        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
        )

        self.token = Token.objects.create(
            user=self.user
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )


    def test_booking_requires_authentication(self):

        self.client.credentials()

        response = self.client.post(
            "/api/v1/bookings/",
            {}
        )

        self.assertEqual(response.status_code, 401)


    def test_api_root(self):
        response = self.client.get("/api/v1/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["status"],
            "ok",
        )

    @patch("bookings.views.process_payment")
    def test_confirm_booking_creates_payment(self, mock_payment):

        mock_payment.return_value = {
            "success": True,
            "message": "Payment processed successfully.",
            "transaction_id": "txn-test-123",
        }

        parent = Parent.objects.create(
            name="Payment Parent",
            email="payment-parent@example.com",
            phone="1234567890",
        )

        skill = Skill.objects.create(
            name="PaymentSkill",
        )

        lsa = LSAProfile.objects.create(
            name="Payment LSA",
            email="payment-lsa@example.com",
            phone="9876543210",
            is_available=True,
        )

        lsa.skills.add(skill)

        booking_request = BookingRequest.objects.create(
            parent=parent,
            required_skill=skill,
            preferred_lsa=lsa,
            start_time="2026-09-01T10:00:00Z",
            end_time="2026-09-01T12:00:00Z",
        )

        response = self.client.post(
            f"/api/v1/booking-requests/{booking_request.id}/confirm/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        booking = Booking.objects.get(
            booking_request=booking_request,
        )

        payment = Payment.objects.get(
            booking=booking,
        )

        self.assertEqual(payment.status, "SUCCESS")
        self.assertEqual(
            payment.transaction_id,
            "txn-test-123",
        )

        mock_payment.assert_called_once()


    def test_payment_webhook_success(self):
        parent = Parent.objects.create(
            name="Webhook Parent",
            email="webhook@example.com",
            phone="1234567890",
        )

        skill = Skill.objects.create(
            name="WebhookSkill",
        )

        lsa = LSAProfile.objects.create(
            name="Webhook LSA",
            email="webhook-lsa@example.com",
            phone="9876543210",
            is_available=True,
        )

        lsa.skills.add(skill)

        booking_request = BookingRequest.objects.create(
            parent=parent,
            required_skill=skill,
            preferred_lsa=lsa,
            start_time="2026-12-01T10:00:00Z",
            end_time="2026-12-01T12:00:00Z",
            status="ACCEPTED",
        )

        booking = Booking.objects.create(
            booking_request=booking_request,
            parent=parent,
            lsa=lsa,
            start_time="2026-12-01T10:00:00Z",
            end_time="2026-12-01T12:00:00Z",
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
                "transaction_id": "webhook-txn-123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        payment.refresh_from_db()
        booking.refresh_from_db()

        self.assertEqual(payment.status, "SUCCESS")
        self.assertEqual(
            payment.transaction_id,
            "webhook-txn-123",
        )
        self.assertEqual(booking.status, "CONFIRMED")



    def test_payment_webhook_failure(self):
        parent = Parent.objects.create(
            name="Webhook Failure Parent",
            email="webhook-failure@example.com",
            phone="1234567890",
        )

        skill = Skill.objects.create(
            name="WebhookFailureSkill",
        )

        lsa = LSAProfile.objects.create(
            name="Webhook Failure LSA",
            email="webhook-failure-lsa@example.com",
            phone="9876543210",
            is_available=True,
        )

        lsa.skills.add(skill)

        booking_request = BookingRequest.objects.create(
            parent=parent,
            required_skill=skill,
            preferred_lsa=lsa,
            start_time="2026-12-02T10:00:00Z",
            end_time="2026-12-02T12:00:00Z",
            status="ACCEPTED",
        )

        booking = Booking.objects.create(
            booking_request=booking_request,
            parent=parent,
            lsa=lsa,
            start_time="2026-12-02T10:00:00Z",
            end_time="2026-12-02T12:00:00Z",
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
                "transaction_id": "webhook-failed-123",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        payment = Payment.objects.get(
            booking=booking,
        )

        booking.refresh_from_db()

        self.assertEqual(payment.status, "FAILED")
        self.assertEqual(
            payment.transaction_id,
            "webhook-failed-123",
        )
        self.assertEqual(
            booking.status,
            "CANCELLED",
        )