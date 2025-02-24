import asyncio
from aiogram import Router, types, F
from aiogram.utils.text_decorations import markdown_decoration
from loguru import logger
from bot.utils.config import DEEPL_API_KEY, DEEPL_TRANSLATE_URL
from bot.utils.inference import get_cloud_solution
from langdetect import detect, DetectorFactory
import httpx  # For translation API requests

router = Router()

# Store conversation context per user
user_context = {}

# Greeting keywords
GREETINGS = {'hello', 'hi', 'hey', 'greetings', 'hola', 'sup', 'yo'}

# Cloud-related inline queries
CLOUD_TASKS = {
    "aws_deploy": "How to deploy on AWS?",
    "k8s_setup": "How to set up a Kubernetes cluster?",
    "cicd": "How to configure a CI/CD pipeline?",
    "serverless": "How to deploy a serverless function?"
}

# Ensure consistent results
DetectorFactory.seed = 0



async def send_typing(message: types.Message):
    """Send typing action to show that the bot is processing."""
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

async def detect_user_language(text):
    try:
        detected_lang = await asyncio.to_thread(detect, text)
        logger.info(f"Detected language: {detected_lang}")
        return detected_lang
    except Exception as e:
        logger.error(f"Language detection error: {e} - Defaulting to English.")
        return "en"  # Default to English if detection fails

async def translate_text(text, target_lang="en"):
    """Translate text using DeepL API."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                DEEPL_TRANSLATE_URL,
                data={"auth_key": DEEPL_API_KEY, "text": text, "target_lang": target_lang},
            )
            response_json = response.json()
            translated_text = response_json["translations"][0]["text"]
            return translated_text
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text  
        
@router.message()
async def handle_text_query(message: types.Message):
    """Handles user queries: detects language, translates to English, processes, and translates back."""
    user_id = message.from_user.id
    user_text = message.text.strip() if message.text else ""
    logger.info(f"User {user_id} sent: {user_text}")

    # Handle greetings first
    if user_text.lower() in GREETINGS:
        await message.answer("👋 Hey! How's it going?")
        return

    await send_typing(message)

    # Detect user language
    detected_lang = await detect_user_language(user_text)

    # Translate user query to English
    if detected_lang != "en":
        translated_query = await translate_text(user_text, "EN")
        logger.info(f"Translated query from {detected_lang} to English: {translated_query}")
    else:
        translated_query = user_text

    # Maintain conversation context (store last 5 messages)
    user_context.setdefault(user_id, []).append(translated_query)
    if len(user_context[user_id]) > 5:
        user_context[user_id].pop(0)  # Keep last 5 messages

    # Detect topic shift
    if len(user_context[user_id]) > 1 and translated_query not in user_context[user_id][-2]:
        user_context[user_id] = [translated_query]  # Reset if new topic

    try:
        context = " ".join(user_context[user_id])
        response = await get_cloud_solution(context)  # Process query in English

        # Translate response back to user's original language
        if detected_lang != "en":
            final_response = await translate_text(response, detected_lang.upper())
            logger.info(f"Translated response back to {detected_lang}: {final_response}")
        else:
            final_response = response

        await send_chunked_response(message, final_response)
    except Exception as e:
        logger.error(f"Error handling user query: {e}")
        await message.answer("An error occurred while processing your request.")

async def send_chunked_response(message: types.Message, response: str, chunk_size=4000):
    """Splits long responses into chunks and sends them sequentially."""
    chunks = []
    current_chunk = ""
    lines = response.split("\n")
    
    for line in lines:
        if len(current_chunk) + len(line) + 1 <= chunk_size:
            current_chunk += line + "\n"
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = line + "\n"
    
    if current_chunk:
        chunks.append(current_chunk)

    for chunk in chunks:
        try:
            escaped_chunk = markdown_decoration.escape(chunk.strip())
            await message.answer(escaped_chunk, parse_mode="MarkdownV2")
        except Exception as e:
            logger.warning(f"Markdown parsing failed, sending as plain text: {e}")
            await message.answer(chunk.strip())
        await asyncio.sleep(0.1)
