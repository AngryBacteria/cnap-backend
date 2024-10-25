import logging
from logging.handlers import RotatingFileHandler

app_logger = logging.getLogger("app_logger")
app_logger.setLevel(logging.DEBUG)

app_logger.handlers = []

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# File handler with rotation
file_handler = RotatingFileHandler("app.log", maxBytes=50 * 1024 * 1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# Add handlers to logger
app_logger.addHandler(file_handler)
app_logger.addHandler(console_handler)
