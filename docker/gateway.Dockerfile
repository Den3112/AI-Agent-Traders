FROM node:22-slim

# Install Python and build dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    bash \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv for blazing fast python dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Create a non-root user
RUN groupadd -r openclaw && useradd -r -g openclaw openclaw \
    && chown -R openclaw:openclaw /app

# Install OpenClaw globally (optimized)
RUN npm install -g openclaw@2026.4.15 && npm cache clean --force

# Use a virtual environment with uv
ENV VIRTUAL_ENV=/app/.venv
RUN /bin/uv venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies from pyproject.toml
COPY pyproject.toml .
RUN /bin/uv pip install . --no-cache

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
