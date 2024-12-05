FROM python:3.12.4-slim

# Set the working directory
WORKDIR /frontend

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libffi-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the application code
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Expose the application port
EXPOSE 8501
