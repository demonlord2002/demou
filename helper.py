import aria2p
import os

# Connect to aria2c with RPC secret
aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret="madara123"
    )
)

def download_with_aria2(url):
    try:
        download = aria2.add_uris([url])
        download.wait_for_completion()

        if not download.is_complete:
            return None, "Download did not complete."

        valid_files = []
        video_files = []

        for f in download.files:
            if not os.path.exists(f.path):
                continue
            size = os.path.getsize(f.path)
            ext = os.path.splitext(f.path)[1].lower()

            if ext in [".mp4", ".mkv"] and size > 100 * 1024:
                video_files.append((f.path, size))
            elif size > 100 * 1024:
                valid_files.append((f.path, size))

        if video_files:
            best_file = max(video_files, key=lambda x: x[1])[0]
        elif valid_files:
            best_file = max(valid_files, key=lambda x: x[1])[0]
        else:
            return None, "No valid media file found."

        return best_file, None

    except Exception as e:
        return None, str(e)

