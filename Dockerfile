# Base image
# Use an official Python runtime as a parent image
FROM python:3.11-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt ./

# Install dependencies
RUN python -m pip install -r requirements.txt

# Install PyTorch
RUN python -m pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install spaCy model
RUN python -m spacy download en_core_web_sm

# Copy the current directory contents into the container at /app
COPY . /app

EXPOSE 8080

# Define environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080
# Run the Flask app
CMD ["flask", "run"]

