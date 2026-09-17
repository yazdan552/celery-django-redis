FROM python:3.12-slim

# بهینه‌سازی پایتون
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# پوشه کاری
WORKDIR /app

# پیش‌نیازهای سیستمی
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# نصب پکیج‌های پایتون
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# کپی پروژه
COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]