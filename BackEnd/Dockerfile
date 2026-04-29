# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY BackEnd/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# Copying specifically into BackEnd folder to keep imports valid
COPY BackEnd ./BackEnd

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "BackEnd.main:app", "--host", "0.0.0.0", "--port", "8000"]
