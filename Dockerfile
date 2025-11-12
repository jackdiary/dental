# Stage 1: Build frontend assets
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Build the final backend image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*



# Copy built frontend assets from the builder stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist/

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy project source code
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Create directories
RUN mkdir -p /app/logs /app/ml_models /app/staticfiles /app/media \
    && chmod -R 755 /app/logs /app/staticfiles /app/media

# Expose port
EXPOSE 8000

