import os

# 🔐 Telegram API credentials
API_ID = int(os.getenv("API_ID", "123456"))  # Replace with your actual API ID
API_HASH = os.getenv("API_HASH", "your_api_hash_here")
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token_here")

# 👑 Owner Telegram user ID
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))

# 📂 Download directory
DOWNLOAD_DIR = "downloads"

# 🔧 Aria2c RPC config
ARIA2_HOST = "http://localhost"
ARIA2_PORT = 6800
ARIA2_SECRET = "madara123"

# 🚫 Cooldown per user (seconds)
USER_COOLDOWN = 10
