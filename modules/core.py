import os
import time
import datetime
import aiohttp
import aiofiles
import asyncio
import logging
import subprocess
import concurrent.futures
import requests
import tgcrypto

from utils import progress_bar
from pyrogram import Client, filters
from pyrogram.types import Message

# Logger setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

# File duration using ffprobe
def duration(filename):
    try:
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return float(result.stdout)
    except Exception as e:
        logger.error(f"Error getting duration for {filename}: {e}")
        return 0.0

# Run a shell command
def exec(cmd):
    try:
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output = process.stdout.decode()
        if process.stderr:
            logger.error(f"Error running command: {process.stderr.decode()}")
        return output
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return None

# Run a list of commands concurrently
def pull_run(work, cmds):
    with concurrent.futures.ThreadPoolExecutor(max_workers=work) as executor:
        logger.info("Waiting for tasks to complete...")
        list(executor.map(exec, cmds))

# Async download function using aiohttp
async def download(url, name):
    try:
        k = f'{name}.pdf'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(k, mode='wb') as f:
                        await f.write(await resp.read())
        return k
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        return None

# Parse video information from a string
def parse_vid_info(info):
    info = info.strip().split("\n")
    new_info = []
    temp = []
    for line in info:
        line = line.strip()
        if "[" not in line and '---' not in line:
            line = " ".join(line.split())
            parts = line.split("|")[0].split(" ", 2)
            try:
                if "RESOLUTION" not in parts[2] and parts[2] not in temp and "audio" not in parts[2]:
                    temp.append(parts[2])
                    new_info.append((parts[0], parts[2]))
            except Exception as e:
                logger.error(f"Error parsing video info: {e}")
    return new_info

# Parse video info into a dictionary
def vid_info(info):
    info = info.strip().split("\n")
    new_info = {}
    temp = []
    for line in info:
        line = line.strip()
        if "[" not in line and '---' not in line:
            line = " ".join(line.split())
            parts = line.split("|")[0].split(" ", 3)
            try:
                if "RESOLUTION" not in parts[2] and parts[2] not in temp and "audio" not in parts[2]:
                    temp.append(parts[2])
                    new_info[parts[2]] = parts[0]
            except Exception as e:
                logger.error(f"Error parsing video info: {e}")
    return new_info

# Execute a command asynchronously
async def run(cmd):
    try:
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            logger.error(f"Command {cmd} failed with code {proc.returncode}.")
            return False

        if stdout:
            return stdout.decode()
        if stderr:
            logger.error(f"stderr: {stderr.decode()}")
            return stderr.decode()
    except Exception as e:
        logger.error(f"Error executing command {cmd}: {e}")
        return None

# Download function (alternative with requests)
def old_download(url, file_name, chunk_size=1024 * 10):
    if os.path.exists(file_name):
        os.remove(file_name)
    try:
        r = requests.get(url, allow_redirects=True, stream=True)
        with open(file_name, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    fd.write(chunk)
        return file_name
    except requests.exceptions.RequestException as e:
        logger.error(f"Download failed: {e}")
        return None

# Human-readable file size
def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

# Generate a file name based on current time
def time_name():
    now = datetime.datetime.now()
    return f"{now.strftime('%Y-%m-%d %H%M%S')}.mp4"

# Download video and handle retries
async def download_video(url, cmd, name):
    download_cmd = f'{cmd} -R 25 --fragment-retries 25 --external-downloader aria2c --downloader-args "aria2c: -x 16 -j 32"'
    logger.info(f"Running download command: {download_cmd}")
    try:
        result = subprocess.run(download_cmd, shell=True)
        if result.returncode != 0:
            logger.error(f"Download failed for {url} with error code {result.returncode}")
            return None
        return name
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running download video command: {e}")
        return None

# Send a document (PDF, etc.) using pyrogram
async def send_doc(bot: Client, m: Message, cc, ka, cc1, prog, count, name):
    try:
        reply = await m.reply_text(f"Uploading » `{name}`")
        start_time = time.time()
        await m.reply_document(ka, caption=cc1)
        count += 1
        await reply.delete(True)
        os.remove(ka)
    except Exception as e:
        logger.error(f"Error sending document: {e}")

# Send a video with thumbnail
async def send_vid(bot: Client, m: Message, cc, filename, thumb, name, prog):
    try:
        subprocess.run(f'ffmpeg -i "{filename}" -ss 00:01:00 -vframes 1 "{filename}.jpg"', shell=True)
        reply = await m.reply_text(f"**⥣ Uploading ...** » `{name}`")
        thumbnail = f"{filename}.jpg" if thumb == "no" else thumb
        dur = int(duration(filename))

        await m.reply_video(filename, caption=cc, supports_streaming=True, height=720, width=1280, thumb=thumbnail, duration=dur, progress=progress_bar, progress_args=(reply, start_time))
        os.remove(filename)
        os.remove(f"{filename}.jpg")
        await reply.delete(True)
    except Exception as e:
        logger.error(f"Error sending video: {e}")
        await m.reply_document(filename, caption=cc, progress=progress_bar, progress_args=(reply, start_time))
