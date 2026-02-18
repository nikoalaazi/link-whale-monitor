#!/bin/bash
# Wrapper script for LINK Whale Monitor
# Called by cron every 3 hours

export NANSEN_API_KEY="${NANSEN_API_KEY}"
export ETHERSCAN_API_KEY="${ETHERSCAN_API_KEY}"
export GOOGLE_SHEET_ID="${GOOGLE_SHEET_ID}"

# Change to home directory
cd /home/ubuntu

# Run the monitor
/usr/bin/python3 /home/ubuntu/link_whale_monitor.py

# Log output
echo "[$(date)] Monitor script executed" >> /home/ubuntu/.openclaw/workspace/link_monitor.log