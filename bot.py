from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID
from user_db import add_user, get_users, remove_user, format_user_list, is_user
from helper import download_with_aria2

import os
import time
import aiohttp
import aiofiles
import asyncio
from urllib.parse import urlparse, unquote
import uuid
import re

bot = Client("4GBUploader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

pending_rename = {}
active_downloads = {}
user_modes = {}
user_last_request = {}

def sanitize_filename(name):
    name = re.sub(r"[^\w\-_.]", "_", name)
    return name.strip("._")[:100]

@bot.on_message(filters.command("start"))
async def start(_, msg: Message):
    uid = msg.from_user.id
    if uid == OWNER_ID:
        add_user(uid)

    if uid not in get_users():
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
        "`/mode` - Set upload mode\n"
        "`/broadcast` - Owner only\n"
        "`/addusers` - Owner only\n"
        "`/delusers` - Owner only\n"
        "`/getusers` - Owner only\n\n"
        "☠️ Only chosen users have access.\n"
        "DM @Madara_Uchiha_lI to unlock the gate."
    )

@bot.on_message(filters.command("rename"))
async def rename_command(_, msg: Message):
    uid = msg.from_user.id
    if uid not in get_users():
        return await msg.reply("❌ Access denied.")
    if len(msg.command) < 2:
        return await msg.reply("❌ Usage: `/rename newfilename.ext`")
    if uid not in pending_rename:
        return await msg.reply("❗ No URL sent yet. Send a link first.")
    safe_name = sanitize_filename(msg.command[1])
    pending_rename[uid]["rename"] = safe_name
    await msg.reply(f"✅ Filename set to: `{safe_name}`")

@bot.on_message(filters.command("cancel"))
async def cancel_command(_, msg: Message):
    uid = msg.from_user.id
    if pending_rename.pop(uid, None):
        await msg.reply("🛑 Cancelled your request.")
    else:
        await msg.reply("ℹ️ No session to cancel.")

@bot.on_message(filters.command("status"))
async def status_command(_, msg: Message):
    uid = msg.from_user.id
    await msg.reply("📊 Status: Download/upload in progress." if uid in active_downloads else "✅ No active tasks now.")

@bot.on_message(filters.command("mode"))
async def mode_command(_, msg: Message):
    uid = msg.from_user.id
    if len(msg.command) < 2:
        return await msg.reply("❌ Usage: `/mode normal` or `/mode fast`")
    mode = msg.command[1].lower()
    if mode in ["normal", "fast"]:
        user_modes[uid] = mode
        await msg.reply(f"⚙️ Mode set to: `{mode}`")
    else:
        await msg.reply("❌ Invalid mode. Use `normal` or `fast`")

@bot.on_message(filters.command("broadcast"))
async def broadcast_command(_, msg: Message):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply("❌ Only the bot owner can use broadcast.")
    if len(msg.command) < 2:
        return await msg.reply("❗ Usage: `/broadcast your message here`")
    text = " ".join(msg.command[1:])
    success, fail = 0, 0
    for uid in get_users():
        try:
            await bot.send_message(uid, text)
            success += 1
        except Exception as e:
            print(f"[Broadcast error] {uid}: {e}")
            fail += 1
    await msg.reply(f"📢 Broadcast complete:\n✅ Sent: {success} users\n❌ Failed: {fail}")

@bot.on_message(filters.command("addusers"))
async def add_users_cmd(_, msg: Message):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply("❌ You are not allowed to add users.")
    if len(msg.command) < 2:
        return await msg.reply("❗ Usage: `/addusers 123456789`")
    try:
        uid = int(msg.command[1])
        add_user(uid)
        await msg.reply(f"✅ User `{uid}` added to allowed list.")
    except:
        await msg.reply("❌ Invalid user ID.")

@bot.on_message(filters.command("delusers"))
async def del_users_cmd(_, msg: Message):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply("❌ You are not allowed to delete users.")
    if len(msg.command) < 2:
        return await msg.reply("❗ Usage: `/delusers 123456789`")
    try:
        uid = int(msg.command[1])
        remove_user(uid)
        await msg.reply(f"❌ User `{uid}` removed from allowed list.")
    except:
        await msg.reply("❌ Invalid user ID.")

@bot.on_message(filters.command("getusers"))
async def get_users_list(_, msg: Message):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply("❌ Only the owner can view the user list.")
    await msg.reply(format_user_list())

@bot.on_message(filters.private & ~filters.command([
    "start", "help", "rename", "cancel", "status", "mode", "broadcast", "addusers", "delusers", "getusers"
]))
async def handle_url(_, message: Message):
    uid = message.from_user.id
    if uid not in get_users():
        return await message.reply("❌ Forbidden. Ask @Madara_Uchiha_lI to unlock access.")
    if uid in user_last_request and time.time() - user_last_request[uid] < 20:
        return await message.reply("⏳ Please wait a few seconds before sending another request.")
    user_last_request[uid] = time.time()

    url = message.text.strip()
    reply = await message.reply("📥 Starting download...")
    pending_rename[uid] = {"url": url, "msg": message}
    active_downloads[uid] = True
    await process_upload(message, url, message)
    pending_rename.pop(uid, None)

async def process_upload(message: Message, url: str, user_msg: Message):
    uid = message.from_user.id
    reply = await user_msg.reply("📥 Downloading...")
    file_path = None
    try:
        mode = user_modes.get(uid, "normal")
        chunk_size = 10 * 1024 * 1024 if mode == "fast" else 5 * 1024 * 1024
        timeout = aiohttp.ClientTimeout(total=300)

        # 🔥 Torrent or Magnet
        if url.startswith("magnet:") or url.endswith(".torrent"):
            file_path, error = await download_with_aria2(url)
            if error:
                await reply.edit(error)
                return

        # 🌐 Direct HTTP/HTTPS
        elif url.startswith("http://") or url.startswith("https://"):
            os.makedirs("downloads", exist_ok=True)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await reply.edit("❌ Download failed.")
                        return

                    # 🔍 Try to extract filename from headers
                    cd = resp.headers.get("Content-Disposition")
                    if cd:
                        match = re.search('filename="?([^"]+)"?', cd)
                        file_name = match.group(1) if match else None
                    else:
                        file_name = None

                    # 🔁 Fallback to URL path
                    if not file_name:
                        parsed = urlparse(url)
                        file_name = unquote(os.path.basename(parsed.path))

                    # 🧼 Final fallback
                    if not file_name or file_name.strip() == "":
                        file_name = f"downloaded_{uuid.uuid4().hex[:8]}.bin"

                    file_name = sanitize_filename(file_name[:100])
                    file_path = f"downloads/{uuid.uuid4().hex}_{file_name}"

                    # 💾 Download file
                    async with aiofiles.open(file_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(chunk_size):
                            await f.write(chunk)

        else:
            await reply.edit("❌ Invalid link.")
            return

        # 📂 File existence check
        if not file_path or not os.path.exists(file_path):
            await reply.edit("❌ Download failed.")
            return

        # 🚫 2GB file limit
        if os.path.getsize(file_path) > 2 * 1024 * 1024 * 1024:
            await reply.edit("❌ File is too large (2GB limit).")
            os.remove(file_path)
            return

        # ✍️ Allow rename before upload
        await reply.edit("✍️ Send `/rename filename.ext` within 30s to rename the file...")
        for _ in range(30):
            await asyncio.sleep(1)
            if uid in pending_rename and "rename" in pending_rename[uid]:
                break

        rename = pending_rename.get(uid, {}).get("rename")
        if rename:
            new_path = os.path.join("downloads", sanitize_filename(rename))
            os.rename(file_path, new_path)
            file_path = new_path

        # 📤 Upload to Telegram
        await reply.edit("📤 Uploading to Telegram...")
        sent = await message.reply_document(file_path, caption="✅ Upload complete.")

        # ⏳ Auto delete after 5 minutes
        await asyncio.sleep(300)
        await reply.delete()
        await sent.delete()

        # 🧹 Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await reply.edit(f"❌ Error: {e}")
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    finally:
        active_downloads.pop(uid, None)

print("🚀 Madara Uchiha's Forbidden Uploader Bot has awakened!")
bot.run()
