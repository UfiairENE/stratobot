from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger

router = Router()  

@router.message(Command("start"))  
async def start_command(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[ 
        [
            InlineKeyboardButton(text="Deploy on AWS", callback_data="aws_deploy"),
            InlineKeyboardButton(text="Setup Kubernetes", callback_data="k8s_setup")
        ],
        [
            InlineKeyboardButton(text="CI/CD Pipelines", callback_data="cicd"),
            InlineKeyboardButton(text="Serverless Functions", callback_data="serverless")
        ]
    ])

    await message.answer("Hello! Select a cloud task:", reply_markup=keyboard)
    logger.info(f"User {message.from_user.id} started the bot.")
