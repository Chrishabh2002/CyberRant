# CyberRant Enterprise Agent System - Production Dockerfile
# Supports: FastAPI + LEA (embedded) + Frontend + Sandbox

# Stage 1: Build the React Frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Serve with Python FastAPI + Embedded LEA
FROM python:3.11-slim
WORKDIR /app

# Install system utilities needed by LEA tools (network recon, audit)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    net-tools \
    iputils-ping \
    procps \
    iproute2 \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Copy LEA (Local Execution Agent) — runs embedded in cloud mode
COPY local_agent.py /app/local_agent.py

# Copy built frontend assets to be served by FastAPI
COPY --from=frontend-build /app/frontend/dist ./static

# Create sandbox directory for agent operations
RUN mkdir -p /app/agent_sandbox

# Security: Create non-privileged user
RUN useradd -m cyberrant

# Ensure all writable directories are owned by cyberrant
RUN mkdir -p media/audio media/video && \
    chown -R cyberrant:cyberrant /app

# Switch to the user
USER cyberrant

# Enterprise Configuration
ENV PORT=8000
ENV HOST=0.0.0.0
ENV IS_SYSTEM_ARMED=true
ENV LOG_LEVEL=INFO
ENV RENDER=true

EXPOSE 8000

# Start the hardened agent gateway
# LEA auto-starts via lifespan in main.py (dispatch_security_bridge)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
