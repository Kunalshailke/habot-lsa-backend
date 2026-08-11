from django.db import models


class Parent(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class LSAProfile(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    skills = models.ManyToManyField(Skill, related_name="lsa_profiles")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class BookingRequest(models.Model):

    STATUS_CHOICES = [
        ("PENDING" , "Pending"),
        ("ACCEPTED" , "Accepted"),
        ("REJECTED" , "Rejected"),
    ]

    parent = models.ForeignKey(
        Parent,
        on_delete=models.CASCADE,
        related_name="booking_requests"

    )
    required_skill = models.ForeignKey(
        Skill,
        on_delete=models.PROTECT,
        related_name="booking_requests"
    )

    preferred_lsa = models.ForeignKey(
        LSAProfile,
        on_delete=models.SET_NULL,
        related_name="booking_requests",
        null=True,
        blank=True,
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField( max_length=20, choices=STATUS_CHOICES, default="PENDING")

    def __str__(self):
        return f" Request #{self.id}"



class Booking(models.Model):

    STATUS_CHOICES = [
        ("CANCELLED", "Cancelled"),
        ("CONFIRMED", "Confirmed"),
        ("COMPLETED", "Completed"),
    ]

    booking_request = models.OneToOneField(
        BookingRequest,
        on_delete=models.PROTECT,
        related_name="bookings",
    )

    parent = models.ForeignKey(
        Parent,
        on_delete=models.PROTECT,
        related_name="bookings"
    )

    lsa = models.ForeignKey(
        LSAProfile,
        on_delete=models.PROTECT,
        related_name="bookings"
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="CONFIRMED")


    def __str__(self):
        return f" Booking #{self.id}"


class Payment(models.Model):

    STATUS_CHOICES = [
        ("PENDING","Pending"),
        ("SUCCESS","Success"),
        ("FAILED","Failed"),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.PROTECT,
        related_name="payment"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True,)
    
    def __str__(self):
        return f" Payment for Booking #{self.booking_id}"