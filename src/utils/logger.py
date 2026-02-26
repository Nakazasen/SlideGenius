"""Logging configuration and utilities."""
import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Optional

# Constants
LOG_DIR = Path("logs")
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logging(app_name: str = "SlideGenius", debug: bool = False) -> None:
    """Setup logging configuration.
    
    Args:
        app_name: Name of the application logger
        debug: If True, set level to DEBUG
    """
    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Root logger config
    level = logging.DEBUG if debug else logging.INFO
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Formatter
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # 1. File Handler (Rotating daily, keep 5 days)
    log_file = LOG_DIR / f"{app_name.lower()}.log"
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    root_logger.addHandler(file_handler)
    
    # 2. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Silence some noisy libraries
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logging.info(f"Logging initialized. Logs stored in {LOG_DIR.absolute()}")

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with valid name."""
    return logging.getLogger(name)
