# Use official Python runtime as a parent image
# 3.10-slim is a good balance of size and compatibility
FROM python:3.10-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
# ffmpeg is required for audio optimization
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Create the temp directories to ensure permissions (though tempfile handles this usually)
# It's good practice to have a non-root user, but for simple Render deployment root is often default.
# We'll stick to default for simplicity unless specified.

# Expose port 8000 (standard for uvicorn, but Render will assign dynamic port)
EXPOSE 8000

# Define the command to run the application
# We use sh -c to expand the $PORT environment variable provided by Render
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
