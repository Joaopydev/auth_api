from datetime import date
from typing import Dict, AnyStr, Literal
from pydantic import BaseModel, ValidationError, EmailStr

from ..lib.jwt import signin_access_token
from ..app_types.http import HTTPResponse
from ..utils.http import created, bad_request, conflict

from ..repository.user_repository import UserRepository
from ..services.hashed.hashed_service import HashedPasswordService

from ..db.models.users import GenderType, GoalType
from ..lib.goal_calculator import calculate_goals, CalculateGoalsParams


class AccountSchema(BaseModel):
    name: str
    email: EmailStr
    password: str


class EventSchema(BaseModel):
    goal: GoalType
    gender: GenderType
    birthDate: date
    height: int
    weight: int
    activityLevel: Literal[1, 2, 3, 4, 5]
    account: AccountSchema


class SignupController:

    def __init__(self, user_repository: UserRepository, hashed_service: HashedPasswordService):
        self.user_repository = user_repository
        self.hashed_service = hashed_service

    def _validate_body(self, body: Dict[str, AnyStr]) -> EventSchema:
        return EventSchema(**body)
    
    async def handle(self, body: Dict[str, AnyStr]) -> HTTPResponse:
        try:
            event = self._validate_body(body)
        except ValidationError as ex:
            return bad_request(body={"errors": ex.errors()})
        
        user = await self.user_repository.get_user_by_email(email=event.account.email)
        if user:
            return conflict(body={"error": "Email already exists"})
            
        hashed_password = self.hashed_service.hash_password(password=event.account.password)
        calculate_goals_params = CalculateGoalsParams(
            height=event.height,
            weight=event.weight,
            gender=event.gender.value,
            birth_date=event.birthDate,
            activity_level=event.activityLevel,
            goal=event.goal.value
        )
        goals = calculate_goals(calculate_goals_params)
        new_user = await self.user_repository.insert_user(
            name=event.account.name,
            email=event.account.email,
            password=hashed_password,
            goal=event.goal,
            gender=event.gender,
            birth_date=event.birthDate,
            height=event.height,
            weight=event.weight,
            activity_level=event.activityLevel,
            calories=goals["calories"],
            proteins=goals["proteins"],
            carbohydrates=goals["carbohydrates"],
            fats=goals["fats"],
        )
        access_token = signin_access_token(user_id=new_user.id)
        return created(body={"accessToken": access_token})