import asyncio
import logging
import sys

from aiogram import Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from cart.router import router as cart_router
from config import bot
from db.config import get_connection
from db.repository import RawSQLRepository
from faq.router import router as faq_router
from logs.config import setup_logger
from products.router import router as product_router
from tasks.promo import promote

SUBSCRIBE_TO = []

dp = Dispatcher()


async def check_subscription(channel_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if not all([check_subscription(ch, message.from_user.id) for ch in SUBSCRIBE_TO]):
        message.answer('Отсутствуют подписки на необходимые каналы')
        return

    async with get_connection() as conn:
        repo = RawSQLRepository(conn)
        if await repo.add_user(message.from_user):
            logging.info('Новый пользователь @%s(%s)', message.from_user.username, message.from_user.id)

    kb = [
        [KeyboardButton(text="Каталог")],
        [KeyboardButton(text="Корзина"), KeyboardButton(text="FAQ")]
    ]

    await message.answer(
        "Привет! Нашу продукцию можно посмотреть, нажав по кнопке Каталог",
        reply_markup=ReplyKeyboardBuilder(kb).as_markup(
            resize_keyboard=True,
            input_field_placeholder="Выберите один из пунктов меню",
        )
    )


async def main() -> None:
    setup_logger()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(promote, 'interval', minutes=1,)
    scheduler.start()

    dp.include_router(product_router)
    dp.include_router(cart_router)
    dp.include_router(faq_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
