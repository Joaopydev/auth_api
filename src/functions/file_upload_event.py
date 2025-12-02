import asyncio
import os

from dotenv import load_dotenv

from ..app_types.s3_events import S3Event
from ..clients.sqs_client import sqs_client

load_dotenv()

async def async_handler(event: S3Event):
    async with sqs_client as client:
        tasks = [
            client.send_message(
                QueueUrl=os.getenv("MEALS_QUEUE_URL"),
                MessageBody=record["s3"]["object"]["key"]
            )
            for record in event["Records"]
        ]
        return await asyncio.gather(*tasks)

def handler(event: S3Event):
    return asyncio.run(async_handler(event=event))