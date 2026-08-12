from django.urls import path
from .views import BookingCreateView, LSASearchView, BookingConfirmView, PaymentWebhookView, APIRootView, MockPaymentView


urlpatterns = [
    path("", APIRootView.as_view(), name="api-root"),
    path("bookings/", BookingCreateView.as_view(), name="booking-create"),
    path("lsas/search/", LSASearchView.as_view(), name="lsa-search"),
    path("booking-requests/<int:booking_request_id>/confirm/", BookingConfirmView.as_view(), name="booking-confirm"),
    path("payments/webhook/", PaymentWebhookView.as_view(), name="payment-webhook"),
    path("payments/mock/", MockPaymentView.as_view(), name="mock-payment"),

]