from typing import List, TypedDict

class S3BucketInfo(TypedDict):
    name: str
    arn: str


class S3ObjectInfo(TypedDict):
    key: str
    size: int
    eTag: str
    sequencer: str


class S3Entity(TypedDict):
    s3SchemaVersion: str
    bucket: S3BucketInfo
    object: S3ObjectInfo


class S3Record(TypedDict):
    eventVersion: str
    eventSource: str
    awsRegion: str
    eventTime: str
    eventName: str
    s3: S3Entity


class S3Event(TypedDict):
    Records: List[S3Record]