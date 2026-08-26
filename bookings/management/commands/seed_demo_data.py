from pathlib import Path
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from bookings.models import Room, RoomType


class Command(BaseCommand):
    help = "Creates a handful of demo room types and rooms so you can try out the site right away."

    def handle(self, *args, **options):
        data = [
            {
                "name": "Standard Queen Room",
                "description": "A cosy, beautifully decorated sanctuary with a plush queen bed, smart ambient lighting, rainfall shower, and dedicated workspace.",
                "base_price_per_night": 15000,
                "max_occupancy": 2,
                "amenities": "High-Speed Wi-Fi, Air Conditioning, 4K Smart TV, Rainfall Shower, Coffee Maker, Work Desk",
                "image": "rooms/standard_room.jpg",
                "rooms": ["101", "102"],
            },
            {
                "name": "Deluxe King Room",
                "description": "Spacious guest room featuring a king-size bed, city view balcony, artisan minibar, luxury bath amenities, and comfortable seating.",
                "base_price_per_night": 25000,
                "max_occupancy": 2,
                "amenities": "High-Speed Wi-Fi, King Bed, Private Balcony, 4K Smart TV, Mini Fridge, Organic Bath Products",
                "image": "rooms/deluxe_room.jpg",
                "rooms": ["201", "202"],
            },
            {
                "name": "Executive Business Suite",
                "description": "Tailored for professionals and discerning travelers with a separated living salon, ergonomic workspace, and skyline panoramas.",
                "base_price_per_night": 45000,
                "max_occupancy": 3,
                "amenities": "High-Speed Wi-Fi, Executive Lounge Access, Separate Salon, Smart TV, Premium Minibar, Airport Pickup",
                "image": "rooms/executive_suite.jpg",
                "rooms": ["301", "302"],
            },
            {
                "name": "Presidential Villa Suite",
                "description": "The pinnacle of opulence boasting private oceanfront terrace, marble bathtub, dedicated butler service, and private pool access.",
                "base_price_per_night": 95000,
                "max_occupancy": 6,
                "amenities": "Private Terrace, Ocean View, Butler Service, Private Pool Access, Jacuzzi, Smart TV, Champagne Welcome, VIP Airport Transfer",
                "image": "rooms/presidential_suite.jpg",
                "rooms": ["401"],
            },
            {
                "name": "Sunset Ocean Panorama Suite",
                "description": "Floor-to-ceiling glass windows offering unobstructed 180-degree sunset ocean views, private sundeck, and couples soaking tub.",
                "base_price_per_night": 65000,
                "max_occupancy": 2,
                "amenities": "Oceanfront Balcony, Sunset View, Deep Soaking Tub, Daily Breakfast in Bed, Smart Home Controls, Nespresso Machine",
                "image": "rooms/presidential_suite.jpg",
                "rooms": ["501", "502"],
            },
            {
                "name": "Luxury Penthouse Suite",
                "description": "Top-floor penthouse with expansive dining area, private rooftop terrace, designer bar, and 360-degree city and coastline vistas.",
                "base_price_per_night": 85000,
                "max_occupancy": 4,
                "amenities": "Rooftop Terrace, Full Bar Setup, Gourmet Kitchenette, 65-inch OLED TV, Dedicated Concierge, Valet Parking",
                "image": "rooms/executive_suite.jpg",
                "rooms": ["601"],
            },
            {
                "name": "Grand Family Garden Suite",
                "description": "Interconnected family sanctuary featuring two separate master bedrooms, direct botanical garden patio, and family entertainment zone.",
                "base_price_per_night": 55000,
                "max_occupancy": 5,
                "amenities": "Private Garden Access, 2 Bedrooms, Child Safety Features, Gaming Console, Free Breakfast for Family, Laundry Service",
                "image": "rooms/deluxe_room.jpg",
                "rooms": ["701", "702"],
            },
            {
                "name": "Honeymoon Romantic Haven",
                "description": "Designed exclusively for couples with canopy king bed, aromatherapy spa jacuzzi, ambient fireplace, and complimentary champagne.",
                "base_price_per_night": 70000,
                "max_occupancy": 2,
                "amenities": "Aromatherapy Jacuzzi, Chilled Champagne, Rose Petal Turndown, In-suite Couples Spa, Breakfast Included",
                "image": "rooms/standard_room.jpg",
                "rooms": ["801"],
            },
            {
                "name": "Lagoon View Superior Room",
                "description": "Peaceful retreat facing the serene lagoon waters with custom teak furniture, private lounge deck, and tranquil morning mist views.",
                "base_price_per_night": 32000,
                "max_occupancy": 2,
                "amenities": "Lagoon Water View, Private Sunbed, Teak Furniture, High-Speed Wi-Fi, Room Service, Tea Station",
                "image": "rooms/deluxe_room.jpg",
                "rooms": ["901", "902"],
            },
            {
                "name": "Royal Crown Master Residence",
                "description": "Palatial two-story residence with private infinity plunge pool, full chef's dining room, grand piano, and 24-hour security chauffeur.",
                "base_price_per_night": 120000,
                "max_occupancy": 8,
                "amenities": "Private Plunge Pool, 24/7 Chauffeur & Security, Chef Dining Service, Grand Piano, VIP Lounge Access, Helipad Transfer",
                "image": "rooms/presidential_suite.jpg",
                "rooms": ["1001"],
            },
        ]

        for entry in data:
            room_numbers = entry.pop("rooms")
            image_path = entry.pop("image")
            room_type, created = RoomType.objects.get_or_create(name=entry["name"], defaults=entry)
            room_type.image = image_path
            room_type.description = entry.get("description", room_type.description)
            room_type.save()
            self.stdout.write(f"{'Created' if created else 'Updated'} room type: {room_type.name}")
            for number in room_numbers:
                room, room_created = Room.objects.get_or_create(
                    room_number=number, defaults={"room_type": room_type}
                )
                if room_created:
                    self.stdout.write(f"  + Room {number}")

        # Seed Admin & Staff Accounts
        from django.contrib.auth.models import User
        import shutil
        from django.conf import settings

        # Ensure media images exist from static images
        static_rooms_dir = settings.BASE_DIR / "static" / "images" / "rooms"
        media_rooms_dir = Path(settings.MEDIA_ROOT) / "rooms"
        if static_rooms_dir.exists():
            media_rooms_dir.mkdir(parents=True, exist_ok=True)
            for img_file in static_rooms_dir.glob("*.jpg"):
                dest_file = media_rooms_dir / img_file.name
                if not dest_file.exists():
                    shutil.copy2(img_file, dest_file)

        admin_accounts = [
            ("admin", "admin@aureliahotel.com", True),
            ("admin1", "admin1@aureliahotel.com", True),
            ("admin2", "admin2@aureliahotel.com", True),
            ("admin3", "admin3@aureliahotel.com", True),
            ("admin4", "admin4@aureliahotel.com", True),
            ("admin5", "admin5@aureliahotel.com", True),
        ]
        for uname, email, is_super in admin_accounts:
            user, u_created = User.objects.get_or_create(username=uname)
            user.email = email
            user.is_staff = True
            user.is_superuser = is_super
            user.set_password("admin")
            user.save()
            self.stdout.write(f"{'Created' if u_created else 'Updated'} staff/admin account: {uname} (password: admin)")

        self.stdout.write(self.style.SUCCESS("Demo data & admin accounts ready. Run `python manage.py runserver` and take a look."))

