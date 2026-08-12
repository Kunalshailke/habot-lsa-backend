from rest_framework.test import APITestCase
from rest_framework import status

from bookings.models import Parent, Skill, LSAProfile, BookingRequest, Booking 

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


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


    def test_confirm_booking_request_success(self):

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
            "ACCEPTED"
        )

        self.assertEqual(
            response.data["lsa"],
            lsa.id
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