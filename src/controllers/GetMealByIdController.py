from datetime import date, time, datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, ValidationError
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..app_types.http import ProtectedHttpRequest
from ..utils.http import bad_request, ok
from ..db.connection import get_db
from ..db.models.meals import Meal


class ParamsEventSchema(BaseModel):
    meal_id: uuid.UUID

class GetMealByIdController:

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session or get_db

    def _validate_params(self, params: Dict[str, Any]):
        return ParamsEventSchema(**params)
    
    async def handle(self, request: ProtectedHttpRequest):
        try:
            data = self._validate_params(request.get("params"))
        except ValidationError as ex:
            return bad_request(body={"errors": ex.errors()})
        
        async with self.session() as session:
            query = select(Meal).where(
                Meal.id == str(data.meal_id),
                Meal.user_id == int(request.get("user_id"))
            )
            result = await session.execute(query)
            meal = result.scalars().first()
            
            return ok(body={"meal": meal.to_dict})