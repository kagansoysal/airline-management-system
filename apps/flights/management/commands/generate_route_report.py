from django.core.management.base import BaseCommand
from django.db.models import Count, Sum

from apps.flights.models import Flight, RouteReport
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
        flight_stats = (
            Flight.objects
            .values("departure", "destination")
            .annotate(
                total_flights=Count("id"),
                total_seats=Sum("airplane__capacity"),
            )
        )

        flight_data = {
            (row["departure"], row["destination"]): {
                "total_flights": row["total_flights"],
                "total_seats": row["total_seats"],
            }
            for row in flight_stats
        }

        reservation_stats = (
            Reservation.objects
            .filter(status=True)
            .values(
                "flight__departure",
                "flight__destination",
            )
            .annotate(
                used_seats=Count("id")
            )
        )

        reservation_data = {
            (
                row["flight__departure"],
                row["flight__destination"],
            ): row["used_seats"]
            for row in reservation_stats
        }

        model_stats = (
            Flight.objects
            .values(
                "departure",
                "destination",
                "airplane__model",
            )
            .annotate(
                model_count=Count("id")
            )
            .order_by(
                "departure",
                "destination",
                "-model_count",
            )
        )

        model_data = {}

        for row in model_stats:
            route = (
                row["departure"],
                row["destination"],
            )

            if route not in model_data:
                model_data[route] = row["airplane__model"]

        for route, stats in flight_data.items():

            used_seats = reservation_data.get(route, 0)

            if stats["total_seats"]:
                occupancy_rate = (
                    used_seats / stats["total_seats"] * 100
                )
            else:
                occupancy_rate = 0

            RouteReport.objects.update_or_create(
                departure=route[0],
                destination=route[1],
                defaults={
                    "total_flights": stats["total_flights"],
                    "total_seats": stats["total_seats"],
                    "used_seats": used_seats,
                    "occupancy_rate": round(occupancy_rate, 2),
                    "most_used_plane_model": model_data.get(route),
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
                    max_length = max(
                        max_length,
                        len(str(cell.value))
                    )

            worksheet.column_dimensions[column_letter].width = (
                max_length + 2
            )

        workbook.save(options["output"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Route report generated successfully: "
                f"{options['output']}"
            )
        )