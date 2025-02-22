from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger

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

    await message.answer("👋 Welcome! Choose a cloud task:", reply_markup=keyboard)
    logger.info(f"User {message.from_user.id} started the bot.")

@router.callback_query(lambda c: c.data == "more_options")
async def more_options(callback_query: types.CallbackQuery):
    """Handles 'More Options' button, providing additional choices."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="CI/CD Pipelines", callback_data="cicd"),
                InlineKeyboardButton(text="Serverless Functions", callback_data="serverless"),
            ]
        ]
    )

    await callback_query.message.edit_text("Select an additional cloud task:", reply_markup=keyboard)
    await callback_query.answer()
