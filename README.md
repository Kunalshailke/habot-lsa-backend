# Habot LSA Booking Backend

## Project Overview

A Django REST Framework backend prototype for connecting parents with Learning Support Assistants (LSAs) and managing skill-based booking requests, confirmed bookings, and simulated payments.

This project was developed as part of the HabotConnect Python Backend Developer hiring project.

## Tech Stack

- Python
- Django
- Django REST Framework
- SQLite
- Django ORM
- pytest
- pytest-django
- GitHub Actions

## Features

- Parent, Skill, LSA, Booking Request, Booking, and Payment models
- Token-based API authentication
- LSA search by skill
- Availability filtering
- Booking request creation
- Booking overlap validation
- Booking confirmation
- Payment processing simulation
- Payment success/failure handling
- Payment webhook
- Database indexes for booking queries
- Automated tests
- GitHub Actions CI workflow

## Project Structure

```text
habot_lsa_backend/
├── bookings/
│   ├── migrations/
│   ├── tests/
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