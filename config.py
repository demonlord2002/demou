import os
from dotenv import load_dotenv

# 📦 Load environment variables from .env file
load_dotenv()

# 🔐 Telegram API credentials
API_ID = int(os.getenv("API_ID", "23559126"))            # Replace with your actual API ID
API_HASH = os.getenv("API_HASH", "58347a441c011b1b9ee3367ea936dcc4") # Replace with your actual API HASH
BOT_TOKEN = os.getenv("BOT_TOKEN", "7479028842:AAF_Ag8L6UR5G2VVNrhI-sCkvYjlNyx7IJs")  # Replace with your bot token

# 👑 Bot owner Telegram user ID (int)
OWNER_ID = int(os.getenv("OWNER_ID", "7813285237"))

# 📂 Directory where files will be downloaded
DOWNLOAD_DIR = "downloads"

# ⚙️ Aria2c RPC configuration
ARIA2_HOST = "http://localhost"
ARIA2_PORT = 6800
ARIA2_SECRET = "madara123"  # Must match --rpc-secret in aria2c

# 🚫 Rate limiting (seconds between commands per user)
USER_COOLDOWN = 10
