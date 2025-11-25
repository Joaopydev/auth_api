from typing import Dict, AnyStr, Optional
from pydantic import BaseModel, ValidationError, EmailStr
import bcrypt

from ..db.connection import get_db
from ..db.models.users import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..lib.jwt import signin_access_token
from ..app_types.http import HTTPResponse
from ..utils.http import ok, bad_request, unauthorized


class EventSchema(BaseModel):
    email: EmailStr
    password: str


class SigninController:

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session or get_db

    def _validate_body(self, body: Dict[str, AnyStr]) -> EventSchema:
        return EventSchema(**body)
    
    async def handle(self, body: Dict[str, AnyStr]) -> HTTPResponse:
        try:
            data = self._validate_body(body=body)
        except ValidationError as ex:
            return bad_request(body={"errors": ex.errors()})
        
        body = data.model_dump()
        async with self.session() as db:
            query = select(User).where(User.email == body["email"])
            result = await db.execute(query)
            user = result.scalars().first()
            if not user:
                return unauthorized(body={"error": "Invalid Credentials."})
            
            is_valid_password = bcrypt.checkpw(
                body.get("password").encode("utf-8"),
                user.password
            )
            if not is_valid_password:
                return unauthorized(body={"error": "Invalid Credentials."})
            
            access_token = signin_access_token(user_id=user.id)
            
            return ok(body={"access_token": access_token})