import json
from config import USERS_FILE

def get_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def add_user(user_id):
    users = get_users()
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

def remove_user(user_id):
    users = get_users()
    if user_id in users:
        users.remove(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

def format_user_list():
    users = get_users()
    if not users:
        return "🚫 No allowed users found."
    return "👥 **Allowed Users List:**\n" + "\n".join([f"`{u}`" for u in users])
    
