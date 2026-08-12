from django.urls import path

from .views import BookingCreateView
from .views import LSASearchView
from .views import BookingConfirmView
from .views import PaymentWebhookView

from .views import APIRootView
from .views import MockPaymentView

urlpatterns = [
    path("bookings/", BookingCreateView.as_view(), name="booking-create"),
    path("lsas/search/", LSASearchView.as_view(), name="lsa-search"),
    path("booking-requests/<int:booking_request_id>/confirm/", BookingConfirmView.as_view(), name="booking-confirm"),
    path("", APIRootView.as_view(), name="api-root"),
    path("payments/webhook/", PaymentWebhookView.as_view(), name="payment-webhook"),
    path("payments/mock/", MockPaymentView.as_view(), name="mock-payment"),

]