import aria2p

aria2 = aria2p.API(
    aria2p.Client(host="http://localhost", port=6800, secret="")  # Add your secret if you set one
)

def download_with_aria2(url):
    try:
        download = aria2.add_uris([url])
        download.wait_for_complete()  # ✅ correct method
        if download.is_complete:
            return download.files[0].path, None
        else:
            return None, "Download did not complete."
    except Exception as e:
        return None, str(e)
        
