# Aurelia Hotel — booking & scheduling site (Django)

A working MVP of a hotel room booking system: guests search by date range,
book a room type, and the system auto-assigns a specific room with no
double-booking. Staff confirm, check guests in/out, and manage inventory.

## Setup

```bash
cd hotel_booking
python3 -m venv venv
source venv/bin/activate        # on Windows: source venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser   # your staff/admin login
python manage.py seed_demo_data    # optional: adds 3 room types + 9 rooms
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`. Log into `/admin/` with your superuser to
manage room types and rooms directly, or visit `/staff/` (as a staff user)
for the day-to-day confirm/check-in/check-out desk.

If `python manage.py migrate` complains about the included migration, it's
because I hand-wrote it without being able to run Django in this sandbox
(no network access here to install packages). Fix: delete
`bookings/migrations/0001_initial.py` and run
`python manage.py makemigrations bookings` yourself — the models are the
source of truth and that will regenerate a correct migration.

## Use cases covered

**Guest**
- Register / log in / log out
- Search rooms by check-in date, check-out date, and guest count
- Browse room types with live availability for the searched dates
- View room type detail (description, price, amenities)
- Book a room (system finds and assigns a free room of that type)
- View "My bookings" and a single booking's detail
- Cancel an upcoming booking

**Staff** (`is_staff=True`)
- Manage room types & rooms — add, edit, deactivate (Django admin)
- View all active bookings on a staff desk, ordered by check-in
- Confirm a pending booking, check a guest in, check a guest out, or cancel

**System / scheduling core**
- No double-booking: a room is only offered if no *active* booking
  (pending/confirmed/checked-in) overlaps the requested date range
- Total price is computed automatically from nights × room rate
- Validation blocks past check-in dates and check-out ≤ check-in
- Automated tests (`bookings/tests.py`) cover the overlap logic directly —
  run them with `python manage.py test`

## What's deliberately left out (good next steps)

- **Payments** — no gateway is wired up; bookings go straight to "pending".
  Paystack/Flutterwave are the common choices for a Nigeria-facing site.
- **Email confirmations** — Django's `django.core.mail` with an SMTP or
  provider backend would send guests a receipt on booking/status change.
- **Race condition on room assignment** — two guests booking the same last
  room in the same second could both succeed today. Wrapping the
  assignment in `select_for_update()` inside a transaction closes this.
- **Reviews/ratings**, **multi-hotel support**, **search by price range**,
  and a nicer image gallery per room type are all natural extensions of
  the current models.

## Project structure

```
hotel_booking/
├── manage.py
├── hotel_booking/        # project settings, root urls
├── bookings/             # the one app: models, views, forms, admin, tests
│   └── management/commands/seed_demo_data.py
├── templates/             # base.html + registration/ + bookings/
└── static/css/style.css
```

Currency is shown in Naira (₦) — change `base_price_per_night` values and
the `₦` in templates if you need a different currency.
