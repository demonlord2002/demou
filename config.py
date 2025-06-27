import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

USERS_FILE = "users.json"

# ✅ Add allowed users here
ALLOWED_USERS = [123456789, 987654321]  # Example user IDs
