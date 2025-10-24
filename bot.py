import os
import asyncio
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ─────────────────────────────────
# Bot Configuration
# ─────────────────────────────────
API_ID = "24569375"  # Get from my.telegram.org
API_HASH = "fa07c6910ac4d5bc2fd4db809cd5063f"  # Get from my.telegram.org
BOT_TOKEN = "7231961104:AAG8iYF26MvUkUu_MFl1soxyd09y0zpcIuU"  # Get from @BotFather

# YouTube Download API Configuration
API_URL = "https://teaminflex.xyz"
API_KEY = "INFLEX20512028D"  # Get from @InflexAPIBot

# Initialize bot
app = Client(
    "youtube_downloader_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Store user states
user_states = {}

# ─────────────────────────────────
# YouTube Download Functions
# ─────────────────────────────────
async def download_song(link: str) -> str:
    """Download YouTube audio"""
    video_id = link.split('v=')[-1].split('&')[0]
    print(f"🎵 [AUDIO] Starting download process for ID: {video_id}")
    
    if not video_id or len(video_id) < 5:
        return None
        
    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.webm")
    
    if os.path.exists(file_path):
        print(f"🎵 [LOCAL] downloaded from LOCAL for ID: {video_id}")
        return file_path
        
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"url": video_id, "type": "audio"}
            headers = {"X-API-KEY": API_KEY}
            
            async with session.post(f"{API_URL}/download", json=payload, headers=headers) as response:
                if response.status == 401:
                    print("[API] Your provided key is not valid, please use a valid one or get it from @InflexAPIBot")
                    return None
                if response.status != 200:
                    print(f"[AUDIO] API returned status {response.status} for ID: {video_id}")
                    return None
                    
                data = await response.json()
                if data.get("status") != "success" or not data.get("download_url"):
                    print(f"[AUDIO] API error for ID: {video_id} - {data}")
                    return None
                    
                download_link = f"{API_URL}{data['download_url']}"
                
                async with session.get(download_link) as file_response:
                    if file_response.status != 200:
                        print(f"[AUDIO] Download failed with status {file_response.status} for ID: {video_id}")
                        return None
                        
                    with open(file_path, "wb") as f:
                        async for chunk in file_response.content.iter_chunked(8192):
                            f.write(chunk)
                            
        print(f"🎵 [API] downloaded from API for ID: {video_id}")
        return file_path
    except Exception as e:
        print(f"[AUDIO] Exception for ID: {video_id} - {e}")
        return None


async def download_video(link: str) -> str:
    """Download YouTube video"""
    video_id = link.split('v=')[-1].split('&')[0]
    print(f"🎥 [VIDEO] Starting download process for ID: {video_id}")
    
    if not video_id or len(video_id) < 5:
        return None
        
    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mkv")
    
    if os.path.exists(file_path):
        print(f"🎥 [LOCAL] downloaded from LOCAL for ID: {video_id}")
        return file_path
        
    try:
        async with aiohttp.ClientSession() as session:
            payload = {"url": video_id, "type": "video"}
            headers = {"X-API-KEY": API_KEY}
            
            async with session.post(f"{API_URL}/download", json=payload, headers=headers) as response:
                if response.status == 401:
                    print("[API] Your provided key is not valid, please use a valid one or get it from @InflexAPIBot")
                    return None
                if response.status != 200:
                    print(f"[VIDEO] API returned status {response.status} for ID: {video_id}")
                    return None
                    
                data = await response.json()
                if data.get("status") != "success" or not data.get("download_url"):
                    print(f"[VIDEO] API error for ID: {video_id} - {data}")
                    return None
                    
                download_link = f"{API_URL}{data['download_url']}"
                
                async with session.get(download_link) as file_response:
                    if file_response.status != 200:
                        print(f"[VIDEO] Download failed with status {file_response.status} for ID: {video_id}")
                        return None
                        
                    with open(file_path, "wb") as f:
                        async for chunk in file_response.content.iter_chunked(8192):
                            f.write(chunk)
                            
        print(f"🎥 [API] downloaded from API for ID: {video_id}")
        return file_path
    except Exception as e:
        print(f"[VIDEO] Exception for ID: {video_id} - {e}")
        return None


# ─────────────────────────────────
# Bot Handlers
# ─────────────────────────────────
@app.on_message(filters.command("start"))
async def start_command(client, message):
    """Handle /start command"""
    await message.reply_text(
        "👋 **Welcome to YouTube Downloader Bot!**\n\n"
        "📝 **How to use:**\n"
        "• Send me a YouTube link\n"
        "• Choose Audio or Video format\n"
        "• Wait for your download!\n\n"
        "💡 You can also use `/get <youtube_link>` command\n\n"
        "Made with ❤️ using Pyrogram",
        disable_web_page_preview=True
    )


@app.on_message(filters.command("get"))
async def get_command(client, message):
    """Handle /get command with YouTube link"""
    if len(message.command) < 2:
        await message.reply_text(
            "❌ **Usage:** `/get <youtube_link>`\n\n"
            "**Example:**\n`/get https://youtu.be/dQw4w9WgXcQ`"
        )
        return
    
    link = message.command[1]
    
    # Validate YouTube link
    if not ("youtube.com" in link or "youtu.be" in link):
        await message.reply_text("❌ Please provide a valid YouTube link!")
        return
    
    # Store link and show format options
    user_states[message.from_user.id] = {"link": link}
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 Audio", callback_data="format_audio"),
            InlineKeyboardButton("🎥 Video", callback_data="format_video")
        ]
    ])
    
    await message.reply_text(
        f"🔗 **Link received!**\n\n"
        f"Choose download format:",
        reply_markup=keyboard
    )


@app.on_message(filters.text & filters.private & ~filters.command(["start", "get"]))
async def handle_link(client, message):
    """Handle YouTube links sent directly"""
    link = message.text.strip()
    
    # Validate YouTube link
    if not ("youtube.com" in link or "youtu.be" in link):
        await message.reply_text(
            "❌ Please send a valid YouTube link!\n\n"
            "**Example:**\n`https://youtu.be/dQw4w9WgXcQ`"
        )
        return
    
    # Store link and show format options
    user_states[message.from_user.id] = {"link": link}
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 Audio", callback_data="format_audio"),
            InlineKeyboardButton("🎥 Video", callback_data="format_video")
        ]
    ])
    
    await message.reply_text(
        f"🔗 **Link received!**\n\n"
        f"Choose download format:",
        reply_markup=keyboard
    )


@app.on_callback_query(filters.regex("^format_"))
async def handle_format_selection(client, callback_query):
    """Handle format selection"""
    user_id = callback_query.from_user.id
    format_type = callback_query.data.split("_")[1]  # audio or video
    
    # Check if user has a stored link
    if user_id not in user_states or "link" not in user_states[user_id]:
        await callback_query.answer("❌ Please send a YouTube link first!", show_alert=True)
        return
    
    link = user_states[user_id]["link"]
    
    await callback_query.answer()
    await callback_query.message.edit_text(
        f"⏳ **Downloading {format_type}...**\n\n"
        f"Please wait, this may take a moment..."
    )
    
    try:
        if format_type == "audio":
            file_path = await download_song(link)
            file_type = "audio"
            emoji = "🎵"
        else:
            file_path = await download_video(link)
            file_type = "video"
            emoji = "🎥"
        
        if not file_path or not os.path.exists(file_path):
            await callback_query.message.edit_text(
                f"❌ **Download failed!**\n\n"
                f"Please check:\n"
                f"• Your API key is valid\n"
                f"• The YouTube link is correct\n"
                f"• The video is available"
            )
            return
        
        # Update status
        await callback_query.message.edit_text(
            f"📤 **Uploading {file_type}...**\n\n"
            f"Please wait..."
        )
        
        # Send file
        if format_type == "audio":
            await callback_query.message.reply_audio(
                audio=file_path,
                caption=f"{emoji} **Downloaded Audio**\n\n🔗 [Source]({link})"
            )
        else:
            await callback_query.message.reply_video(
                video=file_path,
                caption=f"{emoji} **Downloaded Video**\n\n🔗 [Source]({link})"
            )
        
        # Delete status message
        await callback_query.message.delete()
        
        # Clean up user state
        if user_id in user_states:
            del user_states[user_id]
            
    except Exception as e:
        print(f"Error during upload: {e}")
        await callback_query.message.edit_text(
            f"❌ **Upload failed!**\n\n"
            f"Error: {str(e)}"
        )


# ─────────────────────────────────
# Run Bot
# ─────────────────────────────────
if __name__ == "__main__":
    print("🤖 Bot is starting...")
    print("📝 Make sure to configure:")
    print("   • API_ID and API_HASH from my.telegram.org")
    print("   • BOT_TOKEN from @BotFather")
    print("   • API_KEY from @InflexAPIBot")
    app.run()
