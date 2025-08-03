import aria2p
import os
import uuid
import re

# 🔌 Connect to Aria2 RPC server
aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret="madara123"
    )
)

# 🧼 Sanitize filename to avoid OS errors
def sanitize_filename(name):
    # Remove unsafe characters
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.strip()

# 📁 Safe Aria2 download with auto filename
def download_with_aria2(url):
    try:
        # Extract base name from URL
        base_name = os.path.basename(url.split("?")[0])
        base_name = sanitize_filename(base_name or "file")

        # Add random UUID to prevent overwrite
        unique_name = f"{uuid.uuid4().hex[:8]}_{base_name}"

        # Target directory
        download_dir = "downloads"
        os.makedirs(download_dir, exist_ok=True)

        # Start download
        download = aria2.add_uris([url], options={
            "dir": download_dir,
            "out": unique_name,
            "max-connection-per-server": "16",
            "split": "16"
        })

        # Wait for completion
        while not download.is_complete:
            if download.error_message:
                raise Exception(f"Aria2 error: {download.error_message}")
            download.update()
        
        # Full path
        file_path = os.path.join(download_dir, unique_name)

        if not os.path.exists(file_path):
            raise Exception("Download failed or file missing.")

        return file_path

    except Exception as e:
        raise Exception(f"Download failed: {e}")

# 🔄 Human-readable file size
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P"]:
        if abs(num) < 1024.0:
            return f"{num:.2f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.2f}Y{suffix}"
