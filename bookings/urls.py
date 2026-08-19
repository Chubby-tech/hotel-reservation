from django.urls import path

from . import views

urlpatterns = [
    path("", views.room_list, name="room_list"),
    path("room-types/<int:pk>/", views.room_type_detail, name="room_type_detail"),
    path("book/<int:pk>/", views.create_booking, name="create_booking"),
    path("bookings/", views.booking_list, name="booking_list"),
    path("bookings/<int:pk>/", views.booking_detail, name="booking_detail"),
    path("bookings/<int:pk>/cancel/", views.booking_cancel, name="booking_cancel"),
    path("register/", views.register, name="register"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
    path(
        "staff/bookings/<int:pk>/status/<str:new_status>/",
        views.staff_update_status,
        name="staff_update_status",
    ),
]
