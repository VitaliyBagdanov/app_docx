import asyncpg
from ..config import settings
from .logger import logger

class DatabaseV2:
    def __init__(self):
        self._pool = None

    async def connect(self):
        if not self._pool:
            logger.info("Creating asyncpg connection pool")
            self._pool = await asyncpg.create_pool(
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
                host=settings.POSTGRES_HOST,
                port=int(settings.POSTGRES_PORT),
                min_size=1, max_size=5
            )

    async def disconnect(self):
        if self._pool:
            await self._pool.close()

    async def fetch_document_dynamic(self, id_: str, fields: list):
        await self.connect()
        field_list = ', '.join(fields)
        query = f"SELECT {field_list} FROM mfg_bot WHERE id = $1"
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, id_)
            if row:
                return dict(row)
            return None

db_v2 = DatabaseV2()
