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
    try:
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
        while not download.is_complete and not download.error_message:
            await asyncio.sleep(2)
            download = aria2.get_download(download.gid)

        # Check for error
        if download.error_message:
            return None, f"❌ Aria2 Error: {download.error_message}"

        # 🔍 Select the best file to return
        files = download.files
        if not files:
            return None, "❌ No files found in download."

        # 🥇 Priority: pick the largest .mkv or video file
        video_exts = ['.mkv', '.mp4', '.avi', '.mov', '.webm']
        video_files = [f for f in files if os.path.splitext(f.path)[-1].lower() in video_exts]

        if video_files:
            largest_video = max(video_files, key=lambda x: x.length)
            return largest_video.path, None

        # 🥈 Otherwise, return the largest file
        largest_file = max(files, key=lambda x: x.length)
        return largest_file.path, None

    except Exception as e:
        return None, f"⚠️ Download Failed: {str(e)}"
        
