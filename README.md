@'
# HABOT LSA Backend

Django REST API backend for managing parents, skills, LSAs (Learning Support Assistants), booking requests, confirmed bookings, and payment processing.

## Tech Stack

- Python 3.12
- Django 5.2
- Django REST Framework
- SQLite
- Token Authentication
- Pytest / pytest-django
- Requests

## Features

- Create booking requests
- Validate booking time ranges
- Search available LSAs by skill
- Confirm booking requests
- Validate LSA availability
- Validate required LSA skills
- Prevent overlapping bookings
- Atomic booking confirmation
- Token-based API authentication
- Mock payment service with failure handling

## API Endpoints

### Authentication

`POST /api/v1/auth/token/`

Obtain an authentication token using Django user credentials.

### Booking Requests

`POST /api/v1/bookings/`

Create a booking request.

### LSA Search

`GET /api/v1/lsas/search/?skill=Python`

Search available LSAs by skill.

### Booking Confirmation

`POST /api/v1/booking-requests/<booking_request_id>/confirm/`

Confirm a pending booking request.

## Authentication

Protected endpoints require a token:

`Authorization: Token <your-token>`

## Running Locally

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1