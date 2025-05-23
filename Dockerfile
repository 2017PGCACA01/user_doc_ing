# Base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Create virtual environment
RUN python -m venv $VIRTUAL_ENV

# Set work directory
WORKDIR /app

# Install dependencies inside virtual environment
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose Flask port
EXPOSE 5000

# Default command
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]