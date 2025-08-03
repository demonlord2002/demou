from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, OWNER_ID
from user_db import add_user, get_users, remove_user, format_user_list
from helper import download_with_aria2
from pyrogram.enums import ChatAction
import os
import time
import aiohttp
import aiofiles
import asyncio
from urllib.parse import urlparse, unquote

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
    "start", "help", "rename", "cancel", "status", "mode",
    "broadcast", "addusers", "delusers", "getusers"
]))
async def handle_url(_, message: Message):
    uid = message.from_user.id
    if uid not in get_users():
        await message.reply("❌ Forbidden. Ask @Madara_Uchiha_lI to unlock access.")
        return
    url = message.text.strip()
    reply = await message.reply("📥 Starting download...")
    pending_rename[uid] = {"url": url, "msg": message}
    active_downloads[uid] = True
    await process_upload(message, url, message)
    pending_rename.pop(uid, None)

async def process_upload(message: Message, url: str, user_msg: Message):
    uid = message.from_user.id
    reply = await user_msg.reply("📥 Downloading...")

    try:
        file_path = None
        error = None

        # Handle magnet/torrent with aria2
        if url.startswith("magnet:") or url.endswith(".torrent"):
            file_path, error = download_with_aria2(url)

        # Direct HTTP/HTTPS
        elif url.startswith("http://") or url.startswith("https://"):
            parsed = urlparse(url)
            file_name = unquote(os.path.basename(parsed.path))[:100]
            os.makedirs("downloads", exist_ok=True)
            file_path = f"downloads/{file_name}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await reply.edit("❌ Download failed.")
                        active_downloads.pop(uid, None)
                        return

                    total_size = int(resp.headers.get('Content-Length', 0))
                    downloaded = 0
                    chunk_size = 5 * 1024 * 1024  # 5 MB chunks

                    async with aiofiles.open(file_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(chunk_size):
                            await f.write(chunk)
                            downloaded += len(chunk)

            error = None

        else:
            await reply.edit("❌ Invalid link.")
            active_downloads.pop(uid, None)
            return

        if not file_path or error:
            await reply.edit(f"❌ Download failed: {error or 'Unknown error'}")
            active_downloads.pop(uid, None)
            return

        await reply.edit("✍️ Send `/rename filename.ext` within 15s if you want to rename the file...")
        await asyncio.sleep(15)

        rename = pending_rename.get(uid, {}).get("rename")
        if rename:
            new_path = os.path.join("downloads", rename)
            os.rename(file_path, new_path)
            file_path = new_path

        await reply.edit("📤 Uploading to Telegram...")
        await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_DOCUMENT)

        start = time.time()
        sent = await bot.send_document(
            chat_id=uid,
            document=file_path,
            caption=f"✅ Done in {round(time.time() - start, 2)}s",
            force_document=True
        )

        ✅ Cleanup immediately after upload
        os.remove(file_path)
        await reply.delete()
        await sent.delete()

    except Exception as e:
        await reply.edit(f"❌ Error: {e}")
    finally:
        active_downloads.pop(uid, None)


print("🚀 Madara Uchiha's Forbidden Uploader Bot has awakened!")
bot.run()
