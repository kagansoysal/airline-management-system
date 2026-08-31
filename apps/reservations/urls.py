from django.urls import path

from apps.reservations.views import (
    ReservationListCreateView,
    ReservationDetailView,
)

urlpatterns = [
    path(
        "",
        ReservationListCreateView.as_view(),
        name="reservation-list-create"
    ),
    path(
        "<int:pk>/",
        ReservationDetailView.as_view(),
        name="reservation-detail"
    ),
]