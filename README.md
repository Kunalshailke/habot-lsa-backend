# Habot LSA Booking Backend

A Django REST API for managing Learning Support Assistant (LSA) booking requests, bookings, and simulated payments.

## Tech Stack

- Python
- Django
- Django REST Framework
- SQLite
- pytest
- pytest-django
- GitHub Actions

## Main Features

- Parent, LSA and skill data models
- Skill-based LSA search
- LSA availability checking
- Booking request creation
- Booking confirmation
- Booking overlap validation
- Simulated payment processing
- Payment webhook handling
- Token authentication
- Automated API tests

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