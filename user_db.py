import json
import os

DB_FILE = "db.json"

# 📂 Ensure DB file exists
def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({"users": []}, f)

# 📖 Load DB content
def load_db():
    init_db()
    with open(DB_FILE, "r") as f:
        return json.load(f)

# 💾 Save DB content
def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ➕ Add new user
def add_user(user_id):
    data = load_db()
    if user_id not in data["users"]:
        data["users"].append(user_id)
        save_db(data)

# ➖ Remove user
def remove_user(user_id):
    data = load_db()
    if user_id in data["users"]:
        data["users"].remove(user_id)
        save_db(data)

# ✅ Get all users
def get_users():
    data = load_db()
    return data["users"]

# 🔍 Check if a user exists
def is_user(user_id):
    data = load_db()
    return user_id in data["users"]

# 🧾 Format user list for display
def format_user_list():
    users = get_users()
    return "\n".join([f"👤 `{uid}`" for uid in users]) if users else "❌ No users found."
    
