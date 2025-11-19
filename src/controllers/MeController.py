from sqlalchemy import select

from ..db.models.users import User
from ..app_types.http import ProtectedHttpRequest
from ..db.connection import get_db
from ..utils.http import ok

class MeController:
    
    @staticmethod
    async def handle(data: ProtectedHttpRequest):
        user_id = int(data.get("user_id"))
        async with get_db() as session:
            query = select(User).where(User.id == user_id)
            result = await session.execute(query)
            user = result.scalars().first()

            return ok(body={"user": user.to_dict()})