import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.handlers.start import router as start_router
from bot.handlers.ask import router as ask_router
from bot.utils.config import BOT_TOKEN

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(ask_router)  

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
