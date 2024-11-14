import logging

app_logger = logging.getLogger("app_logger")
app_logger.setLevel(logging.DEBUG)

app_logger.handlers = []

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# Add handlers to logger
# app_logger.addHandler(file_handler) we do not need this in docker operation
app_logger.addHandler(console_handler)
