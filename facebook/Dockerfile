# Stage 1: Build the application
FROM python:3.12-alpine AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=facebook.settings

# Install build dependencies
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
RUN pip install -r requirements.txt && which daphne
# Copy the application code
COPY . /facebook/

# Collect static files
RUN python manage.py collectstatic --noinput --verbosity 3

# Stage 2: Create the final image
FROM python:3.12-alpine
# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=facebook.settings


# Add daphne to the PATH
ENV PATH="/usr/local/lib/python3.12/site-packages/daphne:${PATH}"
# Install runtime dependencies
RUN apk update && apk add --no-cache mariadb-connector-c

# Create and set the working directory
WORKDIR /facebook

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /facebook /facebook


# Expose port 8000
EXPOSE 8000

# Command to run the Django server using daphne
CMD ["python", "-m", "daphne", "-b", "0.0.0.0", "-p", "8000", "facebook.asgi:application"]
