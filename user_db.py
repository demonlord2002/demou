import json
from config import USERS_FILE
from datetime import datetime

LOG_FILE = "log.txt"

def log_action(action):
    with open(LOG_FILE, "a") as log:
        log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {action}\n")

def get_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def add_user(user_id, by_owner=False):
    users = get_users()
    if user_id not in users and by_owner:
        users.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)
        log_action(f"User added: {user_id}")

def remove_user(user_id):
    users = get_users()
    if user_id in users:
        users.remove(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)
        log_action(f"User removed: {user_id}")

def format_user_list():
    users = get_users()
    if not users:
        return "👥 No users currently allowed."
    text = "👥 Allowed Users List:\n"
    for uid in users:
        text += f"[`{uid}`](tg://user?id={uid})\n"
    return text


    
