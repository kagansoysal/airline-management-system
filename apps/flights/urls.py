from django.urls import path

from .views import (
    FlightDetailView,
    FlightListCreateView,
    FlightReservationsView,
)

urlpatterns = [
    path("", FlightListCreateView.as_view(), name="flight-list-create"),
    path("<int:pk>/", FlightDetailView.as_view(), name="flight-detail"),
    path(
        "<int:pk>/reservations/",
        FlightReservationsView.as_view(),
        name="flight-reservations",
    ),
]