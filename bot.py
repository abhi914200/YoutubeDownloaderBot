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
async def download_song(video_id: str) -> str:
    """Download YouTube audio"""
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


async def download_video(video_id: str) -> str:
    """Download YouTube video"""
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


def extract_video_id(text: str) -> str:
    """Extract video ID from text (supports video ID or full YouTube URL)"""
    text = text.strip()
    
    # If it's a full URL, extract the video ID
    if "youtube.com" in text or "youtu.be" in text:
        if "youtu.be/" in text:
            video_id = text.split("youtu.be/")[-1].split("?")[0].split("&")[0]
        elif "v=" in text:
            video_id = text.split("v=")[-1].split("&")[0]
        else:
            return text
        return video_id
    
    # Otherwise, assume it's already a video ID
    return text


# ─────────────────────────────────
# Bot Handlers
# ─────────────────────────────────
@app.on_message(filters.command("start"))
async def start_command(client, message):
    """Handle /start command"""
    await message.reply_text(
        "👋 **Welcome to YouTube Downloader Bot!**\n\n"
        "📝 **How to use:**\n"
        "• Use `/get <video_id>` command\n"
        "• Choose Audio or Video format\n"
        "• Wait for your download!\n\n"
        "💡 **Example:**\n"
        "`/get dQw4w9WgXcQ`\n\n"
        "Made with ❤️ using Pyrogram",
        disable_web_page_preview=True
    )


@app.on_message(filters.command("get"))
async def get_command(client, message):
    """Handle /get command with YouTube video ID"""
    if len(message.command) < 2:
        await message.reply_text(
            "❌ **Usage:** `/get <video_id>`\n\n"
            "**Example:**\n`/get dQw4w9WgXcQ`\n\n"
            "💡 **Tip:** Send only the video ID, not the full link!"
        )
        return
    
    video_id = message.command[1]
    
    # Extract video ID if user accidentally sent a full URL
    video_id = extract_video_id(video_id)
    
    # Validate video ID (YouTube IDs are typically 11 characters)
    if len(video_id) < 5 or len(video_id) > 20:
        await message.reply_text(
            "❌ **Invalid video ID!**\n\n"
            "Please provide a valid YouTube video ID.\n\n"
            "**Example:**\n`/get dQw4w9WgXcQ`"
        )
        return
    
    # Store video ID and show format options
    user_states[message.from_user.id] = {"video_id": video_id}
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 Audio", callback_data="format_audio"),
            InlineKeyboardButton("🎥 Video", callback_data="format_video")
        ]
    ])
    
    await message.reply_text(
        f"✅ **Video ID received:** `{video_id}`\n\n"
        f"Choose download format:",
        reply_markup=keyboard
    )


@app.on_callback_query(filters.regex("^format_"))
async def handle_format_selection(client, callback_query):
    """Handle format selection"""
    user_id = callback_query.from_user.id
    format_type = callback_query.data.split("_")[1]  # audio or video
    
    # Check if user has a stored video ID
    if user_id not in user_states or "video_id" not in user_states[user_id]:
        await callback_query.answer("❌ Please use /get command first!", show_alert=True)
        return
    
    video_id = user_states[user_id]["video_id"]
    
    await callback_query.answer()
    await callback_query.message.edit_text(
        f"⏳ **Downloading {format_type}...**\n\n"
        f"Video ID: `{video_id}`\n"
        f"Please wait, this may take a moment..."
    )
    
    try:
        if format_type == "audio":
            file_path = await download_song(video_id)
            file_type = "audio"
            emoji = "🎵"
        else:
            file_path = await download_video(video_id)
            file_type = "video"
            emoji = "🎥"
        
        if not file_path or not os.path.exists(file_path):
            await callback_query.message.edit_text(
                f"❌ **Download failed!**\n\n"
                f"Video ID: `{video_id}`\n\n"
                f"Please check:\n"
                f"• Your API key is valid\n"
                f"• The video ID is correct\n"
                f"• The video is available\n\n"
                f"Try again with `/get {video_id}`"
            )
            return
        
        # Update status
        await callback_query.message.edit_text(
            f"📤 **Uploading {file_type}...**\n\n"
            f"Video ID: `{video_id}`\n"
            f"Please wait..."
        )
        
        # Construct YouTube link for caption
        youtube_link = f"https://www.youtube.com/watch?v={video_id}"
        
        # Send file
        if format_type == "audio":
            await callback_query.message.reply_audio(
                audio=file_path,
                caption=f"{emoji} **Downloaded Audio**\n\n"
                        f"📹 Video ID: `{video_id}`\n"
                        f"🔗 [Watch on YouTube]({youtube_link})"
            )
        else:
            await callback_query.message.reply_video(
                video=file_path,
                caption=f"{emoji} **Downloaded Video**\n\n"
                        f"📹 Video ID: `{video_id}`\n"
                        f"🔗 [Watch on YouTube]({youtube_link})"
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
            f"Video ID: `{video_id}`\n"
            f"Error: `{str(e)}`\n\n"
            f"Try again with `/get {video_id}`"
        )


# ─────────────────────────────────
# Run Bot
# ─────────────────────────────────
if __name__ == "__main__":
    print("🤖 Bot is starting...")
    print("=" * 50)
    print("📝 Configuration:")
    print(f"   • API_ID: {API_ID}")
    print(f"   • BOT_TOKEN: {BOT_TOKEN[:20]}...")
    print(f"   • API_KEY: {API_KEY}")
    print("=" * 50)
    print("✅ Bot is ready!")
    print("💡 Usage: /get <video_id>")
    print("=" * 50)
    app.run()
