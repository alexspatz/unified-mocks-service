# Unified Mocks Service

Unified mock service for Payment Edge, Fiscal Edge, and KDS (Kitchen Display System) with Telegram bot management.

## Features

- ✅ Single FastAPI service for all three mock endpoints
- 🤖 Telegram bot for configuration and monitoring
- 🔄 Multiple operation modes: AUTO_SUCCESS, AUTO_FAILURE, MANUAL, SEQUENCE
- 📊 Real-time logging and monitoring
- 🚀 Railway-ready deployment

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd test_enviroment
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your Telegram bot credentials
```

5. Run the service:
```bash
python main.py
```

The service will be available at `http://localhost:8000`

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ADMIN_IDS=123456789,987654321
TELEGRAM_CHAT_ID=-100123456789
PORT=8000
```

### Getting Telegram Credentials

1. **Bot Token**: Create a bot with [@BotFather](https://t.me/botfather)
2. **Admin IDs**: Get your user ID from [@userinfobot](https://t.me/userinfobot)
3. **Chat ID**: Create a group, add the bot, and use [@getidsbot](https://t.me/getidsbot)

## API Endpoints

### Payment Mock
```http
POST /mocks/payment
Content-Type: application/json

{
  "kiosk_id": "kiosk_001",
  "order_id": 9999995,
  "sum": 57000
}
```

### Fiscal Mock
```http
POST /mocks/fiscal
Content-Type: application/json

{
  "order_id": 9999996,
  "kiosk_id": "kiosk_001",
  "items": [
    {
      "item_id": 123,
      "item_description": "Cappuccino 250ml",
      "item_price_net": 30000,
      "item_price_gross": 36000,
      "item_vat_value": 6000,
      "quantity": 1
    }
  ],
  "total_net": 30000,
  "total_vat": 6000,
  "total_gross": 36000,
  "payment_method": "CARD"
}
```

### KDS Mock
```http
POST /mocks/kds
Content-Type: application/json

{
  "order_id": 9999996,
  "kiosk_id": "kiosk_001",
  "items": [
    {"item_id": 123, "description": "Cappuccino 250ml", "quantity": 1},
    {"item_id": 124, "description": "Bagel", "quantity": 2}
  ]
}
```

### Configuration
```http
GET /mocks/config
POST /mocks/config
```

### Logs
```http
GET /mocks/logs?limit=100
```

## Telegram Bot Commands

- `/status` - Brief service status
- `/status_detailed` - Detailed status with sequence information
- `/config` - Configure individual service
- `/config_all` - Configure all services at once
- `/logs [N]` - Show last N logs (default 10, max 50)
- `/help` - Show help message

## Operation Modes

### AUTO_SUCCESS
Always returns successful responses.

### AUTO_FAILURE
Always returns failure responses.

### MANUAL
Sends requests to Telegram for manual approval with inline buttons.
- Configurable timeout
- Default response on timeout

### SEQUENCE
Configurable sequence of success/failure responses.
- Example: 5 successes, 2 failures
- Sequence shuffled randomly
- Auto-regenerates when exhausted

## Railway Deployment

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Login to Railway:
```bash
railway login
```

3. Create new project:
```bash
railway init
```

4. Add environment variables in Railway dashboard:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_ADMIN_IDS`
   - `TELEGRAM_CHAT_ID`

5. Deploy:
```bash
railway up
```

The service will automatically use the `railway.json` configuration.

## Project Structure

```
.
├── main.py              # FastAPI application
├── models.py            # Pydantic models
├── storage.py           # In-memory storage
├── mocks.py             # Mock handlers
├── telegram_bot.py      # Telegram bot
├── requirements.txt     # Python dependencies
├── railway.json         # Railway configuration
├── .env.example         # Environment template
└── README.md           # This file
```

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

MIT
