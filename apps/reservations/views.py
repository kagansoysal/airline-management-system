from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.reservations.models import Reservation
from apps.reservations.serializers import ReservationSerializer


class ReservationListCreateView(APIView):

    def get(self, request):
        reservations = Reservation.objects.all()
        serializer = ReservationSerializer(reservations, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = ReservationSerializer(data=request.data)

        if serializer.is_valid():
            reservation = serializer.save()
            return Response(
                ReservationSerializer(reservation).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ReservationDetailView(APIView):

    def get(self, request, pk):
        try:
            reservation = Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            return Response(
                {"detail": "Reservation not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ReservationSerializer(reservation)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            reservation = Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            return Response(
                {"detail": "Reservation not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ReservationSerializer(
            reservation,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            reservation = serializer.save()
            return Response(ReservationSerializer(reservation).data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )