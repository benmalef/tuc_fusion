# Use Python 3.10.12 as base image
FROM python:3.10.12-slim

# Set environment variables
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install pipenv

# Set working directory
WORKDIR /fusion

# Copy Pipfile and Pipfile.lock into the container
COPY Pipfile Pipfile.lock ./

# Install project dependencies
RUN pipenv install

# Copy the rest of the application code into the container
COPY . . 

# Command to run the application
CMD ["pipenv", "run", "python", "src/my_kafka_fusion.py"]
