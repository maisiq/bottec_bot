from contextlib import asynccontextmanager
from os import getenv

from psycopg_pool import AsyncConnectionPool

from config import dp

POSTGRES_CONNINFO = getenv('POSTGRES_CONNINFO')


async def init_pool():
    pool = AsyncConnectionPool(
        conninfo=POSTGRES_CONNINFO,
        min_size=1,
        max_size=10,
        open=False,
        timeout=30.0,
        max_lifetime=3600.0,
        max_idle=600.0,
    )
    return pool


@asynccontextmanager
async def get_connection():
    pool: AsyncConnectionPool = dp['pool']
    async with pool.connection() as conn:
        yield conn
