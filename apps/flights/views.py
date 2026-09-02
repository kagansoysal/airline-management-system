from datetime import timedelta
from datetime import date

from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.flights.models import Flight
from apps.flights.serializers import FlightSerializer
from apps.reservations.serializers import ReservationSerializer

class FlightListCreateView(APIView):

    def get(self, request):
        flights = Flight.objects.all()

        departure = request.query_params.get("departure")
        destination = request.query_params.get("destination")
        departure_date = request.query_params.get("departure_date")
        arrival_date = request.query_params.get("arrival_date")

        if departure:
            departure = departure.replace("ı", "i").replace("İ", "I")
            flights = flights.filter(departure__icontains=departure)

        if destination:
            destination = destination.replace("ı", "i").replace("İ", "I")
            flights = flights.filter(destination__icontains=destination)

        if departure_date:
            try:
                date.fromisoformat(departure_date)
            except ValueError:
                return Response(
                    {"departure_date": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            flights = flights.filter(departure_time__date=departure_date)

        if arrival_date:
            try:
                date.fromisoformat(arrival_date)
            except ValueError:
                return Response(
                    {"arrival_date": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            flights = flights.filter(arrival_time__date=arrival_date)

        serializer = FlightSerializer(flights, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = FlightSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        airplane = serializer.validated_data["airplane"]
        departure_time = serializer.validated_data["departure_time"]
        arrival_time = serializer.validated_data["arrival_time"]

        conflict_exists = Flight.objects.filter(
            airplane=airplane
        ).filter(
            Q(
                departure_time__lt=arrival_time + timedelta(hours=1),
                arrival_time__gt=departure_time - timedelta(hours=1)
            )
        ).exists()

        if conflict_exists:
            return Response(
                {
                    "detail": (
                        "Flight conflicts with another flight assigned to "
                        "the same airplane. A minimum gap of 1 hour is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class FlightDetailView(APIView):

    def get(self, request, pk):
        try:
            flight = Flight.objects.get(pk=pk)
        except Flight.DoesNotExist:
            return Response(
                {"detail": "Flight not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FlightSerializer(flight)

        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            flight = Flight.objects.get(pk=pk)
        except Flight.DoesNotExist:
            return Response(
                {"detail": "Flight not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FlightSerializer(
            flight,
            data=request.data,
            partial=True
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        airplane = serializer.validated_data.get(
            "airplane",
            flight.airplane
        )
        departure_time = serializer.validated_data.get(
            "departure_time",
            flight.departure_time
        )
        arrival_time = serializer.validated_data.get(
            "arrival_time",
            flight.arrival_time
        )

        conflict_exists = Flight.objects.filter(
            airplane=airplane
        ).exclude(
            pk=flight.pk
        ).filter(
            departure_time__lt=arrival_time + timedelta(hours=1),
            arrival_time__gt=departure_time - timedelta(hours=1)
        ).exists()

        if conflict_exists:
            return Response(
                {
                    "detail": (
                        "Flight conflicts with another flight assigned to "
                        "the same airplane. A minimum gap of 1 hour is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        return Response(serializer.data)
    
    def delete(self, request, pk):
        try:
            flight = Flight.objects.get(pk=pk)
        except Flight.DoesNotExist:
            return Response(
                {"detail": "Flight not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        flight.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class FlightReservationsView(APIView):

    def get(self, request, pk):
        try:
            flight = Flight.objects.get(pk=pk)
        except Flight.DoesNotExist:
            return Response(
                {"detail": "Flight not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        reservations = flight.reservations.all()

        serializer = ReservationSerializer(
            reservations,
            many=True
        )

        return Response(serializer.data)