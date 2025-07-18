from ..db import db  # импортируйте существующий экземпляр/коннектор
import asyncpg

class DatabaseV2:
    def __init__(self):
        # можно использовать существующий pool из db, если он singleton
        self.db = db

    async def fetch_document_dynamic(self, id_: str, fields: list):
        await self.db.connect()
        field_list = ', '.join(fields)
        query = f"SELECT {field_list} FROM mfg_bot WHERE id = $1"
        async with self.db._pool.acquire() as conn:
            row = await conn.fetchrow(query, id_)
            if row:
                return dict(row)
            return None

db_v2 = DatabaseV2()