from os import getenv

from aiogram import Bot, Dispatcher

TOKEN = getenv('BOT_TOKEN')
PAYMASTER_TOKEN = getenv('PAYMASTER_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher()
