import aria2p

aria2 = aria2p.API(
    aria2p.Client(host="http://localhost", port=6800, secret="")
)

def download_with_aria2(url):
    try:
        download = aria2.add_uris([url])
        download.wait_for_complete()
        return download.files[0].path, None
    except Exception as e:
        return None, str(e)
