FROM python:3.12-alpine

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=facebook.settings



RUN apk update && apk add --no-cache \
    mariadb-connector-c-dev \
    gcc \
    musl-dev \
    linux-headers \
    mariadb-dev \
    pkgconf
# Create and set the working directory
RUN mkdir /facebook
WORKDIR /facebook

# Copy the application code to the container
COPY . /facebook/

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
COPY requirements.txt /facebook/
RUN pip install -r requirements.txt


# Collect static files
RUN python manage.py collectstatic --noinput

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
