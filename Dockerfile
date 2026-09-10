# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Build Python backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if any are needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY src/ src/
COPY pyproject.toml .

# Install the package in editable mode
RUN pip install -e .

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose FastAPI port
EXPOSE 8000

ENV STATIC_DIR=/app/frontend/dist

ENTRYPOINT ["uvicorn", "qroute.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
