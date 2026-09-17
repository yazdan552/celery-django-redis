# Django + Celery + Redis + Docker

A sample project for learning Celery with Django, Redis, and Docker.

## 🛠 Tech Stack

- Python 3.12
- Django 6.1
- Celery 5.6
- Redis 7
- Docker & Docker Compose
- Flower (monitoring)

## ✨ Features

- Async task execution with Celery
- Automatic retry with exponential backoff
- Scheduled tasks with Celery Beat
- Real-time monitoring with Flower
- Fully containerized with Docker Compose
- Three sample tasks:
  - `my_first_task` — simple task with sleep
  - `send_welcome_email` — task with retry logic
  - `check_system_status` — periodic task (every 15s)

## 🚀 Quick Start

### Prerequisites

- Docker Desktop
- Git

### 1) Clone the repository

```bash
git clone https://github.com/yazdan552/celery-django-redis.git
cd celery-django-redis
```

### 2) Create the `.env` file

```bash
cp .env.example .env
```

### 3) Build and run

```bash
docker compose up -d --build
```

### 4) Run migrations and create a superuser

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

### 5) Access the services

- Django: http://localhost:8000
- Admin: http://localhost:8000/admin
- Flower: http://localhost:5555

## 📁 Project Structure

```
celery_app/
├── accounts/              # Tasks app
│   ├── tasks.py           # Celery tasks
│   ├── views.py
│   └── urls.py
├── celery_app/            # Project settings
│   ├── settings.py
│   ├── celery.py          # Celery + Beat config
│   └── urls.py
├── templates/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── manage.py
```

## 🧪 Testing Tasks

### From Django shell

```bash
docker compose exec web python manage.py shell
```

```python
from accounts.tasks import my_first_task, send_welcome_email

# Simple task
my_first_task.delay('user1')

# Task with retry
send_welcome_email.delay(1)
```

### From Flower

Open http://localhost:5555 to monitor tasks in real time.

## 📊 Services

| Service | Port | Description          |
|---------|------|----------------------|
| web     | 8000 | Django application   |
| flower  | 5555 | Celery monitoring    |
| redis   | 6379 | Broker + Result backend |

## 🐳 Useful Commands

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f web
docker compose logs -f celery
docker compose logs -f celery-beat
docker compose logs -f flower

# Restart a service
docker compose restart celery

# Django shell
docker compose exec web python manage.py shell
```

## 📝 License

MIT