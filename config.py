import os

# Environment variables (set these in your environment or .env file)
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

# File path where allowed users are stored
USERS_FILE = "users.json"
