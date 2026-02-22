# n8n Production Dockerfile for Render Deployment
# This runs n8n as a separate microservice alongside CyberRant backend

FROM n8nio/n8n:latest

# Switch to root to set up directories
USER root

# Create persistent data directory
RUN mkdir -p /home/node/.n8n && chown -R node:node /home/node/.n8n

# Switch back to non-root user
USER node

# n8n Configuration via Environment Variables
# These are set in Render Dashboard, NOT hardcoded here
# N8N_ENCRYPTION_KEY=<random-32-char-string>
# N8N_BASIC_AUTH_ACTIVE=true
# N8N_BASIC_AUTH_USER=admin
# N8N_BASIC_AUTH_PASSWORD=<strong-password>
# DB_POSTGRESDB_HOST=<render-postgres-host>
# DB_POSTGRESDB_PORT=5432
# DB_POSTGRESDB_DATABASE=n8n
# DB_POSTGRESDB_USER=<db-user>
# DB_POSTGRESDB_PASSWORD=<db-password>
# N8N_PORT=5678
# WEBHOOK_URL=https://rant-n8n.onrender.com/
# OPENROUTER_API_KEY=<your-key>

EXPOSE 5678

# Start n8n
CMD ["n8n", "start"]
