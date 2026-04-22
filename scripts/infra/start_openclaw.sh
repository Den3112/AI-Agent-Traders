#!/bin/bash
# start_openclaw.sh (FIXED)

NODE_PATH="/home/creator/.nvm/versions/node/v22.22.2/bin/node"
OPENCLAW_BIN="./node_modules/.bin/openclaw"

export OPENCLAW_GATEWAY_TOKEN=admin123
echo "Starting OpenClaw with $NODE_PATH (Token: admin123)..."
nohup $NODE_PATH $OPENCLAW_BIN gateway run --config openclaw.json --token admin123 > openclaw_stdout.log 2>&1 &
echo "OpenClaw starting in background."
