from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import BookingRequestSerializer, BookingSerializer
from .models import BookingRequest, LSAProfile, Booking
from .serializers import LSASerializer
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import BookingRequest, LSAProfile, Booking, Payment
from .payment_service import process_payment
class APIRootView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({
            "status": "ok",
            "bookings": "/api/v1/bookings/",
            "lsa_search": "/api/v1/lsas/search/",
            "booking_confirm": "/api/v1/booking-requests/<id>/confirm/",
            "auth_token": "/api/v1/auth/token/",
        })
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
        # IMPORTANT:
        # This line has 8 spaces.
        # It is INSIDE def post().
        with transaction.atomic():
            # This code has 12 spaces.
            # It is INSIDE transaction.atomic().
            booking = Booking.objects.create(
                booking_request=booking_request,
                parent=booking_request.parent,
                lsa=booking_request.preferred_lsa,
                start_time=booking_request.start_time,
                end_time=booking_request.end_time,
                status="CONFIRMED",
            )
            payment_result = process_payment(
                amount="500.00",
                booking_id=booking.id,
            )
            if not payment_result["success"]:
                transaction.set_rollback(True)
                return Response(
                    {
                        "error": payment_result["message"],
                    },
                    status=status.HTTP_502_BAD_GATEWAY,
                )
            Payment.objects.create(
                booking=booking,
                amount="500.00",
                status="SUCCESS",
                transaction_id=payment_result["transaction_id"],
            )
            booking_request.status = "ACCEPTED"
            booking_request.save(update_fields=["status"])
        # IMPORTANT:
        # This return has 8 spaces.
        # It is INSIDE def post(), but OUTSIDE transaction.atomic().
        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_201_CREATED,
        )
class PaymentWebhookView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        booking_id = request.data.get("booking_id")
        payment_status = request.data.get("status")
        transaction_id = request.data.get("transaction_id")
        if not booking_id:
            return Response(
                {
                    "error": "booking_id is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if payment_status not in ["SUCCESS", "FAILED"]:
            return Response(
                {
                    "error": "status must be SUCCESS or FAILED."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        booking = get_object_or_404(
            Booking,
            id=booking_id,
        )
        payment = Payment.objects.filter(
            booking=booking,
        ).first()
        if not payment:
            return Response(
                {
                    "error": "Payment not found for this booking."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        with transaction.atomic():
            if payment_status == "SUCCESS":
                payment.status = "SUCCESS"
                if transaction_id:
                    payment.transaction_id = transaction_id
                payment.save(
                    update_fields=[
                        "status",
                        "transaction_id",
                    ]
                )
                booking.status = "CONFIRMED"
                booking.save(update_fields=["status"])
            else:
                payment.status = "FAILED"
                if transaction_id:
                    payment.transaction_id = transaction_id
                payment.save(
                    update_fields=[
                        "status",
                        "transaction_id",
                    ]
                )
                booking.status = "CANCELLED"
                booking.save(update_fields=["status"])
        return Response(
            {
                "message": "Payment webhook processed successfully.",
                "booking_id": booking.id,
                "booking_status": booking.status,
                "payment_status": payment.status,
                "transaction_id": payment.transaction_id,
            },
            status=status.HTTP_200_OK,
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
class MockPaymentView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        return Response(
            {
                "success": True,
                "message": "Mock payment processed successfully.",
            },
            status=status.HTTP_200_OK,
        )
