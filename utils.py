import math
import re

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T"]:
        if abs(num) < 1024.0:
            return f"{num:.2f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.2f} P{suffix}"

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name).strip()
