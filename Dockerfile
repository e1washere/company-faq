FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Set Python path to include modules
ENV PYTHONPATH=/app/modules/m2-api-gateway:/app:$PYTHONPATH

# Change to the API gateway directory
WORKDIR /app/modules/m2-api-gateway

# Expose port
EXPOSE 8080

# Run the API gateway
CMD ["uvicorn", "api_gateway:app", "--host", "0.0.0.0", "--port", "8080"] 