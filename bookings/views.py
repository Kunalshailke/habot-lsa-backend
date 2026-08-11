from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import BookingRequestSerializer, BookingSerializer

from .models import BookingRequest, LSAProfile, Booking
from .serializers import LSASerializer

from rest_framework.permissions import IsAuthenticated

from django.db import transaction


class BookingCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BookingRequestSerializer(data=request.data)

        if serializer.is_valid():
            booking_request = serializer.save()

            return Response(
                BookingRequestSerializer(booking_request).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )



class BookingConfirmView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, booking_request_id):

        booking_request = get_object_or_404(
            BookingRequest,
            id=booking_request_id
        )

        if booking_request.status != "PENDING":
            return Response(
                {
                    "error": "Only pending booking requests can be confirmed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        lsa = booking_request.preferred_lsa

        if not lsa:
            return Response(
                {
                    "error": "A preferred LSA is required for confirmation."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not lsa.is_available:
            return Response(
                {
                    "error": "This LSA is currently unavailable."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not lsa.skills.filter(
            id=booking_request.required_skill_id
        ).exists():
            return Response(
                {
                    "error": "This LSA does not have the required skill."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        overlapping_booking = Booking.objects.filter(
            lsa=lsa,
            start_time__lt=booking_request.end_time,
            end_time__gt=booking_request.start_time,
        ).exists()

        if overlapping_booking:
            return Response(
                {
                    "error": "This LSA already has an overlapping booking."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            booking = Booking.objects.create(
                booking_request=booking_request,
                parent=booking_request.parent,
                lsa=booking_request.preferred_lsa,
                start_time=booking_request.start_time,
                end_time=booking_request.end_time,
                status="CONFIRMED",
            )

            booking_request.status = "ACCEPTED"
            booking_request.save(update_fields=["status"])

        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_201_CREATED,
        )
    

    
class LSASearchView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        skill = request.query_params.get("skill")

        lsas = LSAProfile.objects.filter(
            is_available=True
        ).prefetch_related("skills")

        if skill:
            lsas = lsas.filter(
                skills__name__iexact=skill
            )

        serializer = LSASerializer(lsas, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
