import math
import os
import re
import uuid
import asyncio
import aria2p

# 📦 Convert bytes to human-readable format
def sizeof_fmt(size):
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

# 🚀 Download using aria2 (supports HTTP, magnet, torrent)
async def download_with_aria2(url, download_path="downloads"):
    aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=6800,
            secret="madara123"
        )
    )

    # Add URI (magnet/torrent/http)
    download = aria2.add_uri([url], options={"dir": download_path})

    # Wait until complete
    while not download.is_complete:
        await asyncio.sleep(2)
        download = aria2.get_download(download.gid)

    # Return final file path
    return download.files[0].path
    
