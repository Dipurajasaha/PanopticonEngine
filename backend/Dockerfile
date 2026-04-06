# Base Python runtime
FROM python:3.12-slim

# Set container working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Application port
EXPOSE 8000

# Start ASGI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]