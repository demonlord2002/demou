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
        for f in download.files:
            if not os.path.exists(f.path):
                continue
            size = os.path.getsize(f.path)
            ext = os.path.splitext(f.path)[1].lower()

            # ⛔ Skip trash files
            junk_exts = [
                ".txt", ".url", ".nfo", ".ds_store", ".exe", ".lnk", ".ini",
                ".html", ".htm", ".xml", ".bat", ".sh", ".cmd", ".applicant"
            ]
            if ext in junk_exts or size < 1024 * 100:
                continue

            valid_files.append((f.path, size))

        if not valid_files:
            return None, "No valid file found in the torrent."

        # ✅ Pick largest valid file
        best_file = max(valid_files, key=lambda x: x[1])[0]
        return best_file, None

    except Exception as e:
        return None, str(e)
        
