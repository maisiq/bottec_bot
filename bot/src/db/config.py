from contextlib import asynccontextmanager
from os import getenv

from psycopg import AsyncConnection

POSTGRES_CONNINFO = getenv('POSTGRES_CONNINFO')


@asynccontextmanager
async def get_connection():
    async with await AsyncConnection.connect(POSTGRES_CONNINFO) as conn:
        yield conn
