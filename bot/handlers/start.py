from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger
from bot.handlers.ask import CLOUD_TASKS
from bot.utils.inference import get_cloud_solution

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    """Sends a welcome message with a simplified inline keyboard."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="AWS Deploy", callback_data="aws_deploy"),
                InlineKeyboardButton(text="Kubernetes Setup", callback_data="k8s_setup"),
            ],
            [
                InlineKeyboardButton(text="More Options", callback_data="more_options")
            ]
        ]
    )
    await message.answer("Welcome! Choose a cloud task:", reply_markup=keyboard)
    logger.info(f"User {message.from_user.id} started the bot.")

async def send_long_message(message: types.Message, text: str):
    """Splits long messages into multiple parts and sends them."""
    chunk_size = 4000  
    for i in range(0, len(text), chunk_size):
        await message.answer(f"```\n{text[i:i+chunk_size]}\n```", parse_mode="Markdown")

@router.callback_query(F.data.in_(CLOUD_TASKS.keys()))
async def handle_cloud_task(callback_query: types.CallbackQuery):
    """Handles inline button clicks and sends AI-generated responses."""
    user_query = CLOUD_TASKS[callback_query.data]  
    logger.info(f"User selected: {user_query}")

    await callback_query.answer("Generating response...")  

    ai_response = await get_cloud_solution(user_query)

    await send_long_message(callback_query.message, ai_response)
