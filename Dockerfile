# Use Ubuntu 22.04 as base image
FROM ubuntu:22.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /src

# Copy project files into the container
COPY . /src/

# Update package index and install Python 3
RUN apt-get update && \
    apt-get install -y python3 python3-pip

# Install MySQL client
RUN apt-get install -y mysql-client

# Install Redis server
RUN apt-get install -y redis-server

# Install cron
RUN apt-get install -y cron

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose port 8000 (or any other port your Django server listens on)
EXPOSE 8000

# Set permissions for entrypoint script
RUN chmod +x docker-entrypoint-prod.sh

# Set the entrypoint command
ENTRYPOINT [ "./docker-entrypoint-prod.sh" ]
