# Deployment Guide

This guide provides instructions for deploying the **AI Agent Traders** system in production environments.

## Deployment Options

### 1. Docker Compose (Recommended)

The simplest way to deploy the entire stack on a single server.

```bash
# Clone and enter
git clone https://github.com/Den3112/AI-Agent-Traders.git
cd AI-Agent-Traders

# Configure
cp .env.example .env
# Set: TRADING_MODE=PAPER initially

# Build and Start
docker-compose up -d --build
```

### 2. Manual Installation (Development)

Use this if you need to debug individual services.

- **Requirements**: Python 3.10+, Node.js 18+, Redis 7.0+.
- **Install Python env**: `uv venv && uv sync`
- **Install Node env**: `npm install`
- **Run Loop**: `python scripts/ai/continuous_loop.py`

## Environment Configuration

| Variable | Description | Default |
| :--- | :--- | :--- |
| `TRADING_MODE` | `PAPER` or `LIVE` | `PAPER` |
| `OPENCLAW_URL` | Endpoint for the gateway | `http://gateway:18789/chat` |
| `OKX_API_KEY` | Your exchange API key | - |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |

## Production Best Practices

### 🛡️ Security

- **API Keys**: Never commit `.env` files. Use GitHub Secrets or AWS Secrets Manager.
- **Network**: Keep Redis isolated from the public internet. Use Docker internal networks.
- **Non-Root**: All containers run as `openclaw` or `trader` users to prevent escalation.

### 📈 Monitoring

- Check logs: `docker-compose logs -f trader`
- Monitor Redis: `redis-cli --stat`
- Health Checks: Every service has a built-in health-check in `docker-compose.yml`.

### 🔄 Updates

To update the system without downtime:

```bash
git pull
docker-compose up -d --build --no-deps <service_name>
```

## Troubleshooting

### Container stuck in 'Restarting'

- Check logs: `docker-compose logs <service>`
- Often caused by missing environment variables or Redis being unreachable.

### Slow Market Scan

- Check your internet connection.
- Ensure `CCXT` is using the latest version to avoid API rate-limit issues.
