FROM python:3.12

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /app/venv

# Activate virtual environment and upgrade pip
ENV PATH="/app/venv/bin:$PATH"
RUN pip install --upgrade pip

# Copy requirements
COPY requirements.txt .

# Install Python dependencies in virtual environment
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run the application using venv's python
CMD ["/app/venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]