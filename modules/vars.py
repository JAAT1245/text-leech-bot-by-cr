import os

# Read sensitive information from environment variables
API_ID = os.environ.get("API_ID","24894984")
API_HASH = os.environ.get("API_HASH","4956e23833905463efb588eb806f9804")
BOT_TOKEN = os.environ.get("BOT_TOKEN","")

# Validate that all critical variables are set
if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("Missing one or more environment variables: API_ID, API_HASH, or BOT_TOKEN")

# Set webhook settings and port
WEBHOOK = True  # Don't change this
PORT = int(os.environ.get("PORT", 8080))  # Default to 8080 if not set

# For debugging purposes, print out your config (excluding sensitive information)
print("API_ID and API_HASH loaded successfully.")
print(f"Webhook: {WEBHOOK}, Port: {PORT}")
