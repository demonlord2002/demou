import aria2p
import os
import time
import math

# Connect to aria2c with RPC secret
aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret="madara123"
    )
)

def format_bytes(size):
    # Format file size (e.g., MB, GB)
    power = 2**10
    n = 0
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    while size >= power and n < len(units) - 1:
        size /= power
        n += 1
    return f"{size:.2f} {units[n]}"

def download_with_aria2(url):
    try:
        start_time = time.time()
        download = aria2.add_uris([url])

        # Wait until the download is finished
        download.wait_for_completion()

        if not download.is_complete:
            return None, "❌ Download failed or incomplete."

        valid_files = []
        video_files = []

        for f in download.files:
            path = f.path
            if not os.path.exists(path):
                continue

            # Clean unsafe characters in filename
            safe_name = "".join(c if c.isalnum() or c in "-_.()" else "_" for c in os.path.basename(path))
            safe_path = os.path.join(os.path.dirname(path), safe_name)
            if path != safe_path:
                os.rename(path, safe_path)
                path = safe_path

            size = os.path.getsize(path)
            ext = os.path.splitext(path)[1].lower()

            if ext in [".mp4", ".mkv"] and size > 500 * 1024:  # 500KB+ video
                video_files.append((path, size))
            elif size > 100 * 1024:
                valid_files.append((path, size))

        # Pick largest video file or fallback to largest other file
        if video_files:
            best_file = max(video_files, key=lambda x: x[1])
        elif valid_files:
            best_file = max(valid_files, key=lambda x: x[1])
        else:
            return None, "❌ No valid downloadable file found."

        end_time = time.time()
        duration = end_time - start_time
        size_str = format_bytes(best_file[1])
        speed = format_bytes(best_file[1] / duration) + "/s"
        time_taken = f"{duration:.2f} sec"

        # Return tuple: file path, caption info
        caption = f"✅ File: `{os.path.basename(best_file[0])}`\n📦 Size: `{size_str}`\n🚀 Speed: `{speed}`\n⏱️ Time: `{time_taken}`"
        return best_file[0], caption

    except Exception as e:
        return None, f"⚠️ Error: {str(e)}"
        
