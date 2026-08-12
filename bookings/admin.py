from django.contrib import admin

from .models import (
    Parent,
    Skill,
    LSAProfile,
    BookingRequest,
    Booking,
    Payment,
)


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone", "created_at")
    search_fields = ("name", "email", "phone")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(LSAProfile)
class LSAProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "phone", "is_available")
    list_filter = ("is_available",)
    search_fields = ("name", "email", "phone")
    filter_horizontal = ("skills",)


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "parent",
        "required_skill",
        "preferred_lsa",
        "start_time",
        "end_time",
        "status",
    )
    list_filter = ("status",)
    search_fields = ("parent__name", "preferred_lsa__name")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "booking_request",
        "parent",
        "lsa",
        "start_time",
        "end_time",
        "status",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("parent__name", "lsa__name")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "booking",
        "amount",
        "status",
        "transaction_id",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = ("transaction_id",)