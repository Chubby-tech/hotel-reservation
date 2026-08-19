from django.contrib import admin

from .models import Booking, Room, RoomType


class RoomInline(admin.TabularInline):
    model = Room
    extra = 1


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "base_price_per_night", "max_occupancy")
    search_fields = ("name",)
    inlines = [RoomInline]


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "room_type", "floor", "is_active")
    list_filter = ("room_type", "is_active")
    search_fields = ("room_number",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "guest", "room", "check_in", "check_out", "status", "total_price")
    list_filter = ("status", "room__room_type")
    search_fields = ("guest__username", "room__room_number")
    autocomplete_fields = ("guest", "room")
    readonly_fields = ("total_price", "created_at")
