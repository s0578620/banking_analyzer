# scraper/logger.py
import logging
import os

def setup_logger(name):
    formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO) #logging.DEBUG

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logs_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(logs_dir, exist_ok=True)

    file_path = os.path.join(logs_dir, "bankdaten_scraper.log")
    file_handler = logging.FileHandler(file_path, encoding="utf-8")
    #file_handler = logging.FileHandler(file_path, mode='w', encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
