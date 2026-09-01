import random
import string

from rest_framework import serializers

from apps.reservations.models import Reservation

class ReservationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservation
        fields = [
            "id",
            "passenger_name",
            "passenger_email",
            "reservation_code",
            "flight",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "reservation_code",
            "created_at",
        ]

    def validate(self, data):
        if self.instance is None and data.get("status", True) is False:
            raise serializers.ValidationError({
                "status": "A new reservation must be active."
            })

        flight = data.get("flight")

        if flight is None and self.instance is not None:
            flight = self.instance.flight

        if flight is None:
            raise serializers.ValidationError({
                "flight": "Flight is required."
            })

        active_reservations = Reservation.objects.filter(
            flight=flight,
            status=True
        ).exclude(
            pk=self.instance.pk if self.instance else None
        ).count()

        if active_reservations >= flight.airplane.capacity:
            raise serializers.ValidationError({
                "flight": "This flight is fully booked."
            })

        return data

    def create(self, validated_data):
        validated_data["status"] = True

        while True:
            reservation_code = "".join(
                random.choices(
                    string.ascii_uppercase + string.digits,
                    k=5
                )
            )

            if not Reservation.objects.filter(
                reservation_code=reservation_code
            ).exists():
                break

        return Reservation.objects.create(
            reservation_code=reservation_code,
            **validated_data
        )