from .models import MfgBot
from .db import async_session_maker
from sqlalchemy.future import select

class MfgBotDAO:
    @staticmethod
    async def get_by_id(id_: int):
        async with async_session_maker() as session:
            result = await session.execute(select(MfgBot).where(MfgBot.id == id_))
            return result.scalar_one_or_none()

    @staticmethod
    async def fetch_document_dynamic(id_: int, fields: list):
        async with async_session_maker() as session:
            # Получаем ссылки на нужные колонки модели
            cols = [getattr(MfgBot, field) for field in fields if hasattr(MfgBot, field)]
            if not cols:
                return None
            query = select(*cols).where(MfgBot.id == id_)
            result = await session.execute(query)
            row = result.first()
            if row:
                # row - tuple из значений в порядке cols
                return dict(zip(fields, row))
            return None
