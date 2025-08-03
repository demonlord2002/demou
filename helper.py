import aria2p
import os
import time

# Connect to running aria2c RPC daemon (ensure aria2c is started with --enable-rpc)
aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret="madara123"
    )
)

# 📦 Convert bytes to human-readable format
def format_bytes(size):
    power = 1024
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    for unit in units:
        if size < power:
            return f"{size:.2f} {unit}"
        size /= power
    return f"{size:.2f} TB"

# 🚀 Main download logic using aria2
def download_with_aria2(url):
    try:
        start_time = time.perf_counter()

        # Add URL to aria2 queue
        download = aria2.add_uris([url], options={
            "max-connection-per-server": "16",  # 🚀 Increase parallel connections
            "split": "16",
            "min-split-size": "1M",
            "max-download-limit": "0",  # No speed limit
            "dir": "downloads"  # Store in downloads/
        })

        # Wait for the download to complete
        download.wait_for_completion(timeout=1800)  # 30 min max

        if not download.is_complete:
            return None, "❌ Download failed or timed out."

        # Filter valid files
        valid_files = []
        video_files = []

        for file in download.files:
            path = file.path
            if not os.path.exists(path):
                continue

            # Sanitize name
            safe_name = "".join(c if c.isalnum() or c in "-_.()" else "_" for c in os.path.basename(path))
            safe_path = os.path.join(os.path.dirname(path), safe_name)
            if path != safe_path:
                os.rename(path, safe_path)
                path = safe_path

            size = os.path.getsize(path)
            ext = os.path.splitext(path)[1].lower()

            if ext in [".mp4", ".mkv", ".webm"] and size > 500 * 1024:
                video_files.append((path, size))
            elif size > 100 * 1024:
                valid_files.append((path, size))

        # Select the largest usable file
        if video_files:
            best_file = max(video_files, key=lambda x: x[1])
        elif valid_files:
            best_file = max(valid_files, key=lambda x: x[1])
        else:
            return None, "❌ No valid files found to upload."

        end_time = time.perf_counter()
        duration = max(end_time - start_time, 1)

        size_str = format_bytes(best_file[1])
        speed = format_bytes(best_file[1] / duration) + "/s"
        time_taken = f"{duration:.2f} sec"

        caption = (
            f"✅ File: `{os.path.basename(best_file[0])}`\n"
            f"📦 Size: `{size_str}`\n"
            f"🚀 Speed: `{speed}`\n"
            f"⏱️ Time: `{time_taken}`"
        )

        return best_file[0], caption

    except Exception as e:
        return None, f"⚠️ Error: {str(e)}"
        
