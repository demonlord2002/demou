import subprocess
import os

ARIA2C_CMD = "aria2c --max-connection-per-server=10 --split=10 --dir=downloads"

def download_with_aria2(url):
    os.makedirs("downloads", exist_ok=True)
    cmd = f"{ARIA2C_CMD} \"{url}\""
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        return None, stderr.decode()

    for root, dirs, files in os.walk("downloads"):
        for file in files:
            return os.path.join(root, file), None

    return None, "No file found."
