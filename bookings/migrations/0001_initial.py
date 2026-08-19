import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RoomType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                ("base_price_per_night", models.DecimalField(decimal_places=2, max_digits=10)),
                ("max_occupancy", models.PositiveSmallIntegerField(default=2)),
                (
                    "amenities",
                    models.CharField(
                        blank=True,
                        help_text="Comma-separated, e.g. Wi-Fi, Air conditioning, TV, Breakfast included",
                        max_length=500,
                    ),
                ),
                ("image", models.ImageField(blank=True, null=True, upload_to="room_types/")),
            ],
            options={
                "ordering": ["base_price_per_night"],
            },
        ),
        migrations.CreateModel(
            name="Room",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("room_number", models.CharField(max_length=10, unique=True)),
                ("floor", models.PositiveSmallIntegerField(blank=True, null=True)),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Uncheck to take a room out of service (maintenance, etc.)",
                    ),
                ),
                (
                    "room_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rooms",
                        to="bookings.roomtype",
                    ),
                ),
            ],
            options={
                "ordering": ["room_number"],
            },
        ),
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("check_in", models.DateField()),
                ("check_out", models.DateField()),
                ("num_guests", models.PositiveSmallIntegerField(default=1)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending confirmation"),
                            ("confirmed", "Confirmed"),
                            ("checked_in", "Checked in"),
                            ("checked_out", "Checked out"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("special_requests", models.TextField(blank=True)),
                ("total_price", models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "guest",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "room",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookings",
                        to="bookings.room",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
