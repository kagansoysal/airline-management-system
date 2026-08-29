from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Airplane
from .serializers import AirplaneSerializer


class AirplaneListCreateView(APIView):

    def get(self, request):
        airplanes = Airplane.objects.all()
        serializer = AirplaneSerializer(airplanes, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = AirplaneSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AirplaneDetailView(APIView):

    def get(self, request, pk):
        try:
            airplane = Airplane.objects.get(pk=pk)
        except Airplane.DoesNotExist:
            return Response(
                {"detail": "Airplane not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AirplaneSerializer(airplane)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            airplane = Airplane.objects.get(pk=pk)
        except Airplane.DoesNotExist:
            return Response(
                {"detail": "Airplane not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AirplaneSerializer(
            airplane,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        try:
            airplane = Airplane.objects.get(pk=pk)
        except Airplane.DoesNotExist:
            return Response(
                {"detail": "Airplane not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        airplane.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AirplaneFlightsView(APIView):

    def get(self, request, pk):
        try:
            airplane = Airplane.objects.get(pk=pk)
        except Airplane.DoesNotExist:
            return Response(
                {"detail": "Airplane not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        
        return Response([])