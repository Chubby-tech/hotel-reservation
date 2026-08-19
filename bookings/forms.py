from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RoomSearchForm(forms.Form):
    check_in = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "min": date.today().isoformat()}),
        label="Check-in Date"
    )
    check_out = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "min": date.today().isoformat()}),
        label="Check-out Date"
    )
    guests = forms.IntegerField(min_value=1, initial=1, label="Number of Guests")

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get("check_in")
        check_out = cleaned.get("check_out")
        if check_in and check_in < date.today():
            self.add_error("check_in", "Check-in date cannot be in the past.")
        if check_in and check_out and check_out <= check_in:
            self.add_error("check_out", "Check-out date must be after check-in.")
        return cleaned


class BookingCreateForm(forms.Form):
    check_in = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "min": date.today().isoformat(), "id": "id_check_in"}),
        label="Check-in Date"
    )
    check_out = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "min": date.today().isoformat(), "id": "id_check_out"}),
        label="Check-out Date"
    )
    num_guests = forms.IntegerField(min_value=1, initial=1, label="Guests")
    special_requests = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Any special requests or preferences..."}),
        required=False
    )

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get("check_in")
        check_out = cleaned.get("check_out")
        if check_in and check_in < date.today():
            self.add_error("check_in", "Check-in date cannot be in the past.")
        if check_in and check_out and check_out <= check_in:
            self.add_error("check_out", "Check-out date must be after check-in.")
        return cleaned


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
