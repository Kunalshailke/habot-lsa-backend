# Habot LSA Booking Backend

**Kunal Shailke**
**Email:** kunalshailke@gmail.com
**Contact:** 9589496151

A Django REST API for managing Learning Support Assistant (LSA) booking requests, bookings, and simulated payments.

## Tech Stack

- Python
- Django
- Django REST Framework
- SQLite
- Django ORM
- pytest
- pytest-django
- GitHub Actions

## Main Features

- Parent, LSA and Skill data models
- Skill-based LSA search
- LSA availability checking
- Booking request creation
- Booking confirmation
- Booking overlap validation
- Simulated payment processing
- Payment webhook handling
- Token authentication
- Automated API tests
- GitHub Actions CI workflow

## Project Structure

```text
habot_lsa_backend/
├── bookings/
│   ├── migrations/
│   ├── tests/
│   │   ├── test_api.py
│   │   └── test_payment.py
│   ├── admin.py
│   ├── models.py
│   ├── payment_service.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── habot_lsa_backend/
│   ├── settings.py
│   └── urls.py
├── .github/
│   └── workflows/
│       └── tests.yml
├── manage.py
├── requirements.txt
└── README.md
```

## Setup Instructions

These steps are for setting up the project in a fresh environment.

### 1. Clone the Repository

```bash
git clone https://github.com/Kunalshailke/habot-lsa-backend.git
cd habot-lsa-backend
```

### 2. Create and Activate Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Apply Migrations

```powershell
python manage.py migrate
```

### 5. Run the Development Server

```powershell
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

The root URL redirects to:

```text
http://127.0.0.1:8000/api/v1/
```

## Authentication

The API uses Django REST Framework Token Authentication.

### Obtain Token

```http
POST /api/v1/auth/token/
```

Example request:

```json
{
    "username": "testuser",
    "password": "testpassword123"
}
```

Use the returned token for authenticated requests:

```http
Authorization: Token <your-token>
```

## API Endpoints

Base URL:

```text
http://127.0.0.1:8000/api/v1/
```

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| GET | `/api/v1/` | API root and available routes | No |
| POST | `/api/v1/auth/token/` | Obtain authentication token | No |
| POST | `/api/v1/bookings/` | Create a booking request | Yes |
| GET | `/api/v1/lsas/search/?skill_id=<id>` | Search available LSAs by skill | Yes |
| POST | `/api/v1/booking-requests/<id>/confirm/` | Confirm a booking request | Yes |
| POST | `/api/v1/payments/webhook/` | Handle payment webhook | Yes |
| POST | `/api/v1/payments/mock/` | Simulated payment endpoint | Yes |

### Create Booking Request

Example request:

```json
{
    "parent": 1,
    "required_skill": 1,
    "start_time": "2026-08-20T10:00:00Z",
    "end_time": "2026-08-20T12:00:00Z"
}
```

A new booking request is created with `PENDING` status.

### Confirm Booking

Before confirming a booking, the API checks:

- Booking request is pending
- Preferred LSA is selected
- LSA is available
- LSA has the required skill
- No overlapping booking exists
- Simulated payment succeeds

A successful confirmation creates a `CONFIRMED` booking and a successful payment record.

## Database Design

The main models are:

- **Parent** — stores parent information.
- **Skill** — represents skills available for LSAs.
- **LSAProfile** — stores LSA information, availability and skills.
- **BookingRequest** — stores a parent's requested booking details.
- **Booking** — represents a confirmed booking.
- **Payment** — stores simulated payment information.

The project uses Django ORM for database operations.

## Query Optimization

### LSA Search

LSA search uses Django ORM relationships to filter LSAs by the requested skill and availability.

This ensures that the API returns relevant and currently available LSAs.

### Booking Overlap Validation

Before confirming a booking, the API checks whether the selected LSA already has a booking overlapping the requested time range.

The overlap condition is:

```text
existing_start < requested_end
AND
existing_end > requested_start
```

This prevents conflicting bookings while allowing non-overlapping bookings.

### Database Index Review

The original project contained custom indexes for booking queries.

During simplification, these indexes were reviewed and removed because they were not necessary for the final prototype's query patterns.

The database migration for this change is included in:

```text
bookings/migrations/0004_remove_booking_booking_lsa_time_idx_and_more.py
```

The final database design keeps the schema simple while retaining the required query and validation logic.

## Payment Flow

The project uses a simulated payment service instead of a real payment gateway.

```text
Booking Request
      ↓
Validate Request
      ↓
Validate LSA
      ↓
Check Skill & Availability
      ↓
Check Booking Overlap
      ↓
Create Booking
      ↓
Process Simulated Payment
      ↓
Create Payment Record
      ↓
Mark Request as Accepted
```

Booking confirmation and payment creation are handled inside a database transaction. If payment processing fails, the transaction is rolled back.

## Testing

Automated tests cover the main API and payment behaviour, including:

- Authentication
- Booking request creation
- LSA search
- Booking confirmation
- Booking validation
- Booking overlap handling
- Payment processing
- Payment failure handling
- Payment webhook behaviour

Run the tests with:

```powershell
python -m pytest -q
```

Final test result:

```text
12 passed
```

Django system check:

```powershell
python manage.py check
```

Expected:

```text
System check identified no issues (0 silenced).
```

Git whitespace check:

```powershell
git diff --check
```

## Continuous Integration

GitHub Actions runs the automated test suite using:

```text
.github/workflows/tests.yml
```

This helps verify the project automatically when changes are pushed to GitHub.

## Final Validation

The project was validated using:

```powershell
python -m pytest -q
python manage.py check
git diff --check
git status
```

Final status:

- 12 tests passed
- Django system check passed
- Git diff check passed
- Working tree clean

## Repository

GitHub:

https://github.com/Kunalshailke/habot-lsa-backend

## Author

**Kunal Shailke**
**Email:** kunalshailke@gmail.com
**Contact:** 9589496151