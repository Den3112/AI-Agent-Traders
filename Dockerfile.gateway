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

# Install OpenClaw globally
RUN npm install -g openclaw@2026.4.15

# Install Python dependencies from pyproject.toml
# Note: Installing system-wide in the container for simplicity
RUN pip3 install --break-system-packages --no-cache-dir \
    ccxt \
    pandas \
    numpy \
    python-dotenv \
    requests \
    pydantic

# Expose OpenClaw Gateway port
EXPOSE 18789

# Entry point
# We use --host 0.0.0.0 to ensure it's accessible from outside the container
CMD ["openclaw", "gateway", "--port", "18789", "--allow-unconfigured"]
