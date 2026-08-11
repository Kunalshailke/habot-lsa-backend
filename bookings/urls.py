from django.urls import path

from .views import BookingCreateView
from .views import LSASearchView
from .views import BookingConfirmView

urlpatterns = [
    path("bookings/", BookingCreateView.as_view(), name="booking-create"),
    path("lsas/search/", LSASearchView.as_view(), name="lsa-search"),
    path("booking-requests/<int:booking_request_id>/confirm/", BookingConfirmView.as_view(), name="booking-confirm"),

]