# Airline Management System

A Django REST API for managing airplanes, flights, and reservations. The system also provides route utilization reporting with Excel export and email confirmation for newly created reservations.

## Technologies

* Python 3.11
* Django 5.2
* Django REST Framework
* SQLite
* OpenPyXL
* SMTP / Gmail

## Installation and Setup

### 1. Navigate to the project directory

```bash
cd airline-management-system
```

### 2. Create and activate a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

The project uses SQLite. The `db.sqlite3` database file is created automatically when migrations are applied.

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

Email configuration is optional for the rest of the API, but required for sending reservation confirmation emails.

See the **Email Configuration** section below for details.

## Running the Development Server

Start the Django development server with:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

## API Endpoints

### Airplanes

| Method | Endpoint                   | Description                             |
| ------ | -------------------------- | --------------------------------------- |
| GET    | `/airplanes/`              | List all airplanes                      |
| GET    | `/airplanes/{id}/`         | Get details of a specific airplane      |
| GET    | `/airplanes/{id}/flights/` | Get all flights assigned to an airplane |
| POST   | `/airplanes/`              | Create a new airplane                   |
| PATCH  | `/airplanes/{id}/`         | Partially update an airplane            |
| DELETE | `/airplanes/{id}/`         | Delete an airplane                      |

### Flights

| Method | Endpoint                      | Description                       |
| ------ | ----------------------------- | --------------------------------- |
| GET    | `/flights/`                   | List all flights                  |
| GET    | `/flights/{id}/`              | Get details of a specific flight  |
| GET    | `/flights/{id}/reservations/` | Get all reservations for a flight |
| POST   | `/flights/`                   | Create a new flight               |
| PATCH  | `/flights/{id}/`              | Partially update a flight         |
| DELETE | `/flights/{id}/`              | Delete a flight                   |

#### Flight Filtering

The flight list endpoint supports optional filters:

```text
GET /flights/?departure=Heathrow
GET /flights/?destination=Istanbul
GET /flights/?departure_date=2026-09-01
GET /flights/?arrival_date=2026-09-01
```

Location filters are case-insensitive and support partial matches.

#### Flight Conflict Check

When creating or updating a flight, the system verifies that the assigned airplane does not have overlapping flights.

A minimum one-hour gap is required between consecutive flights assigned to the same airplane.

A `400 Bad Request` response is returned when a scheduling conflict is detected.

### Reservations

| Method | Endpoint              | Description                           |
| ------ | --------------------- | ------------------------------------- |
| GET    | `/reservations/`      | List all reservations                 |
| GET    | `/reservations/{id}/` | Get details of a specific reservation |
| POST   | `/reservations/`      | Create a new reservation              |
| PATCH  | `/reservations/{id}/` | Partially update a reservation        |

When a reservation is created:

* The reservation code is generated automatically.
* The reservation code is unique and alphanumeric.
* The reservation starts with an active status.
* The flight's available capacity is checked against active reservations.
* A confirmation email is sent to the passenger.

The `reservation_code` and `created_at` fields cannot be modified by the client.

#### Occupancy Check

Before creating a reservation, the system checks the number of active reservations against the capacity of the airplane assigned to the flight.

If the flight is fully booked, the API returns a `400 Bad Request` response.

## Route Report Command

The project provides a Django management command for generating route utilization reports.

Run:

```bash
python manage.py generate_route_report
```

The command:

1. Groups flights by departure and destination.
2. Calculates the total number of flights.
3. Calculates total available seats.
4. Calculates the number of active reservations.
5. Calculates the occupancy rate.
6. Determines the most frequently used airplane model on each route.
7. Upserts the results into the `RouteReport` database table.
8. Exports all route reports to an Excel file.

The default output file is:

```text
route_report.xlsx
```

A custom output path can be specified with `--output`:

```bash
python manage.py generate_route_report --output reports/my_route_report.xlsx
```

The route aggregations are performed using Django ORM database-level aggregation.

## Email Configuration

Reservation confirmation emails are sent using Gmail's SMTP server.

Create a `.env` file in the project root with:

```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

The project uses:

```text
SMTP Host: smtp.gmail.com
Port: 587
TLS: Enabled
```

### Gmail App Password

If using Gmail, an App Password should be used instead of the normal Gmail account password.

The account must have two-step verification enabled before an App Password can be created.

After creating the App Password, place it in `.env`:

```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Postman Collection

A Postman collection containing the API requests is included with the project.

Import the collection into Postman and configure the `BASE_URL` environment variable:

```text
BASE_URL=http://127.0.0.1:8000
```

The collection contains requests for:

* Airplanes
* Flights
* Flight filtering
* Reservations

Since the repository does not contain the SQLite database, the database will initially be empty after running migrations. Create the required airplanes and flights through the API before creating reservations.

## Project Notes

* SQLite is used as the database for this project.
* The SQLite database file is generated locally and is not required to run the project.