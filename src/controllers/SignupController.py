from typing import Dict, AnyStr, Optional
from pydantic import BaseModel, ValidationError, EmailStr

import bcrypt

from ..lib.jwt import signin_access_token
from ..app_types.http import HTTPResponse
from ..utils.http import created, bad_request, conflict

from ..db.connection import get_db
from ..db.models.users import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class EventSchema(BaseModel):
    name: str
    email: EmailStr
    password: str


class SignupController:

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session or get_db

    def _validate_body(self, body: Dict[str, AnyStr]) -> EventSchema:
        return EventSchema(**body)
    
    async def handle(self, body: Dict[str, AnyStr]) -> HTTPResponse:
        try:
            data = self._validate_body(body)
        except ValidationError as ex:
            return bad_request(body={"errors": ex.errors()})
        
        body = data.model_dump()
        async with self.session() as db:
            query = select(User).where(User.email == body["email"])
            result = await db.execute(query)
            user = result.scalars().first()
            if user:
                return conflict(body={"error": "Email already exists"})
            
            hashed_password = bcrypt.hashpw(
                password=body.get("password").encode("utf-8"),
                salt=bcrypt.gensalt(8),
            )
            new_user = User(
                name=body.get("name"),
                email=body.get("email"),
                password=hashed_password,
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            access_token = signin_access_token(user_id=new_user.id)
            
            return created(body={"access_token": access_token})