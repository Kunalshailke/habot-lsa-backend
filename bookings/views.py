from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import BookingRequestSerializer

from .models import LSAProfile
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


    
class LSASearchView(APIView):

    def get(self, request):

        skill = request.query_params.get("skill")

        lsas = LSAProfile.objects.filter(
            is_available=True
        )

        if skill:
            lsas = lsas.filter(
                skills__name__iexact=skill
            )

        serializer = LSASerializer(lsas, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
