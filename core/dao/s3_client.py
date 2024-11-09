import boto3
from core.secrets import aws_secret_access_key, aws_access_key_id


class S3Client:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                use_ssl=False
            )
            return cls._instance


s3_client = S3Client()
