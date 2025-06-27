from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, ALLOWED_USERS, OWNER_ID
from user_db import add_user, get_users
from helper import download_with_aria2
import os
import time
import aiohttp
import asyncio

bot = Client("4GBUploader", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

pending_rename = {}
active_downloads = {}
user_modes = {}

@bot.on_message(filters.command("start"))
async def start(_, msg: Message):
    add_user(msg.from_user.id)
    if msg.from_user.id not in ALLOWED_USERS:
        await msg.reply(
            "❌ You dare challenge Madara Uchiha's forbidden uploader?\n\n"
            "⚠️ This bot is sealed for chosen users only.\n"
            "🔗 Want to use the 🔥 URL Uploader Bot?\n"
            "👁‍🗨 Contact the ghost of the Akatsuki ➤ @Madara_Uchiha_lI"
        )
        return
    await msg.reply("👋 Welcome! Send a magnet, torrent or direct URL.\n"
                    "➕ To rename, send `/rename filename.ext` after the link.")

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
        "`/broadcast` - Owner only: send message to all users\n\n"
        "☠️ Only chosen users have access.\n"
        "DM @Madara_Uchiha_lI to unlock the gate."
    )

@bot.on_message(filters.command("rename"))
async def rename_command(_, msg: Message):
    uid = msg.from_user.id
    if uid not in ALLOWED_USERS:
        await msg.reply("❌ Access denied.")
        return
    if len(msg.command) < 2:
        await msg.reply("❌ Usage: `/rename newfilename.ext`")
        return
    if uid not in pending_rename:
        await msg.reply("❗ No URL sent yet. Send a link first.")
        return
    pending_rename[uid]["rename"] = msg.command[1]
    await msg.reply(f"✅ Filename set to: `{msg.command[1]}`")

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

@bot.on_message(filters.command("mode"))
async def mode_command(_, msg: Message):
    uid = msg.from_user.id
    if len(msg.command) < 2:
        await msg.reply("❌ Usage: `/mode normal` or `/mode fast`")
        return
    mode = msg.command[1].lower()
    if mode in ["normal", "fast"]:
        user_modes[uid] = mode
        await msg.reply(f"⚙️ Mode set to: `{mode}`")
    else:
        await msg.reply("❌ Invalid mode. Use `normal` or `fast`")

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

@bot.on_message(filters.text & ~filters.command(["start", "help", "rename", "cancel", "status", "mode", "broadcast"]))
async def handle_url(_, message: Message):
    uid = message.from_user.id
    if uid not in ALLOWED_USERS:
        await message.reply("❌ Forbidden. Ask @Madara_Uchiha_lI to unlock access.")
        return
    if uid in pending_rename and not message.text.strip().startswith(("http", "magnet:")):
        pending_rename[uid]["rename"] = message.text.strip()
        return await process_upload(message, pending_rename[uid]["url"], pending_rename.pop(uid)["msg"])
    url = message.text.strip()
    reply = await message.reply("📥 Preparing download...")
    pending_rename[uid] = {"url": url, "msg": message}
    active_downloads[uid] = True
    await reply.edit("✍️ Send `/rename filename.ext` in 30s to rename.")
    await asyncio.sleep(30)
    if uid in pending_rename:
        await process_upload(message, url, message)
        pending_rename.pop(uid)

async def process_upload(message: Message, url: str, user_msg: Message):
    uid = message.from_user.id
    reply = await user_msg.reply("📥 Downloading...")
    try:
        if url.startswith("magnet:") or url.endswith(".torrent"):
            file_path, error = download_with_aria2(url)
        elif url.startswith("http://") or url.startswith("https://"):
            file_name = url.split("/")[-1]
            file_path = f"downloads/{file_name}"
            os.makedirs("downloads", exist_ok=True)
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await reply.edit("❌ Download failed.")
                        active_downloads.pop(uid, None)
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
            active_downloads.pop(uid, None)
            return
        rename = pending_rename.get(uid, {}).get("rename")
        if rename:
            new_path = os.path.join("downloads", rename)
            os.rename(file_path, new_path)
            file_path = new_path
        await reply.edit("📤 Uploading to Telegram...")
        start = time.time()
        sent = await message.reply_document(file_path, caption=f"✅ Done in {round(time.time() - start, 2)}s")
        await asyncio.sleep(60)
        await reply.delete()
        await sent.delete()
        os.remove(file_path)
    except Exception as e:
        await reply.edit(f"❌ Error: {e}")
    finally:
        active_downloads.pop(uid, None)

bot.run()
