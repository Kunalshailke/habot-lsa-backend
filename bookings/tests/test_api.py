from rest_framework.test import APITestCase
from rest_framework import status

from bookings.models import Parent, Skill, LSAProfile


class BookingAPITests(APITestCase):

    def setUp(self):
        self.parent = Parent.objects.create(
            name="Test Parent",
            email="testparent@example.com",
            phone="9999999999",
        )

        self.skill = Skill.objects.create(
            name="Python",
        )

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