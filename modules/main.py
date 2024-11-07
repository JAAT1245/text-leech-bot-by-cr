import os
import sys
import asyncio
import time
from aiohttp import web, ClientSession
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from subprocess import getstatusoutput

from vars import API_ID, API_HASH, BOT_TOKEN, WEBHOOK, PORT
from style import Ashu
import helper  # Assuming `helper` handles various utility functions

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
                time.sleep(5)  # Wait for a few seconds before retrying
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

# Adjusted file upload handler
@bot.on_message(filters.command(["upload"]))
async def account_login(bot: Client, m: Message):
    editable = await m.reply_text('Send me a .txt file')
    input_msg: Message = await bot.listen(editable.chat.id)
    x = await input_msg.download()
    await input_msg.delete(True)

    path = f"./downloads/{m.chat.id}"

    try:
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = [i.split("://", 1) for i in content]
        os.remove(x)
    except Exception:
        await m.reply_text("Invalid file input.")
        os.remove(x)
        return
    
    await editable.edit(f"Links found: {len(links)}")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)

    await editable.edit("Now send me your batch name")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)

    await editable.edit("Please send me the video resolution")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)

    # Define video resolution based on input
    res = "UN"
    resolution_map = {
        "144": "256x144",
        "240": "426x240",
        "360": "640x360",
        "480": "854x480",
        "720": "1280x720",
        "1080": "1920x1080"
    }
    res = resolution_map.get(raw_text2, "UN")

    await editable.edit("Send me the video format details")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)

    highlighter = f"️ ⁪⁬⁮⁮"
    MR = highlighter if raw_text3 == 'Robin' else raw_text3

    # Now processing the links
    count = 1 if len(links) == 1 else int(raw_text)

    for i in range(count - 1, len(links)):
        V = links[i][1].replace("file/d/", "uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing", "")
        url = "https://" + V

        # Download logic based on URL type
        if "visionias" in url:
            async with ClientSession() as session:
                async with session.get(url) as resp:
                    text = await resp.text()
                    url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

        # Further URL parsing logic...

        name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").strip()
        name = f'{str(count).zfill(3)}) {name1[:60]}'

        # Download and send video
        try:
            show_msg = f"Downloading video: {name}"
            prog = await m.reply_text(show_msg)

            res_file = await helper.download_video(url, name)
            filename = res_file
            await helper.send_vid(bot, m, filename)
            count += 1
            time.sleep(1)
        except FloodWait as e:
            await m.reply_text(str(e))
            time.sleep(e.x)
            continue
        except Exception as e:
            await m.reply_text(f"Error: {str(e)}")
            continue

    await m.reply_text("Successfully completed!")

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
