from django.db import models

from apps.airplanes.models import Airplane
from django.core.validators import MinValueValidator, MaxValueValidator


class Flight(models.Model):
    flight_number = models.CharField(max_length=20, unique=True)
    departure = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights",
    )

    def __str__(self):
        return self.flight_number
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(arrival_time__gt=models.F("departure_time")),
                name="arrival_after_departure",
            ),
        ]
    
    
class RouteReport(models.Model):
    departure = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    total_flights = models.PositiveIntegerField()
    total_seats = models.PositiveIntegerField()
    used_seats = models.PositiveIntegerField()
    occupancy_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )
    most_used_plane_model = models.CharField(max_length=100)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["departure", "destination"],
                name="unique_route"
            )
        ]

    def __str__(self):
        return f"{self.departure} -> {self.destination}"