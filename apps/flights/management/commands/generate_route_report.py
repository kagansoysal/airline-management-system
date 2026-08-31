from django.core.management.base import BaseCommand

from django.db.models import Count, Sum, Q, F, ExpressionWrapper, DecimalField, OuterRef, Subquery

from apps.flights.models import Flight, RouteReport
from django.db.models.functions import Coalesce
from apps.reservations.models import Reservation

from openpyxl import Workbook
from openpyxl.styles import Font


class Command(BaseCommand):
    help = "Generates route utilization report"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="route_report.xlsx",
            help="Output Excel file path."
        )

    def handle(self, *args, **options):
        model_counts = (
            Flight.objects
            .filter(
                departure=OuterRef("departure"),
                destination=OuterRef("destination"),
            )
            .values("airplane__model")
            .annotate(
                model_count=Count("id")
            )
            .order_by("-model_count")
        )

        reservation_counts = (
            Reservation.objects
            .filter(
                flight__departure=OuterRef("departure"),
                flight__destination=OuterRef("destination"),
                status=True,
            )
            .values(
                "flight__departure",
                "flight__destination",
            )
            .annotate(
                reservation_count=Count("id")
            )
            .values("reservation_count")
        )

        routes = (
            Flight.objects
            .values("departure", "destination")
            .annotate(
                total_flights=Count("id"),
                total_seats=Sum("airplane__capacity"),
                used_seats=Coalesce(
                    Subquery(reservation_counts[:1]),
                    0
                ),
                occupancy_rate=ExpressionWrapper(
                    100.0 * F("used_seats") / F("total_seats"),
                    output_field=DecimalField(
                        max_digits=5,
                        decimal_places=2
                    ),
                ),
                most_used_plane_model=Subquery(
                    model_counts.values("airplane__model")[:1]
                ),
            )
        )

        for route in routes:
            RouteReport.objects.update_or_create(
                departure=route["departure"],
                destination=route["destination"],
                defaults={
                    "total_flights": route["total_flights"],
                    "total_seats": route["total_seats"],
                    "used_seats": route["used_seats"],
                    "occupancy_rate": route["occupancy_rate"],
                    "most_used_plane_model": route["most_used_plane_model"],
                },
            )

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Route Report"

        headers = [
            "Departure",
            "Destination",
            "Total Flights",
            "Total Seats",
            "Used Seats",
            "Occupancy Rate",
            "Most Used Plane Model",
        ]

        worksheet.append(headers)

        for cell in worksheet[1]:
            cell.font = Font(bold=True)

        for report in RouteReport.objects.all():
            worksheet.append([
                report.departure,
                report.destination,
                report.total_flights,
                report.total_seats,
                report.used_seats,
                float(report.occupancy_rate) / 100,
                report.most_used_plane_model,
            ])

        for cell in worksheet["F"][1:]:
            cell.number_format = "0.00%"

        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:
                if cell.value is not None:
                    max_length = max(max_length, len(str(cell.value)))

            worksheet.column_dimensions[column_letter].width = max_length + 2

        workbook.save(options["output"])