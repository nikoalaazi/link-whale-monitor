# LINK Whale Monitor 🔗🐋

Automated monitoring of LINK (Chainlink) token outflows from Binance and Coinbase exchanges. Tracks high-volume transactions (>3000 LINK), filters recipient wallets by age (<90 days) and token dominance (>90% LINK), and saves results to Google Sheets.

## Features

- 📊 **Nansen API Integration**: Tracks LINK flows from CEX wallets
- 🔍 **Etherscan Verification**: Checks wallet age and token balances
- 📈 **Smart Filtering**: Only wallets meeting all criteria are recorded
- 📝 **Google Sheets Export**: Automatic data logging
- ⏰ **Cron Automation**: Runs every 3 hours

## Requirements

- Python 3.8+
- Nansen API key
- Etherscan API key
- Google Service Account (for Sheets)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set environment variables:

```bash
export NANSEN_API_KEY="your_nansen_key"
export ETHERSCAN_API_KEY="your_etherscan_key"
export GOOGLE_SHEET_ID="your_google_sheet_id"
```

Or add to systemd service file:

```ini
Environment="NANSEN_API_KEY=xxx"
Environment="ETHERSCAN_API_KEY=xxx"
Environment="GOOGLE_SHEET_ID=xxx"
```

## Usage

### Manual run:

```bash
python3 link_whale_monitor.py
```

### Automated (cron):

```bash
chmod +x run_link_monitor.sh
./run_link_monitor.sh
```

## Filtering Criteria

| Parameter | Value | Description |
|-----------|-------|-------------|
| Token | LINK (0x5149...) | Only Chainlink |
| Direction | Outflow | From exchanges only |
| Min Volume | 3000 LINK (~$20,000 USD) | High-value transfers |
| Wallet Age | <90 days | Recently created |
| LINK Dominance | >90% | Portfolio concentration |

## API Endpoints Used

- **Nansen**: `/api/v1/tgm/transfers` — CEX transfer tracking
- **Nansen**: `/api/v1/tgm/flows` — Exchange flow analysis
- **Etherscan**: `/api` — Wallet verification

## Output Format

Results saved to Google Sheets with columns:
- Timestamp
- Wallet Address
- Exchange Source (Binance/Coinbase)
- Transaction Amount
- Etherscan Verification Status

## License

MIT