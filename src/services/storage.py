import os
from dotenv import load_dotenv

from aiobotocore.response import StreamingBody
from botocore.exceptions import ClientError

from ..clients.s3_client import get_async_s3_client, sync_s3_client


load_dotenv()


class StorageService:

    @classmethod
    def get_download_url(cls, file_key: str, expires_in: int = 300) -> str:
        """To obtain a pre-signed URL for download, no content type parameters are required."""
        params = {
            "Bucket": os.getenv("BUCKET_NAME"),
            "Key": file_key,
        }
        return cls._get_presigned_url(
            method_type="get_object",
            params=params,
            expires_in=expires_in,
        )
    
    @classmethod
    def get_upload_url(cls, file_key: str, content_type: str, timezone: str, expires_in: int = 600) -> str:
        """Content-Type is required to get pre-signed url for upload"""
        params = {
            "Bucket": os.getenv("BUCKET_NAME"),
            "Key": file_key,
            "ContentType": content_type,
            "Metadata": {
                "timezone": timezone
            }
        }
        return cls._get_presigned_url(
            method_type="put_object",
            params=params,
            expires_in=expires_in,
        )

    @classmethod
    def _get_presigned_url(cls, method_type: str, params: dict,  expires_in: int) -> str:
        # Generate pre-signed URL
        try:
            presigned_url = sync_s3_client.generate_presigned_url(
                method_type,
                Params=params,
                ExpiresIn=expires_in,
            )
            return presigned_url
        except ClientError as e:
            raise RuntimeError(f"Error generating presigned URL: {e}") from e
    
    @classmethod
    async def read_object_content(cls, key: str) -> bytes:
        try:
            async with get_async_s3_client() as s3_client:
                obj = await s3_client.get_object(
                    Bucket=os.getenv("BUCKET_NAME"),
                    Key=key
                )
                async_streaming_body: StreamingBody = obj["Body"]
                return await async_streaming_body.read()  # Read the content of the streaming body
        except ClientError as e:
            raise RuntimeError(f"Failed to fetch object in s3: {e}") from e
        
    @classmethod
    async def head_object(cls, key: str) -> dict:
        try:
            async with get_async_s3_client() as s3_client:
                return await s3_client.head_object(
                    Bucket=os.getenv("BUCKET_NAME"),
                    Key=key
                )

        except ClientError as e:
            raise RuntimeError(
                f"Failed to head object in s3: {e}"
            ) from e