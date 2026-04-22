FROM node:22-slim

# Install Python and build dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    bash \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create a non-root user
RUN groupadd -r openclaw && useradd -r -g openclaw openclaw \
    && chown -R openclaw:openclaw /app

# Install OpenClaw globally
RUN npm install -g openclaw@2026.4.15

# Install Python dependencies from pyproject.toml
COPY pyproject.toml .
# We use --break-system-packages because we are in a container and want these global to the container
RUN pip3 install --break-system-packages --no-cache-dir .

# Copy the rest of the application (excluding what's in .dockerignore)
COPY . .

# Ensure permissions for the non-root user
RUN chown -R openclaw:openclaw /app

# Switch to non-root user
USER openclaw

# Expose OpenClaw Gateway internal port
EXPOSE 18789

# Entry point
CMD ["openclaw", "gateway", "--port", "18789", "--allow-unconfigured"]
