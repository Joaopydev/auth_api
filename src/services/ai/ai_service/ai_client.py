import io
from datetime import datetime

from openai import AsyncOpenAI

from ..prompts.get_image_prompt import get_image_prompt
from ..prompts.get_text_prompt import get_text_prompt

from ....observability.logger import logger

class AIClient:

    def __init__(self):
        self.client = AsyncOpenAI()

    async def transcribe_audio(
        self,
        audio_data: bytes,
        key: str
    ) -> str:
        try:
            logger.info(
                msg="Starting audio transcription",
                extra={
                    "file_key": key
                }
            )
            audio_file = io.BytesIO(audio_data)
            audio_file.name = key.split('/')[-1]

            transcript = await self.client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1"
            )

            logger.info(
                msg="Audio transcription completed",
                extra={
                    "file_key": key
                }
            )
            return transcript.text
        except Exception as e:
            logger.exception(
                msg="Audio transcription failed",
                extra={
                    "file_key": key,
                }
            )
            raise
        
    async def get_meal_details_from_text(
        self,
        input: str,
        created_at: datetime,
        file_key: str
    ) -> str:
        user_input = f"""
            Date: {created_at}
            Meal: {input}
        """
        try:
            logger.info(
                msg="Starting meal details extraction from text",
                extra={
                    "file_key": file_key
                }
            )
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": get_text_prompt()
                    },
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ]
            )
            logger.info(
                msg="Meal details extraction from text completed",
                extra={
                    "file_key": file_key
                }
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.exception(
                msg="Meal details extraction from text failed",
                extra={
                    "file_key": file_key,
                }
            )
            raise

    async def get_meal_details_from_image(
        self,
        image_url: str,
        created_at: datetime,
        file_key: str
    ) -> str:
        try:
            logger.info(
                msg="Starting meal details extraction from image",
                extra={
                    "file_key": file_key
                }
            )

            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": get_image_prompt(created_at)
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ]
            )
            
            logger.info(
                msg="Meal details extraction from image completed",
                extra={
                    "file_key": file_key
                }
            )
            return response.choices[0].message.content
        except Exception:
            logger.exception(
                msg="Meal details extraction from image failed",
                extra={
                    "file_key": file_key
                }
            )
            raise 