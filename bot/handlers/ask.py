import asyncio
from aiogram import Router, types, F
from aiogram.utils.text_decorations import markdown_decoration
from loguru import logger
from bot.utils.inference import get_cloud_solution  

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

async def send_typing(message: types.Message):
    """Send typing action to show that the bot is processing."""
    await message.answer_chat_action("typing")

@router.callback_query(F.data.in_(CLOUD_TASKS.keys()))
async def cloud_task_handler(callback_query: types.CallbackQuery):
    """Handles cloud-related inline queries."""
    task = callback_query.data
    query = CLOUD_TASKS[task]

    await callback_query.answer()  
    await send_typing(callback_query.message)

    try:
        response = await get_cloud_solution(query)
        await send_chunked_response(callback_query.message, response)
        logger.info(f"User {callback_query.from_user.id} received response for {task}")
    except Exception as e:
        logger.error(f"Error processing cloud task: {e}")
        await callback_query.message.answer("Sorry, an error occurred while processing your request.")

@router.message()
async def handle_text_query(message: types.Message):
    """Handles direct user messages, maintains context, and detects topic shifts."""
    user_id = message.from_user.id
    user_text = message.text.strip().lower() if message.text else ""
    logger.info(f"User {user_id} sent: {user_text}")

    # Handle greetings with a simple response
    if user_text in GREETINGS:
        await message.answer("👋 Hey! How's it going?")
        return

    # Maintain context (store last 5 messages)
    user_context.setdefault(user_id, []).append(user_text)
    if len(user_context[user_id]) > 5:
        user_context[user_id].pop(0)  # Remove oldest messages

    # Detect topic change
    if len(user_context[user_id]) > 1 and user_text not in user_context[user_id][-2]:
        user_context[user_id] = [user_text]  # Reset if a new topic starts

    await send_typing(message)

    try:
        context = " ".join(user_context[user_id])
        response = await get_cloud_solution(context)
        await send_chunked_response(message, response)
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
            await message.answer(markdown_decoration(chunk.strip()), parse_mode="MarkdownV2")
        except Exception as e:
            logger.warning(f"Markdown parsing failed, sending as plain text: {e}")
            await message.answer(chunk.strip())

        await asyncio.sleep(0.1)
