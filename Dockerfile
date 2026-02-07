# CyberRant Enterprise Agent System - Production Dockerfile

# Stage 1: Build the React Frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Serve with Python FastAPI
FROM python:3.11-slim
WORKDIR /app

# Install security utilities and project dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Copy built frontend assets to be served by FastAPI or Nginx
# For this simplified enterprise setup, we assume FastAPI serves the build folder
COPY --from=frontend-build /app/frontend/dist ./static

# Security: Run as non-privileged user
RUN useradd -m cyberrant
USER cyberrant

# Enterprise Configuration
ENV PORT=8000
ENV HOST=0.0.0.0
ENV IS_SYSTEM_ARMED=true
ENV LOG_LEVEL=INFO

EXPOSE 8000

# Start the hardened agent gateway
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
