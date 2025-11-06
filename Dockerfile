# Pull official base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Create directories for static and media files with proper permissions
RUN mkdir -p /app/staticfiles /app/media /app/media/theory /app/media/theory/images && \
    chmod -R 777 /app/media && \
    chmod -R 755 /app/staticfiles && \
    chown -R 1000:1000 /app/media

# Make entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# We'll collect static files at runtime to ensure env vars are available
ENTRYPOINT ["/app/docker-entrypoint.sh"]
