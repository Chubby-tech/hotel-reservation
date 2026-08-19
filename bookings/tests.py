from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Booking, Room, RoomType


class AvailabilityTests(TestCase):
    def setUp(self):
        self.room_type = RoomType.objects.create(
            name="Standard", base_price_per_night=10000, max_occupancy=2
        )
        self.room = Room.objects.create(room_type=self.room_type, room_number="101")
        self.guest = User.objects.create_user(username="guest", password="testpass123")
        self.today = date.today()

    def test_room_excluded_when_dates_overlap_an_active_booking(self):
        Booking.objects.create(
            guest=self.guest,
            room=self.room,
            check_in=self.today + timedelta(days=1),
            check_out=self.today + timedelta(days=4),
            num_guests=1,
        )
        available = self.room_type.rooms_available_between(
            self.today + timedelta(days=2), self.today + timedelta(days=3)
        )
        self.assertNotIn(self.room, available)

    def test_room_available_when_dates_do_not_overlap(self):
        Booking.objects.create(
            guest=self.guest,
            room=self.room,
            check_in=self.today + timedelta(days=1),
            check_out=self.today + timedelta(days=4),
            num_guests=1,
        )
        available = self.room_type.rooms_available_between(
            self.today + timedelta(days=4), self.today + timedelta(days=7)
        )
        self.assertIn(self.room, available)

    def test_overlapping_booking_fails_validation(self):
        Booking.objects.create(
            guest=self.guest,
            room=self.room,
            check_in=self.today + timedelta(days=1),
            check_out=self.today + timedelta(days=4),
            num_guests=1,
        )
        conflicting = Booking(
            guest=self.guest,
            room=self.room,
            check_in=self.today + timedelta(days=2),
            check_out=self.today + timedelta(days=3),
            num_guests=1,
        )
        with self.assertRaises(ValidationError):
            conflicting.full_clean()

    def test_two_people_cannot_book_same_room_at_same_dates(self):
        # Create first booking
        Booking.objects.create(
            guest=self.guest,
            room=self.room,
            check_in=self.today + timedelta(days=5),
            check_out=self.today + timedelta(days=8),
            num_guests=1,
        )
        guest2 = User.objects.create_user(username="guest2", password="testpass123")
        # Attempt second booking for overlapping dates
        second_booking = Booking(
            guest=guest2,
            room=self.room,
            check_in=self.today + timedelta(days=6),
            check_out=self.today + timedelta(days=9),
            num_guests=1,
        )
        with self.assertRaises(ValidationError):
            second_booking.full_clean()

    def test_total_price_is_nights_times_rate(self):
        booking = Booking.objects.create(
            guest=self.guest,
            room=self.room,
            check_in=self.today + timedelta(days=1),
            check_out=self.today + timedelta(days=4),
            num_guests=1,
        )
        self.assertEqual(booking.nights, 3)
        self.assertEqual(booking.total_price, 30000)
