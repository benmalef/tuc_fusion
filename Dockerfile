# Use Python 3.10.12 as base image
FROM python:3.10.12-slim

# Set environment variables
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install pipenv

# Install sudo
# RUN apt-get update && apt-get install -y sudo

# # Create a user with sudo privileges
# RUN useradd -m user && \
#     echo "user ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/user

# # Switch to the new user
# USER user


# Set working directory
WORKDIR /fusion

# Copy Pipfile and Pipfile.lock into the container
COPY Pipfile Pipfile.lock ./

# Install project dependencies
RUN pipenv install

# Copy the rest of the application code into the container
COPY . . 

# Command to run the application
ENTRYPOINT [ "pipenv", "run" ]
CMD ["python", "src/my_kafka_fusion.py"]
