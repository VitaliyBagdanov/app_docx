import asyncpg
from .config import settings

class Database:
    def __init__(self):
        self._pool = None

    async def connect(self):
        if not self._pool:
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

    async def fetch_document(self, id_: str):
        await self.connect()
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT secretary, body FROM transcripts_mfg WHERE id = $1",
                id_
            )
            if row:
                return dict(row)
            return None

db = Database()
