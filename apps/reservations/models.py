from django.db import models

from apps.flights.models import Flight
from django.core.validators import MinLengthValidator, RegexValidator


class Reservation(models.Model):
    passenger_name = models.CharField(max_length=50)
    passenger_email = models.EmailField()
    reservation_code = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            MinLengthValidator(5),
            RegexValidator(
                regex=r'^[a-zA-Z0-9]+$',
                message="Reservation code must contain only alphanumeric characters."
            )
        ]
    )
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="reservations"
    )
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reservation_code