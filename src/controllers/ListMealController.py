from datetime import date, time, datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, ValidationError

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..app_types.http import ProtectedHttpRequest, HTTPResponse
from ..utils.http import bad_request, ok
from ..db.connection import get_db
from ..db.models.meals import Meal, MealStatus

class QueryEventSchema(BaseModel):
    date: date

class ListMealController:

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session or get_db

    def _validate_query_params(self, query_params: Dict[str, Any]) -> QueryEventSchema:
        return QueryEventSchema(**query_params)
    
    async def handle(self, request: ProtectedHttpRequest) -> HTTPResponse:
        try:
            data = self._validate_query_params(query_params=request.get("query_params"))
        except ValidationError as ex:
            return bad_request(body={"errors": ex.errors()})
        
        end_date = datetime.combine(data.date, time(23, 59, 59, 59))
        async with self.session() as session:
            query = select(Meal).where(
                Meal.user_id == int(request.get("user_id")),
                Meal.status == MealStatus.success,
                Meal.created_at >= data.date,
                Meal.created_at <= end_date,
            )
            result = await session.execute(query)
            meals = result.scalars().all()

            return ok(body={"meals": [meal.to_dict for meal in meals]})