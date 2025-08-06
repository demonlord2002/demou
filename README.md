
<p align="center"><a href="https://dashboard.heroku.com/new?template=https://github.com/demonlord2002/demonurl"> <img src="https://www.herokucdn.com/deploy/button.svg"></a></p>


# 🚀 Telegram URL + Magnet Uploader Bot (4GB Supported)

This is a Telegram bot that allows you to download files from:
- ✅ Magnet Links
- ✅ Torrent Files
- ✅ Direct HTTP/HTTPS URLs

It uploads them to Telegram (up to 4GB per file).

---

## 🧰 Features

- 4GB upload support
- Uses aria2c for magnet/torrent download
- Supports direct URLs (via aiohttp)
- Uploads to Telegram via Pyrogram

---

## 🛠️ VPS Deployment Guide

### 1. Connect to VPS

```bash
ssh your_username@your_vps_ip
```

---

### 2. Install System Requirements

```bash
sudo apt update && sudo apt install -y python3 python3-pip git aria2 tmux unzip
```

---

### 3. Upload and Unzip the Bot Code

If you already uploaded the ZIP:

```bash
unzip url_uploader_bot.zip
cd url_uploader_bot
```

If cloning from GitHub:

```bash
git clone https://github.com/yourusername/url_uploader_bot.git
cd url_uploader_bot
```

---

### 4. Install Python Requirements

```bash
pip3 install -r requirements.txt
```

---

### 5. Set Environment Variables

You can either set them for the session:

```bash
export API_ID=your_api_id
export API_HASH=your_api_hash
export BOT_TOKEN=your_bot_token
```

Or make them permanent:

```bash
echo 'export API_ID=your_api_id' >> ~/.bashrc
echo 'export API_HASH=your_api_hash' >> ~/.bashrc
echo 'export BOT_TOKEN=your_bot_token' >> ~/.bashrc
source ~/.bashrc
```

---

### 6. Run the Bot

```bash
python3 bot.py
```

---

### 7. Keep It Running with tmux

```bash
tmux new -s uploaderbot
python3 bot.py
# Press Ctrl+B then D to detach
```

To reattach:

```bash
tmux attach -t uploaderbot
```

---

## 🔒 Optional: Restrict to Your Telegram User Only

In `bot.py`, add:

```python
if message.from_user.id != OWNER_ID:
    await message.reply("❌ You are not authorized to use this bot.")
    return
```

And define `OWNER_ID` in `config.py`.

---

## 🧹 Clean Up Downloaded Files

All files are auto-deleted after upload.

---

## ✅ Done!

Your bot is now live on your VPS and can:
- Download from magnet links or URLs
- Upload files to Telegram
- Run 24/7 using `tmux`
