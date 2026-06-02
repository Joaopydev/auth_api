import os
import asyncio
import json

from dotenv import load_dotenv
from ..app_types.s3_events import S3Event
from ..clients.sqs_client import get_sqs_client
from ..observability.logger import logger

load_dotenv()

async def async_handler(event: S3Event, context: any):
    logger.info(
        msg="S3 event received",
        extra={
            "records_count": len(event["Records"]),
        }
    )
    async with get_sqs_client() as client:
        tasks = []

        for record in event["Records"]:
            file_key = record["s3"]["object"]["key"]

            logger.info(
                msg="Queuing meal for processing",
                extra={
                    "file_key": file_key,
                }
            )

            tasks.append(
                client.send_message(
                    QueueUrl=os.getenv("MEALS_QUEUE_URL"),
                    MessageBody=json.dumps({"file_key": file_key}),
                )
            )
        await asyncio.gather(*tasks)

    logger.info("S3 event processing finished")

@logger.inject_lambda_context
def handler(event: S3Event, context: any):
    asyncio.run(async_handler(event=event, context=context))