from typing import Dict, Any
from pydantic import BaseModel, ValidationError
import uuid

from ..app_types.http import ProtectedHttpRequest
from ..utils.http import bad_request, ok
from ..repository.meal_repository import MealRepository

from ..exceptions.MealNotFound import MealNotFound
from ..observability.logger import logger

class ParamsEventSchema(BaseModel):
    meal_id: uuid.UUID


class GetMealByIdController:

    def __init__(self, meal_repository: MealRepository):
        self.meal_repository = meal_repository

    def _validate_params(self, params: Dict[str, Any]):
        return ParamsEventSchema(**params)
    
    async def handle(self, request: ProtectedHttpRequest):
        try:
            data = self._validate_params(request.get("params"))
        except ValidationError as ex:
            return bad_request(body={"errors": ex.errors()})
        
        meal = await self.meal_repository.get_meal_by_id(meal_id=str(data.meal_id), user_id=request["user_id"])
        if not meal:
            logger.warning(f"Meal with id {data.meal_id} not found.")
            raise MealNotFound("Meal not found.")
        
        return ok(body={"meal": meal.to_dict})