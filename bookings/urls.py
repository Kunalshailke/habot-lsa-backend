from django.urls import path

from .views import BookingCreateView
from .views import LSASearchView


urlpatterns = [
    path("bookings/", BookingCreateView.as_view(), name="booking-create"),
    path("lsas/search/", LSASearchView.as_view(), name="lsa-search"),
]