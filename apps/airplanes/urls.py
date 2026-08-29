from django.urls import path

from .views import (
    AirplaneDetailView,
    AirplaneFlightsView,
    AirplaneListCreateView,
)

urlpatterns = [
    path("", AirplaneListCreateView.as_view(), name="airplane-list-create"),
    path("<int:pk>/", AirplaneDetailView.as_view(), name="airplane-detail"),
    path("<int:pk>/flights/", AirplaneFlightsView.as_view(), name="airplane-flights"),
]