from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.users import User
from ..app_types.http import ProtectedHttpRequest
from ..db.connection import get_db
from ..utils.http import ok

class MeController:

    def __init__(self, session: Optional[AsyncSession]):
        self.session = session or get_db

    async def handle(self, data: ProtectedHttpRequest):
        user_id = int(data.get("user_id"))
        async with self.session() as session:
            query = select(User).where(User.id == user_id)
            result = await session.execute(query)
            user = result.scalars().first()

            return ok(body={"user": user.to_dict()})