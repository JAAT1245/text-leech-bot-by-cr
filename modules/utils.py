import time
import math
import os
from pyrogram.errors import FloodWait
from datetime import timedelta

# Timer class to control the rate of sending progress updates
class Timer:
    def __init__(self, time_between=5):
        self.start_time = time.time()
        self.time_between = time_between

    def can_send(self):
        """Return True if enough time has passed to send another progress update."""
        if time.time() > (self.start_time + self.time_between):
            self.start_time = time.time()
            return True
        return False

# Helper functions for converting file sizes and time durations to human-readable formats
def hrb(value, digits=2, delim="", postfix=""):
    """Return a human-readable file size."""
    if value is None:
        return None
    chosen_unit = "B"
    for unit in ("KiB", "MiB", "GiB", "TiB"):
        if value > 1000:
            value /= 1024
            chosen_unit = unit
        else:
            break
    return f"{value:.{digits}f}" + delim + chosen_unit + postfix

def hrt(seconds, precision=0):
    """Return a human-readable time delta as a string."""
    pieces = []
    value = timedelta(seconds=seconds)

    if value.days:
        pieces.append(f"{value.days}d")

    seconds = value.seconds
    if seconds >= 3600:
        hours = int(seconds / 3600)
        pieces.append(f"{hours}h")
        seconds -= hours * 3600

    if seconds >= 60:
        minutes = int(seconds / 60)
        pieces.append(f"{minutes}m")
        seconds -= minutes * 60

    if seconds > 0 or not pieces:
        pieces.append(f"{seconds}s")

    if not precision:
        return "".join(pieces)

    return "".join(pieces[:precision])

# Initialize Timer object
timer = Timer()

async def progress_bar(current, total, reply, start):
    """Display a progress bar with human-readable data transfer speeds and ETA."""
    if timer.can_send():
        now = time.time()
        diff = now - start

        # Only proceed if enough time has passed since the last update
        if diff < 1:
            return

        perc = f"{current * 100 / total:.1f}%"
        elapsed_time = round(diff)
        speed = current / elapsed_time
        remaining_bytes = total - current

        # Calculate ETA based on current speed
        if speed > 0:
            eta_seconds = remaining_bytes / speed
            eta = hrt(eta_seconds, precision=1)
        else:
            eta = "-"

        sp = str(hrb(speed)) + "/s"  # Speed in human-readable format
        tot = hrb(total)  # Total file size in human-readable format
        cur = hrb(current)  # Current progress in human-readable format

        bar_length = 11  # Length of the progress bar
        completed_length = int(current * bar_length / total)
        remaining_length = bar_length - completed_length
        progress_bar = "◆" * completed_length + "◇" * remaining_length

        try:
            # Update the progress message with detailed information
            await reply.edit(f"""
            `╭─⌯══⟰ 𝐔𝐩𝐥𝐨𝐝𝐢𝐧𝐠 ⟰══⌯──★ 
            ├⚡ {progress_bar}|﹝{perc}﹞ 
            ├🚀 Speed » {sp} 
            ├📟 Processed » {cur}
            ├🧲 Size - ETA » {tot} - {eta} 
            `├𝐁𝐲 » CR CHOUDHARY
            ╰─══ ✪ @TARGETALLCOURSE ✪ ══─★
            """)
        except FloodWait as e:
            # Handle FloodWait exception if Telegram API rate limits us
            time.sleep(e.x)
