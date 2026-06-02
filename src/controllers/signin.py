from typing import Dict
from pydantic import BaseModel, ValidationError, EmailStr

from ..lib.jwt import signin_access_token
from ..app_types.http import HTTPResponse
from ..utils.http import ok, bad_request, unauthorized

from ..repository.user_repository import UserRepository
from ..services.hashed.hashed_service import HashedPasswordService


class EventSchema(BaseModel):
    email: EmailStr
    password: str


class SigninController:

    def __init__(self, user_repository: UserRepository, hashed_service: HashedPasswordService):
        self.user_repository = user_repository
        self.hashed_service = hashed_service


    def _validate_body(self, body: Dict[str, str]) -> EventSchema:
        return EventSchema(**body)
    
    async def handle(self, body: Dict[str, str]) -> HTTPResponse:
        try:
            event = self._validate_body(body=body)
        except ValidationError as ex:
            return bad_request(body={"errors": ex.errors()})
        
        user = await self.user_repository.get_user_by_email(email=event.email)
        if not user:
            return unauthorized(body={"error": "Invalid Credentials."})
        
        is_valid_password = self.hashed_service.verify_password(
            password=event.password,
            hashed_password=user.password
        )
        if not is_valid_password:
            return unauthorized(body={"error": "Invalid Credentials."})
        
        access_token = signin_access_token(user_id=user.id)
        return ok(body={"accessToken": access_token})