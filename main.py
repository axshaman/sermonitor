import os, sys
from aiogram import executor
from bot_telegram.config import *
from bot_telegram.loader import bot

async def on_shutdown(dp):
    await bot.close()


if __name__ == '__main__':
    from bot_telegram.handlers import dp
    executor.start_polling(dp, skip_updates=False)