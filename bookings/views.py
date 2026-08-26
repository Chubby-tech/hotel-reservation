from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingCreateForm, RoomSearchForm, SignUpForm
from .models import Booking, RoomType


def is_staff_user(user):
    return user.is_authenticated and user.is_staff


# ---------- Guest-facing views ----------

def home(request):
    """Homepage showcasing hotel overview, highlights, and featured rooms."""
    featured_rooms = RoomType.objects.all()[:4]
    return render(request, "bookings/home.html", {"featured_rooms": featured_rooms})


def room_list(request):
    """Browse room types. Search & date availability filtering is available for logged-in users."""
    search_form = None
    queryset = RoomType.objects.all()
    searched = False
    results = []

    if request.user.is_authenticated:
        search_form = RoomSearchForm(request.GET or None)
        if request.GET and search_form.is_valid():
            searched = True
            check_in = search_form.cleaned_data["check_in"]
            check_out = search_form.cleaned_data["check_out"]
            guests = search_form.cleaned_data["guests"]
            queryset = queryset.filter(max_occupancy__gte=guests)
            for room_type in queryset:
                results.append(
                    {
                        "room_type": room_type,
                        "available": room_type.rooms_available_between(check_in, check_out).count(),
                    }
                )

    if not searched:
        results = [{"room_type": rt, "available": None} for rt in queryset]

    return render(
        request,
        "bookings/room_list.html",
        {
            "search_form": search_form,
            "results": results,
            "searched": searched,
            "request_get": request.GET if request.user.is_authenticated else {},
        },
    )



def room_type_detail(request, pk):
    room_type = get_object_or_404(RoomType, pk=pk)
    return render(
        request,
        "bookings/room_type_detail.html",
        {"room_type": room_type, "request_get": request.GET},
    )


from django.db import transaction

@login_required
def create_booking(request, pk):
    room_type = get_object_or_404(RoomType, pk=pk)
    initial = {
        "check_in": request.GET.get("check_in"),
        "check_out": request.GET.get("check_out"),
        "num_guests": request.GET.get("guests", 1),
    }

    if request.method == "POST":
        form = BookingCreateForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data["check_in"]
            check_out = form.cleaned_data["check_out"]
            num_guests = form.cleaned_data["num_guests"]

            if num_guests > room_type.max_occupancy:
                messages.error(
                    request, f"This room type sleeps up to {room_type.max_occupancy} guest(s)."
                )
            else:
                try:
                    with transaction.atomic():
                        # Lock active rooms for this room type during search & allocation to avoid concurrent double booking
                        available_rooms = room_type.rooms_available_between(check_in, check_out).select_for_update()
                        room = available_rooms.first()

                        if not room:
                            messages.error(
                                request,
                                "Sorry, no rooms of this type are free for those dates. Try different dates.",
                            )
                        else:
                            booking = Booking(
                                guest=request.user,
                                room=room,
                                check_in=check_in,
                                check_out=check_out,
                                num_guests=num_guests,
                                special_requests=form.cleaned_data["special_requests"],
                            )
                            booking.full_clean()
                            booking.save()
                            messages.success(
                                request, "Booking request confirmed — you can review it below."
                            )
                            return redirect("booking_detail", pk=booking.pk)
                except Exception as e:
                    messages.error(request, f"Booking could not be processed: {e}")
    else:
        form = BookingCreateForm(initial=initial)

    return render(request, "bookings/booking_form.html", {"form": form, "room_type": room_type})


@login_required
def booking_list(request):
    bookings = request.user.bookings.select_related("room__room_type").all()
    return render(request, "bookings/booking_list.html", {"bookings": bookings})


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.guest_id != request.user.id and not request.user.is_staff:
        messages.error(request, "You don't have access to that booking.")
        return redirect("booking_list")
    return render(request, "bookings/booking_detail.html", {"booking": booking})


@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.guest_id != request.user.id and not request.user.is_staff:
        messages.error(request, "You don't have access to that booking.")
        return redirect("booking_list")
    if request.method == "POST":
        if booking.can_be_cancelled():
            booking.status = Booking.STATUS_CANCELLED
            booking.save()
            messages.success(request, "Booking cancelled.")
        else:
            messages.error(request, "This booking can no longer be cancelled.")
    return redirect("booking_detail", pk=booking.pk)


def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("room_list")
    else:
        form = SignUpForm()
    return render(request, "bookings/register.html", {"form": form})


# ---------- Staff-facing views ----------

@user_passes_test(is_staff_user)
def staff_dashboard(request):
    bookings = (
        Booking.objects.select_related("guest", "room__room_type")
        .exclude(status=Booking.STATUS_CANCELLED)
        .order_by("check_in")
    )
    return render(request, "bookings/staff_dashboard.html", {"bookings": bookings})


@user_passes_test(is_staff_user)
def staff_update_status(request, pk, new_status):
    booking = get_object_or_404(Booking, pk=pk)
    valid_statuses = dict(Booking.STATUS_CHOICES)
    if request.method == "POST" and new_status in valid_statuses:
        booking.status = new_status
        booking.save()
        messages.success(request, f"Booking #{booking.pk} marked as {valid_statuses[new_status]}.")
    return redirect("staff_dashboard")
