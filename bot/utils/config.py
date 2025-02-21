import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")
HF_API_KEY = os.getenv("HF_API_KEY")

