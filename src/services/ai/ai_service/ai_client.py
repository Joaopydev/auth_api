import io
from datetime import datetime

from openai import AsyncOpenAI

from ..prompts.get_image_prompt import get_image_prompt
from ..prompts.get_text_prompt import get_text_prompt

class AIClient:

    def __init__(self):
        self.client = AsyncOpenAI()

    async def transcribe_audio(
        self,
        audio_data: bytes,
        key: str
    ) -> str:
        try:
            audio_file = io.BytesIO(audio_data)
            audio_file.name = key.split('/')[-1]

            transcript = await self.client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1"
            )
            return transcript.text
        except Exception as e:
            raise RuntimeError(f"Audio transcription failed ({e})")
        
    async def get_meal_details_from_text(
        self,
        input: str,
        created_at: datetime,
    ) -> str:
        user_input = f"""
            Date: {created_at}
            Meal: {input}
        """
        try:
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
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Failed to process meal details by text ({e})")
    
    async def get_meal_details_from_image(
        self,
        image_url: str,
        created_at: datetime
    ) -> str:
        try:
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
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Failed to process meal by image ({e})")