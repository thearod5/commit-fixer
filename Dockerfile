# Use an official Python runtime as a parent image
FROM python:3.11-slim

WORKDIR /app

# Copy the requirements dependencies into the container at /app
COPY requirements/production-requirements.txt requirements.txt
COPY requirements/build-requirements.txt build-requirements.txt

# Install the dependencies specified in requirements.txt
RUN pip install -r requirements.txt
RUN pip install -r build-requirements.txt

# Install git and other dependencies
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code into the container at /app
COPY safa safa
COPY pyproject.toml .
COPY README.md .

RUN python3 -m build
RUN pip3 install .



CMD ["bash"]
