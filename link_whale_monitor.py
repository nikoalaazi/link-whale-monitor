#!/usr/bin/env python3
"""
LINK Whale Monitor
Monitors LINK outflows from Binance/Coinbase via Nansen
Filters wallets via Etherscan and saves to Google Sheets
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
NANSEN_API_KEY = os.getenv('NANSEN_API_KEY')
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
LINK_CONTRACT = "0x514910771af9ca656af840dff83e8264ecf986ca"
MIN_VOLUME_USD = 20000  # Approx 3000 LINK
START_DATE = "2026-01-01T00:00:00Z"
WORKSPACE_DIR = "/home/ubuntu/.openclaw/workspace"
LOG_FILE = Path(WORKSPACE_DIR) / "link_monitor.log"
RESULTS_FILE = Path(WORKSPACE_DIR) / "link_whale_results.json"

# Entity labels for Binance and Coinbase (update with exact labels from Nansen UI)
ENTITY_LABELS = [
    "binance-spot",
    "coinbase-spot",
    # Add more if found: "binance-futures", "coinbase-pro", etc.
]

def log(message):
    """Log message to console and file"""
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp}: {message}"
    print(entry)
    with open(LOG_FILE, 'a') as f:
        f.write(entry + '\n')

def fetch_nansen_flows():
    """Fetch LINK outflows from Nansen API"""
    url = "https://api.nansen.ai/v1/flows"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-KEY": NANSEN_API_KEY
    }
    
    payload = {
        "chain": "ethereum",
        "tokenAddress": LINK_CONTRACT,
        "direction": "outflow",
        "entityLabels": ENTITY_LABELS,
        "volumeUsd": {"min": MIN_VOLUME_USD},
        "blockTimestamp": {
            "from": START_DATE,
            "to": datetime.utcnow().isoformat() + "Z"
        },
        "pagination": {"page": 1, "recordsPerPage": 100},
        "orderBy": [{"field": "blockTimestamp", "direction": "desc"}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log(f"ERROR: Failed to fetch Nansen data: {e}")
        return None

def get_wallet_age(address):
    """Get wallet creation date (first transaction) via Etherscan"""
    url = f"https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": 1,
        "sort": "asc",
        "apikey": ETHERSCAN_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        if data.get("status") == "1" and data.get("result"):
            first_tx = data["result"][0]
            timestamp = int(first_tx.get("timeStamp", 0))
            return datetime.fromtimestamp(timestamp)
    except Exception as e:
        log(f"ERROR: Failed to get wallet age for {address}: {e}")
    
    return None

def is_recent_wallet(address, days=90):
    """Check if wallet was created within last N days"""
    creation_date = get_wallet_age(address)
    if not creation_date:
        return False
    
    cutoff_date = datetime.now() - timedelta(days=days)
    return creation_date >= cutoff_date

def check_link_percentage(address):
    """
    Check if LINK constitutes >90% of wallet value
    This requires querying token balances and current prices
    """
    # This is a simplified check - full implementation would:
    # 1. Get all token balances via Etherscan tokenbalance endpoint
    # 2. Get USD values via price API
    # 3. Calculate percentage
    
    # For now, return True (placeholder for full implementation)
    return True, {"link_amount": "placeholder", "total_usd": "placeholder"}

def save_to_google_sheets(data):
    """
    Save results to Google Sheet using service account
    This requires google-auth and gspread libraries
    """
    # For now, save to local JSON file
    # Full implementation would use Google Sheets API
    output = {
        "timestamp": datetime.now().isoformat(),
        "wallets": data
    }
    
    with open(RESULTS_FILE, 'a') as f:
        f.write(json.dumps(output) + '\n')
    
    log(f"Saved {len(data)} wallet(s) to {RESULTS_FILE}")
    
    # TODO: Implement Google Sheets API integration
    # Requires: pip install gspread google-auth

def main():
    """Main monitoring routine"""
    log("=== LINK Whale Monitor Started ===")
    
    # Check environment variables
    if not all([NANSEN_API_KEY, ETHERSCAN_API_KEY, GOOGLE_SHEET_ID]):
        log("ERROR: Missing API keys. Check environment variables.")
        log(f"NANSEN_API_KEY set: {bool(NANSEN_API_KEY)}")
        log(f"ETHERSCAN_API_KEY set: {bool(ETHERSCAN_API_KEY)}")
        log(f"GOOGLE_SHEET_ID set: {bool(GOOGLE_SHEET_ID)}")
        return 1
    
    # Fetch data from Nansen
    log("Fetching Nansen flows data...")
    nansen_data = fetch_nansen_flows()
    
    if not nansen_data:
        log("No data received from Nansen")
        return 1
    
    log(f"Received data from Nansen: {json.dumps(nansen_data)[:200]}...")
    
    # Process transactions
    # This will vary based on exact Nansen API response format
    # Placeholder implementation:
    
    wallets_found = []
    
    # Extract transactions from response
    # Adjust based on actual Nansen API response structure
    transactions = nansen_data.get("data", []) or nansen_data.get("results", [])
    
    log(f"Found {len(transactions)} transactions")
    
    for tx in transactions[:10]:  # Process first 10
        # Extract wallet address (recipient)
        to_address = tx.get("to") or tx.get("toAddress") or tx.get("recipient")
        
        if not to_address:
            continue
        
        log(f"Checking wallet: {to_address}")
        
        # Check wallet conditions
        if is_recent_wallet(to_address, days=90):
            log(f"  - Recent wallet (<90 days)")
            
            link_dominant, balance_info = check_link_percentage(to_address)
            
            if link_dominant:
                log(f"  - LINK dominant balance")
                wallets_found.append({
                    "address": to_address,
                    "timestamp": datetime.now().isoformat(),
                    "etherscan_url": f"https://etherscan.io/address/{to_address}",
                    "balance_info": balance_info
                })
    
    # Save results
    if wallets_found:
        save_to_google_sheets(wallets_found)
    else:
        log("No wallets matching criteria found")
    
    log("=== Monitor completed ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())