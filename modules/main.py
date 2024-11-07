import os
import sys
import asyncio
import time
import re
from aiohttp import web, ClientSession
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from subprocess import getstatusoutput

from vars import API_ID, API_HASH, BOT_TOKEN, WEBHOOK, PORT
from style import Ashu 

# Initialize the bot with increased sqlite_timeout
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    sqlite_timeout=30.0  # Increased timeout
)

# Define aiohttp routes
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("https://github.com/AshutoshGoswami24")

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

async def start_bot():
    attempt = 0
    while attempt < 3:
        try:
            await bot.start()
            break
        except Exception as e:
            attempt += 1
            print(f"Attempt {attempt} failed: {e}")
            if attempt < 3:
                print("Retrying...")
                await asyncio.sleep(5)  # Wait for a few seconds before retrying
            else:
                print("Failed to start bot after 3 attempts")
                break

async def start_web():
    app = await web_server()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

# Bot handlers
@bot.on_message(filters.command(["start"]))
async def account_login(bot: Client, m: Message):
    await m.reply_text(
       Ashu.START_TEXT, reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("✜ TERA BAAP CR CHOUDHARY ✜", url="https://t.me/Targetallcourse")],
                [InlineKeyboardButton("🦋 Follow Me 🦋", url="https://t.me/targetallcourse")]
            ]
        )
    )

@bot.on_message(filters.command("stop"))
async def restart_handler(_, m):
    await m.reply_text("♦ Stopped ♦", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

# Refactored file upload handler
@bot.on_message(filters.command(["upload"]))
async def upload_file_handler(bot: Client, m: Message):
    editable = await m.reply_text('Send me a .txt file')
    input_msg: Message = await bot.listen(editable.chat.id)

    try:
        # Download the file
        file_path = await input_msg.download()
        print(f"File downloaded at: {file_path}")
        await input_msg.delete(True)
    except Exception as e:
        await m.reply_text(f"Failed to download file: {e}")
        return

    # Read and process the file
    try:
        with open(file_path, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = [i.split("://", 1) for i in content]
        os.remove(file_path)  # Clean up the file after reading
    except Exception as e:
        await m.reply_text(f"Error reading the file: {e}")
        os.remove(file_path)  # Remove the invalid file
        return

    await editable.edit(f"Links found: {len(links)}")

    # Collect additional input (batch name, resolution, etc.)
    batch_name = await ask_for_input(bot, editable.chat.id, "Now send me your batch name")
    resolution = await ask_for_input(bot, editable.chat.id, "Please send me the video resolution")
    video_format = await ask_for_input(bot, editable.chat.id, "Send me the video format details")

    # Define video resolution mapping
    resolution_map = {
        "144": "256x144",
        "240": "426x240",
        "360": "640x360",
        "480": "854x480",
        "720": "1280x720",
        "1080": "1920x1080"
    }
    res = resolution_map.get(resolution, "UN")

    # Process video links
    count = 1 if len(links) == 1 else int(batch_name)

    for i in range(count - 1, len(links)):
        # Prepare the video URL
        video_url = prepare_video_url(links[i][1])

        try:
            await process_video_link(video_url, i, links, m, bot, res, video_format)
            await asyncio.sleep(1)  # Use async sleep to avoid blocking the event loop
        except FloodWait as e:
            await m.reply_text(f"Please wait for {e.x} seconds.")
            await asyncio.sleep(e.x)  # Await async sleep
        except Exception as e:
            await m.reply_text(f"Error processing link {i + 1}: {str(e)}")

    await m.reply_text("Successfully completed!")


# Helper function to ask for user input
async def ask_for_input(bot: Client, chat_id: int, prompt: str) -> str:
    """Send a prompt and wait for user response."""
    await bot.send_message(chat_id, prompt)
    input_msg = await bot.listen(chat_id)
    user_input = input_msg.text
    await input_msg.delete(True)
    return user_input


# Helper function to prepare video URL
def prepare_video_url(url: str) -> str:
    """Prepare the video URL by cleaning it."""
    url = url.replace("file/d/", "uc?export=download&id=") \
             .replace("www.youtube-nocookie.com/embed", "youtu.be") \
             .replace("?modestbranding=1", "") \
             .replace("/view?usp=sharing", "")
    return "https://" + url


# Process the video link and download it
async def process_video_link(url: str, count: int, links: list, m: Message, bot: Client, res: str, video_format: str):
    """Process each video link by downloading and sending the video."""
    name1 = clean_video_name(links[count][0])
    name = f'{str(count + 1).zfill(3)}) {name1[:60]}'

    try:
        show_msg = f"Downloading video: {name}"
        prog = await m.reply_text(show_msg)

        # Assuming helper methods exist
        res_file = await helper.download_video(url, name, res, video_format)
        filename = res_file
        await helper.send_vid(bot, m, filename)
    except Exception as e:
        await m.reply_text(f"Error processing video {name}: {str(e)}")
        print(f"Error in video download and send: {e}")


# Clean the video name
def clean_video_name(name: str) -> str:
    """Clean the video name by removing unwanted characters."""
    name = name.replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").strip()
    return name


# Start the bot and web server concurrently
async def main():
    if WEBHOOK:
        # Start the web server
        app = await web_server()
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        print(f"Web server started on port {PORT}")

if __name__ == "__main__":
    print("""
    █░█░█ █▀█ █▀█ █▀▄ █▀▀ █▀█ ▄▀█ █▀▀ ▀█▀
    ▀▄▀▄▀ █▄█ █▄█ █▄▀ █▄▄ █▀▄ █▀█ █▀░ ░█░
    """)

    # Start the bot and web server concurrently
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(start_bot())
        loop.create_task(start_web())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.stop()
