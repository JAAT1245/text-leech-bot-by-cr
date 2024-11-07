import logging
from logging.handlers import RotatingFileHandler

# Create a custom logger
logger = logging.getLogger("my_logger")

# Set the logging level to ERROR by default
logger.setLevel(logging.ERROR)

# Define the log format
log_format = "%(asctime)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]"
date_format = "%d-%b-%y %H:%M:%S"

# Set up handlers for rotating file and stream (console) output
file_handler = RotatingFileHandler("logs.txt", maxBytes=50000000, backupCount=10)
file_handler.setLevel(logging.ERROR)  # Log errors and above to the file
file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)  # Log warnings and above to the console
console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Optionally adjust logging level for third-party libraries like pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# Now you can use 'logger' to log messages
logger.info("Logger initialized successfully.")
logger.error("This is an error message.")
