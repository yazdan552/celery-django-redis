# Django + Celery + Redis + Docker

A comprehensive sample project for learning **advanced Celery** with Django, Redis, and Docker.

## 🛠 Tech Stack

- Python 3.12
- Django 6.1
- Celery 5.6
- Redis 7
- Docker & Docker Compose
- Flower (real-time monitoring)
- django-celery-results (DB result backend)

## ✨ Features

### Core Celery
- Async task execution
- Automatic retry with exponential backoff
- Soft & hard time limits
- Idempotent tasks (using unique constraints)
- Task chains, groups, and chords

### Advanced
- **Task Routing** — separate queues for heavy vs light tasks
- **Two workers** — `default` (concurrency=4) + `heavy` (concurrency=2)
- **Celery Beat** — scheduled tasks (every 15s)
- **Flower** — real-time monitoring dashboard
- **django-celery-results** — persistent results in DB + admin panel

### Sample Tasks

| Task | Queue | Purpose |
|------|-------|---------|
| `add`, `mul`, `power` | default | Chain example |
| `process_item` | default | Group example |
| `sum_all` | default | Chord callback |
| `process_video` | heavy | Heavy routing example |
| `send_email` | default | Light routing example |
| `send_welcome_email_idempotent` | default | Idempotency demo |
| `task_with_cleanup` | default | Soft time limit |
| `task_with_hard_limit` | default | Hard time limit |
| `check_system_status` | default | Periodic (Beat) |

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
├── accounts/                    # Main app
│   ├── models.py                # EmailLog (idempotency)
│   ├── tasks.py                 # All Celery tasks
│   ├── views.py
│   └── urls.py
├── celery_app/                  # Project config
│   ├── settings.py              # Django + Celery config
│   ├── celery.py                # Celery + Beat schedule
│   └── urls.py
├── templates/
├── Dockerfile
├── docker-compose.yml           # 6 services
├── requirements.txt
├── .env.example
└── manage.py
```

## 🐳 Services

| Service | Port | Description |
|---------|------|-------------|
| web | 8000 | Django application |
| celery | — | Worker for `default` queue |
| celery-heavy | — | Worker for `heavy` queue |
| celery-beat | — | Scheduler |
| flower | 5555 | Monitoring dashboard |
| redis | 6379 | Broker + Cache |

## 🧪 Testing Tasks

### From Django shell

```bash
docker compose exec web python manage.py shell
```

```python
# Simple task
from accounts.tasks import add, my_first_task

add.delay(10, 20).get(timeout=10)          # 30
my_first_task.delay('user1').get(timeout=10)

# Chain
from celery import chain
chain(add.s(4, 4), add.s(8)).apply_async()

# Group
from celery import group
group(add.s(i, i) for i in range(10)).apply_async()

# Chord
from celery import chord
from accounts.tasks import sum_all
chord((add.s(i, i) for i in range(10)))(sum_all.s())

# Retry + idempotency
from accounts.tasks import send_welcome_email_idempotent
send_welcome_email_idempotent.delay(1)     # First: sent, Second: already sent

# Time limits
from accounts.tasks import task_with_cleanup, task_with_hard_limit
task_with_cleanup.delay()        # Soft time limit (5s) → cleanup
task_with_hard_limit.delay()     # Hard time limit (3s) → kill
```

### From Flower

Open http://localhost:5555 to monitor tasks, workers, and queues in real time.

## 🎯 Queue Architecture

```
                    ┌──────────────────┐
                    │   Django (web)   │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        send_email      process_video   check_system_status
              │              │              │
              ▼              ▼              ▼
       ┌─────────┐    ┌──────────┐   ┌──────────┐
       │ default │    │  heavy   │   │  beat    │
       └────┬────┘    └────┬─────┘   └────┬─────┘
            │              │              │
            ▼              ▼              │
      ┌──────────┐   ┌─────────────┐     │
      │ celery   │   │ celery-heavy│     │
      │ c=4      │   │ c=2         │     │
      └──────────┘   └─────────────┘     │
                                          ▼
                                    ┌──────────┐
                                    │  Redis   │
                                    └──────────┘
```

## 🐳 Useful Commands

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f web
docker compose logs -f celery
docker compose logs -f celery-heavy
docker compose logs -f celery-beat
docker compose logs -f flower

# Restart a service
docker compose restart celery

# Django shell
docker compose exec web python manage.py shell

# Check queue lengths
docker exec -it my_redis redis-cli -n 0 LLEN default
docker exec -it my_redis redis-cli -n 0 LLEN heavy
```

## 📊 Task Results

Results are stored in **PostgreSQL/SQLite** via `django-celery-results`.

View them in:
- **Django Admin**: http://localhost:8000/admin/ → **Task results**
- **Shell**: `from django_celery_results.models import TaskResult`

## 📝 License

MIT