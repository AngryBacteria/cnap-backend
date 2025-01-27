import logging

import colorlog

app_logger = logging.getLogger("app_logger")
app_logger.setLevel(logging.DEBUG)

app_logger.handlers = []

# Create formatter
color_formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s[%(levelname)s] - %(message)s%(reset)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(color_formatter)

# Add handlers to logger
app_logger.addHandler(console_handler)
