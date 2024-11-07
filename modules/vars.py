import os
from dotenv import load_dotenv

# Load environment variables from a .env file (if present)
load_dotenv()

# Read sensitive information from environment variables
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Validate that all critical variables are set
if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("Missing one or more environment variables: API_ID, API_HASH, or BOT_TOKEN")

# Set webhook settings and port
WEBHOOK = True  # Don't change this
PORT = int(os.environ.get("PORT", 8080))  # Default to 8080 if not set

# For debugging purposes, print out your config (excluding sensitive information)
print("API_ID and API_HASH loaded successfully.")
print(f"Webhook: {WEBHOOK}, Port: {PORT}")
