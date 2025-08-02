from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID
from user_db import add_user, get_users, remove_user, format_user_list
from helper import download_with_aria2
import os
import time
import math
import aiohttp
import aiofiles
import asyncio
import shutil
from urllib.parse import urlparse, unquote
from utils import sizeof_fmt, sanitize_filename  # helper to format size, sanitize names


CHUNK_SIZE = 8 * 1024 * 1024  # 8MB
active_downloads = {}

bot = Client("4GBUploader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

pending_rename = {}
active_downloads = {}
user_modes = {}

@bot.on_message(filters.command("start"))
async def start(_, msg: Message):
    if msg.from_user.id == OWNER_ID:
        add_user(msg.from_user.id, by_owner=True)

    if msg.from_user.id not in get_users():
        await msg.reply(
            "❌ You dare challenge Madara Uchiha's forbidden uploader?\n\n"
            "⚠️ This bot is sealed for chosen users only.\n"
            "🔗 Want to use the 🔥 URL Uploader Bot?\n"
            "👁‍🔦 Contact the ghost of the Akatsuki ➔ @Madara_Uchiha_lI"
        )
        return

    await msg.reply(
        "👁 Welcome to the Forbidden Grounds...\n"
        "🔗 Send a **magnet**, **torrent**, or **direct URL** to begin the ritual.\n"
        "✍️ Want to rename the offering? Use `/rename filename.ext`\n\n"
        "⚠️ To unveil all secrets and forbidden powers,\n"
        "📜 Use the scroll: `/help` — *the path to knowledge is open to few.*"
    )

@bot.on_message(filters.command("help"))
async def help_command(_, msg: Message):
    await msg.reply(
        "**🌀 Madara Uchiha’s URL Uploader Bot Help**\n\n"
        "**Send:**\n"
        "🔗 Magnet, torrent, or direct URL\n"
        "✍️ Use `/rename filename.ext` to rename before upload\n"
        "💡 Use `/mode normal` or `/mode fast`\n\n"
        "**Commands:**\n"
        "`/start` - Welcome message\n"
        "`/help` - Show this help\n"
        "`/rename` - Rename next upload\n"
        "`/cancel` - Cancel current session\n"
        "`/status` - Show active upload\n"
        "`/broadcast` - Owner only\n"
        "`/addusers` - Owner only\n"
        "`/delusers` - Owner only\n"
        "`/getusers` - Owner only\n\n"
        "☠️ Only chosen users have access.\n"
        "DM @Madara_Uchiha_lI to unlock the gate."
    )

@bot.on_message(filters.command("rename") & filters.reply)
async def rename_command(_, msg: Message):
    user_id = msg.from_user.id
    reply = msg.reply_to_message

    # ✅ Check command argument
    if len(msg.command) < 2:
        return await msg.reply("❌ Usage: `/rename newfilename.ext`\n\n👉 Reply to a file and use the command with new filename.")

    new_name = msg.command[1]

    # ✅ Check if replied message has a downloadable file
    if not (reply.document or reply.video or reply.audio):
        return await msg.reply("❌ Please reply to a media file (document/video/audio).")

    sent = await msg.reply("⏬ Downloading file...")

    # ✅ Download the file
    media = reply.document or reply.video or reply.audio
    original_path = await reply.download()
    
    # ✅ Ensure extension is preserved if not given
    ext = os.path.splitext(media.file_name)[1]
    if not os.path.splitext(new_name)[1]:
        new_name += ext

    new_path = f"./downloads/{new_name}"

    try:
        os.makedirs("./downloads", exist_ok=True)
        shutil.move(original_path, new_path)
    except Exception as e:
        return await sent.edit(f"❌ Failed to rename: {e}")

    # ✅ Upload new renamed file
    await sent.edit("⏫ Uploading renamed file...")

    try:
        await msg.reply_document(document=new_path, caption=f"✅ Renamed to `{new_name}`")
        await sent.delete()
        os.remove(new_path)
    except Exception as e:
        await sent.edit(f"❌ Upload failed: {e}")


@bot.on_message(filters.command("cancel"))
async def cancel_command(_, msg: Message):
    uid = msg.from_user.id
    if uid in pending_rename:
        pending_rename.pop(uid)
        await msg.reply("🛑 Cancelled your request.")
    else:
        await msg.reply("ℹ️ No session to cancel.")

@bot.on_message(filters.command("status"))
async def status_command(_, msg: Message):
    uid = msg.from_user.id
    if uid in active_downloads:
        await msg.reply("📊 Status: Download/upload in progress.")
    else:
        await msg.reply("✅ No active tasks now.")

@bot.on_message(filters.command("broadcast"))
async def broadcast_command(_, msg: Message):
    if msg.from_user.id != OWNER_ID:
        await msg.reply("❌ Only the bot owner can use broadcast.")
        return
    if len(msg.command) < 2:
        await msg.reply("❗ Usage: `/broadcast your message here`")
        return
    text = " ".join(msg.command[1:])
    success, fail = 0, 0
    for uid in get_users():
        try:
            await bot.send_message(uid, text)
            success += 1
        except:
            fail += 1
    await msg.reply(f"📢 Broadcast complete:\n✅ Sent: {success} users\n❌ Failed: {fail}")

@bot.on_message(filters.command("addusers"))
async def add_users_cmd(_, msg: Message):
    if msg.from_user.id != OWNER_ID:
        await msg.reply("❌ You are not allowed to add users.")
        return
    if len(msg.command) < 2:
        await msg.reply("❗ Usage: `/addusers 123456789`")
        return
    try:
        uid = int(msg.command[1])
        add_user(uid, by_owner=True)
        await msg.reply(f"✅ User `{uid}` added to allowed list.")
    except:
        await msg.reply("❌ Invalid user ID.")

@bot.on_message(filters.command("delusers"))
async def del_users_cmd(_, msg: Message):
    if msg.from_user.id != OWNER_ID:
        await msg.reply("❌ You are not allowed to delete users.")
        return
    if len(msg.command) < 2:
        await msg.reply("❗ Usage: `/delusers 123456789`")
        return
    try:
        uid = int(msg.command[1])
        remove_user(uid)
        await msg.reply(f"❌ User `{uid}` removed from allowed list.")
    except:
        await msg.reply("❌ Invalid user ID.")

@bot.on_message(filters.command("getusers"))
async def get_users_list(_, msg: Message):
    if msg.from_user.id != OWNER_ID:
        await msg.reply("❌ Only the owner can view the user list.")
        return
    await msg.reply(format_user_list())

@bot.on_message(filters.text & ~filters.command([
    "start", "help", "rename", "cancel", "status", 
    "broadcast", "addusers", "delusers", "getusers"
]))

async def handle_url(_, message: Message):
    uid = message.from_user.id
    if uid not in get_users():
        await message.reply("❌ Forbidden. Ask @Madara_Uchiha_lI to unlock access.")
        return

    url = message.text.strip()
    reply = await message.reply("📥 Starting fast download...")
    active_downloads[uid] = True

    try:
        await process_upload(message, url, reply)
    finally:
        active_downloads.pop(uid, None)


async def process_upload(message: Message, url: str, reply: Message):
    uid = message.from_user.id
    file_path = None

    try:
        # 🌐 Magnet or Torrent
        if url.startswith("magnet:") or url.endswith(".torrent"):
            file_path, error = download_with_aria2(url)
            if error:
                await reply.edit(f"❌ Aria2 Error: {error}")
                return

        # 🌐 Direct HTTP/HTTPS
        elif url.startswith("http://") or url.startswith("https://"):
            parsed = urlparse(url)
            raw_name = unquote(os.path.basename(parsed.path)) or "file.bin"
            file_name = sanitize_filename(raw_name[:100])
            os.makedirs("downloads", exist_ok=True)
            file_path = f"downloads/{file_name}"

            total = 0
            start = time.time()

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await reply.edit("❌ Direct download failed.")
                        return

                    total_size = int(resp.headers.get("Content-Length", 0))
                    done = 0
                    last_update = 0

                    async with aiofiles.open(file_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                            await f.write(chunk)
                            done += len(chunk)
                            now = time.time()

                            # ⏱️ Update every 2 seconds
                            if now - last_update > 2:
                                percent = done / total_size * 100 if total_size else 0
                                bar = progress_bar(percent)
                                speed = sizeof_fmt(done / (now - start + 1e-6)) + "/s"
                                status = (
                                    f"📥 **Downloading:** {percent:.2f}%\n"
                                    f"{bar}\n"
                                    f"➩ **Speed:** {speed}\n"
                                    f"➩ **Done:** {sizeof_fmt(done)} / {sizeof_fmt(total_size)}"
                                )
                                await reply.edit(status)
                                last_update = now

        else:
            await reply.edit("❌ Invalid URL.")
            return

        if not os.path.exists(file_path):
            await reply.edit("❌ File not found after download.")
            return

        # ✅ Upload
        await reply.edit("📤 Uploading to Telegram...")
        start = time.time()
        file_size = os.path.getsize(file_path)

        sent = await message.reply_document(
            file_path,
            caption=f"✅ `{os.path.basename(file_path)}`\n📦 {sizeof_fmt(file_size)}\n⏱️ Uploaded in {round(time.time() - start, 2)}s"
        )

        # 🧹 Auto-clean
        await asyncio.sleep(600)
        await reply.delete()
        await sent.delete()
        os.remove(file_path)

    except Exception as e:
        await reply.edit(f"❌ Error: {e}")


def progress_bar(percent):
    full = int(percent // 10)
    empty = 10 - full
    return "[" + "▰" * full + "▱" * empty + "]"
    finally:
        active_downloads.pop(uid, None)

print("🚀 Madara Uchiha's Forbidden Uploader Bot has awakened!")
bot.run()
