import math
import os
import re
import uuid

# 📦 Convert bytes to human-readable format
def sizeof_fmt(size):
    # 2**10 = 1024
    power = 1024
    n = 0
    power_labels = {0: "", 1: "K", 2: "M", 3: "G", 4: "T"}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {power_labels[n]}B"

# 📁 Sanitize filename
def sanitize_filename(name):
    name = re.sub(r"[^\w\s.-]", "", name)
    name = re.sub(r"\s+", "_", name)
    return name.strip("._")

# 🆔 Generate unique filename
def get_unique_filename(original_name):
    ext = os.path.splitext(original_name)[-1]
    name = sanitize_filename(os.path.splitext(original_name)[0])
    uid = uuid.uuid4().hex[:8]
    return f"{name}_{uid}{ext}"
