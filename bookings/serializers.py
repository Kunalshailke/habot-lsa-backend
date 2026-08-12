from rest_framework import serializers

from .models import BookingRequest, LSAProfile, Booking


class BookingRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingRequest
        fields = [
            "id",
            "parent",
            "required_skill",
            "preferred_lsa",
            "start_time",
            "end_time",
            "created_at",
            "status",
        ]
        read_only_fields = ["id", "created_at", "status"]

    def validate(self, data):
        start_time = data["start_time"]
        end_time = data["end_time"]
        preferred_lsa = data.get("preferred_lsa")

        if start_time >= end_time:
            raise serializers.ValidationError(
                "start_time must be before end_time."
            )

        if preferred_lsa:
            if not preferred_lsa.is_available:
                raise serializers.ValidationError(
                    "Selected LSA is currently unavailable."
                )

            if not preferred_lsa.skills.filter(
                id=data["required_skill"].id
            ).exists():
                raise serializers.ValidationError(
                    "Selected LSA does not have the required skill."
                )

            overlap = BookingRequest.objects.filter(
                preferred_lsa=preferred_lsa,
                start_time__lt=end_time,
                end_time__gt=start_time,
            ).exists()

            if overlap:
                raise serializers.ValidationError(
                    "This LSA already has an overlapping booking request."
                )

        return data


class LSASerializer(serializers.ModelSerializer):
    skills = serializers.StringRelatedField(many=True)

    class Meta:
        model = LSAProfile
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "skills",
            "is_available",
        ]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "booking_request",
            "parent",
            "lsa",
            "start_time",
            "end_time",
            "created_at",
            "status",
        ]
        read_only_fields = ["id", "created_at", "status"]