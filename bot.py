from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN
from helper import download_with_aria2
import os
import time
import aiohttp

bot = Client("4GBUploader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start(_, msg: Message):
    await msg.reply("👋 Welcome! Send me a magnet link or direct URL to upload to Telegram.")

@bot.on_message(filters.text & ~filters.command(["start"]))
async def handle_url(_, message: Message):
    url = message.text.strip()
    reply = await message.reply("📥 Downloading...")

    try:
        if url.startswith("magnet:") or url.endswith(".torrent"):
            file_path, error = download_with_aria2(url)
        elif url.startswith("http://") or url.startswith("https://"):
            file_path = f"downloads/{url.split('/')[-1]}"
            os.makedirs("downloads", exist_ok=True)

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await reply.edit("❌ Download failed.")
                        return
                    with open(file_path, "wb") as f:
                        while True:
                            chunk = await resp.content.read(1024 * 1024)
                            if not chunk:
                                break
                            f.write(chunk)
            error = None
        else:
            await reply.edit("❌ Invalid link.")
            return

        if error:
            await reply.edit(f"❌ Error: {error}")
            return

        await reply.edit("📤 Uploading to Telegram...")

        start = time.time()
        await message.reply_document(file_path, caption=f"✅ Done in {round(time.time()-start, 2)}s")
        await reply.delete()
        os.remove(file_path)

    except Exception as e:
        await reply.edit(f"❌ Error: {e}")

bot.run()
