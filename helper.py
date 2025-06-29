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

        # Get all downloaded files
        valid_files = []
        for f in download.files:
            if not os.path.exists(f.path):
                continue
            size = os.path.getsize(f.path)
            ext = os.path.splitext(f.path)[1].lower()

            # Skip junk extensions
            if ext in [".nfo", ".txt", ".url", ".exe", ".applicant"]:
                continue
            if size < 1024 * 100:  # Skip files less than 100 KB
                continue

            valid_files.append((f.path, size))

        if not valid_files:
            return None, "No usable file found in the torrent."

        # Pick largest valid file
        best_file = max(valid_files, key=lambda x: x[1])[0]
        return best_file, None

    except Exception as e:
        return None, str(e)
        
