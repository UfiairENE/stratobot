from loguru import logger

logger.add("logs/bot.log", rotation="1 MB", level="INFO", format="{time} - {level} - {message}")
