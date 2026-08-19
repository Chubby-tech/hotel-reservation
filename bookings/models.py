from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class RoomType(models.Model):
    """A category of room the hotel sells, e.g. 'Deluxe Room'. Individual
    physical rooms (Room) belong to a RoomType."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    base_price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    max_occupancy = models.PositiveSmallIntegerField(default=2)
    amenities = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated, e.g. Wi-Fi, Air conditioning, TV, Breakfast included",
    )
    image = models.ImageField(upload_to="rooms/", blank=True, null=True)

    class Meta:
        ordering = ["base_price_per_night"]

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image:
            return self.image.url
        return f"/static/images/rooms/{self.name.lower().replace(' ', '_')}.jpg"

    def amenity_list(self):
        return [a.strip() for a in self.amenities.split(",") if a.strip()]

    def get_absolute_url(self):
        return reverse("room_type_detail", args=[self.pk])

    def rooms_available_between(self, check_in, check_out):
        """Active rooms of this type with no booking that overlaps the
        given [check_in, check_out) date range."""
        overlapping_room_ids = Booking.objects.filter(
            room__room_type=self,
            status__in=Booking.ACTIVE_STATUSES,
            check_in__lt=check_out,
            check_out__gt=check_in,
        ).values_list("room_id", flat=True)
        return self.rooms.filter(is_active=True).exclude(id__in=overlapping_room_ids)


class Room(models.Model):
    """A single physical, bookable room."""

    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name="rooms")
    room_number = models.CharField(max_length=10, unique=True)
    floor = models.PositiveSmallIntegerField(blank=True, null=True)
    is_active = models.BooleanField(
        default=True, help_text="Uncheck to take a room out of service (maintenance, etc.)"
    )

    class Meta:
        ordering = ["room_number"]

    def __str__(self):
        return f"Room {self.room_number} ({self.room_type.name})"


class Booking(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CHECKED_IN = "checked_in"
    STATUS_CHECKED_OUT = "checked_out"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending confirmation"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CHECKED_IN, "Checked in"),
        (STATUS_CHECKED_OUT, "Checked out"),
        (STATUS_CANCELLED, "Cancelled"),
    ]
    # Statuses that still "hold" a room and therefore block other bookings.
    ACTIVE_STATUSES = [STATUS_PENDING, STATUS_CONFIRMED, STATUS_CHECKED_IN]

    guest = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    check_in = models.DateField()
    check_out = models.DateField()
    num_guests = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    special_requests = models.TextField(blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} {self.guest} — {self.room} ({self.check_in} to {self.check_out})"

    def clean(self):
        if self.check_in and self.check_out and self.check_out <= self.check_in:
            raise ValidationError("Check-out date must be after the check-in date.")
        if self.check_in and self.check_in < date.today():
            raise ValidationError("Check-in date cannot be in the past.")
        if self.room_id and self.check_in and self.check_out:
            conflicts = Booking.objects.filter(
                room=self.room,
                status__in=self.ACTIVE_STATUSES,
                check_in__lt=self.check_out,
                check_out__gt=self.check_in,
            ).exclude(pk=self.pk)
            if conflicts.exists():
                raise ValidationError("This room is already booked for part of the selected dates.")

    @property
    def nights(self):
        return (self.check_out - self.check_in).days

    def save(self, *args, **kwargs):
        if self.room_id and self.check_in and self.check_out:
            self.total_price = self.nights * self.room.room_type.base_price_per_night
        super().save(*args, **kwargs)

    def can_be_cancelled(self):
        return self.status in (self.STATUS_PENDING, self.STATUS_CONFIRMED) and self.check_in >= date.today()
