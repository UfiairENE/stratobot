import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")
HF_API_KEY = os.getenv("HF_API_KEY")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
DEEPL_TRANSLATE_URL = os.getenv("DEEPL_TRANSLATE_URL")

