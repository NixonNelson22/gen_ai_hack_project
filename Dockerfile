# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y supervisor zlib1g-dev libjpeg-dev build-essential

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r cement_plant_control_system/requirements.txt

# Copy the supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Run supervisord
CMD ["/usr/bin/supervisord"]