from rest_framework import serializers

from .models import Airplane


class AirplaneSerializer(serializers.ModelSerializer):
    capacity = serializers.IntegerField(min_value=1)

    class Meta:
        model = Airplane
        fields = [
            "id",
            "tail_number",
            "model",
            "capacity",
            "production_year",
            "status",
        ]