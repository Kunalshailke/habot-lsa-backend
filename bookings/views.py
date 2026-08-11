from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import BookingRequestSerializer, BookingSerializer

from .models import BookingRequest, LSAProfile, Booking
from .serializers import LSASerializer


class BookingCreateView(APIView):

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
