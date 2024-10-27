# Use Python image
FROM python:3.12-alpine

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=facebook.settings

# Install dependencies
RUN apk update && apk add --no-cache \
    mariadb-connector-c-dev \
    gcc \
    musl-dev \
    linux-headers \
    mariadb-dev \
    pkgconf

# Create and set the working directory
WORKDIR /facebook

# Copy requirements and install dependencies
COPY requirements.txt /facebook/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the application code
COPY . /facebook/

# Collect static files
RUN python manage.py collectstatic --noinput

# Command to run the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
