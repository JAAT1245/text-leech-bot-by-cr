import os

API_ID    = os.environ.get("API_ID", "24894984")
API_HASH  = os.environ.get("API_HASH", "4956e23833905463efb588eb806f9804")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "") 

WEBHOOK = True  # Don't change this
PORT = int(os.environ.get("PORT", 8080))  # Default to 8000 if not set
