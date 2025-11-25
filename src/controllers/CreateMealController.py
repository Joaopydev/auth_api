import os
import uuid

from typing import Dict, Any, Optional
from enum import StrEnum
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from sqlalchemy.ext.asyncio import AsyncSession

from ..utils.http import bad_request, created
from ..clients.s3_client import s3_client
from ..db.connection import get_db
from ..db.models.meals import Meal, MealStatus, InputType
from ..app_types.http import HTTPResponse, ProtectedHttpRequest


load_dotenv()


class FileType(StrEnum):
    audio = "audio/m4a"
    jpeg = "image/jpeg"


class CreateMealSchema(BaseModel):
    file_type: FileType
    

class CreateMealController:

    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session or get_db

    def _validate_body(self, body: Dict[str, Any]) -> CreateMealSchema:
        return CreateMealSchema(**body)
    
    async def handle(self, request: ProtectedHttpRequest) -> HTTPResponse:
        # Validate input body with Pydantic
        try:
            data = self._validate_body(body=request.get("body", {}))
        except ValidationError as ex:
            return bad_request(body={"errors": ex.errors()})
        
        # Generate file key
        file_id = uuid.uuid4()
        ext = ".m4a" if data.file_type == FileType.audio else ".jpg"
        file_key = f"{file_id}{ext}"
        
        try:
            presigned_url = self.get_presigned_url(
                file_key=file_key,
                content_type=data.file_type.value
            )
        except RuntimeError as e:
            return bad_request(body={"error": str(e)})

        async with self.session() as db:
            meal = Meal(
                user_id=int(request["user_id"]),
                status=MealStatus.uploading,
                input_file_key=file_key,
                input_type=InputType.audio if data.file_type == "audio/m4a" else InputType.picture,
                icon="",
                name="",
                foods=[],
            )

            db.add(meal)
            await db.commit()
            await db.refresh(meal)

            return created(body={
                "meal_id": meal.id,
                "presigned_url": presigned_url,
            })
        
    def get_presigned_url(self, file_key: str, content_type: str, expires_in: int = 600):
        # Generate pre-signed URL
        try:
            presigned_url = s3_client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": os.getenv("BUCKET_NAME"),
                    "Key": file_key,
                    "ContentType": content_type,
                },
                ExpiresIn=expires_in,
            )
            return presigned_url
        except ClientError as e:
            raise RuntimeError(f"Error generating presigned URL: {e}")
