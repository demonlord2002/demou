import aria2p

# Connect to aria2c with RPC secret (make sure you run aria2c with --rpc-secret=madara123)
aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=6800,
        secret="madara123"  # Your aria2 RPC secret
    )
)

def download_with_aria2(url):
    try:
        # Add URI and start downloading
        download = aria2.add_uris([url])

        # Wait until download finishes
        download.wait_for_completion()

        # If completed, return file path
        if download.is_complete:
            return download.files[0].path, None
        else:
            return None, "Download did not complete."

    except Exception as e:
        return None, str(e)
        
