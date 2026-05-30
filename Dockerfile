FROM python:3.11-slim

WORKDIR /app

# Prevents Python from writing .pyc files and buffers logs less aggressively
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies if needed later
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY pyproject.toml .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Install your package in editable mode
RUN pip install -e .

CMD ["python", "-m", "scripts.run_cityfit_ranking"]