from rest_framework import serializers

from .models import Flight


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = [
            "id",
            "flight_number",
            "departure",
            "destination",
            "departure_time",
            "arrival_time",
            "airplane",
        ]

    def validate(self, data):
        departure_time = data.get(
            "departure_time",
            self.instance.departure_time if self.instance else None
        )

        arrival_time = data.get(
            "arrival_time",
            self.instance.arrival_time if self.instance else None
        )

        if departure_time and arrival_time and arrival_time <= departure_time:
            raise serializers.ValidationError({
                "arrival_time": "Arrival time must be after departure time."
            })

        return data