from datetime import date, time, datetime, timezone
from zoneinfo import ZoneInfo
from typing import Dict, Any
from pydantic import BaseModel, ValidationError

from ..app_types.http import ProtectedHttpRequest, HTTPResponse
from ..utils.http import bad_request, ok
from ..repository.meal_repository import MealRepository

class QueryEventSchema(BaseModel):
    date: date
    timeZone: str

class ListMealController:

    def __init__(self, meal_repository: MealRepository):
        self.meal_repository = meal_repository

    def _validate_query_params(self, query_params: Dict[str, Any]) -> QueryEventSchema:
        return QueryEventSchema(**query_params)
    
    async def handle(self, request: ProtectedHttpRequest) -> HTTPResponse:
        try:
            query_event = self._validate_query_params(query_params=request.get("query_params"))
        except ValidationError as ex:
            return bad_request(body={"errors": ex.errors()})
        
        user_timezone = ZoneInfo(query_event.timeZone)
        start_date = datetime.combine(
            query_event.date,
            time.min,
            user_timezone
        )
        end_date = datetime.combine(
            query_event.date,
            time.max,
            user_timezone,
        )
        meals = await self.meal_repository.list_meals_by_date(
            user_id=request["user_id"],
            start_date=start_date.astimezone(timezone.utc),
            end_date=end_date.astimezone(timezone.utc),
        )
        return ok(body={"meals": [meal.to_dict for meal in meals]})