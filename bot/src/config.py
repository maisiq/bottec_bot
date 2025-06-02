from os import getenv

from aiogram import Bot, Dispatcher
from dependency_injector import containers, providers

from db.config import init_pool, get_repository

TOKEN = getenv('BOT_TOKEN')
PAYMASTER_TOKEN = getenv('PAYMASTER_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher()


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            'main',
            'tasks.promo',
            'products.router',
        ],
    )

    pool = providers.Resource(init_pool)

    repository = providers.Factory(
        get_repository,
        pool=pool,
    )
