import asyncio
import logging
import sys
from typing import AsyncContextManager

from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dependency_injector.wiring import Provide, inject

from cart.router import router as cart_router
from config import bot, dp, Container
from db.repository import Repository
from faq.router import router as faq_router
from logs.config import setup_logger
from products.router import router as product_router
from tasks.promo import promote

SUBSCRIBE_TO = []


async def check_subscription(channel_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False


@dp.message(CommandStart())
@inject
async def command_start_handler(
    message: Message,
    repository: AsyncContextManager[Repository] = Provide[Container.repository],
) -> None:
    if not all([check_subscription(ch, message.from_user.id) for ch in SUBSCRIBE_TO]):
        message.answer('Отсутствуют подписки на необходимые каналы')
        return

    async with repository as repo:
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

    container = Container()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(promote, 'interval', minutes=1,)
    scheduler.start()

    dp.include_router(product_router)
    dp.include_router(cart_router)
    dp.include_router(faq_router)

    await dp.start_polling(bot)
    await container.shutdown_resources()


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
