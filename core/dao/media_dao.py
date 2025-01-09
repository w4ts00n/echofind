from .s3_client import s3_client
from core.secrets import aws_bucket_name


class MediaDAO:
    @staticmethod
    def get(file_key: str):
        connection_with_storage = s3_client
        file = connection_with_storage.get_object(Bucket=aws_bucket_name, Key=file_key)
        file_body_content = file["Body"].read()

        return file_body_content

    @staticmethod
    def list(prefix: str):
        connection_with_storage = s3_client
        s3_files = connection_with_storage.list_objects_v2(Bucket=aws_bucket_name, Prefix=prefix)
        files_list = [obj["Key"] for obj in s3_files.get("Contents", []) if obj["Key"].endswith(".mp4")]
        return files_list

    @staticmethod
    def put(file_name: str, storage_file_path: str):
        connection_with_storage = s3_client
        connection_with_storage.upload_file(file_name, aws_bucket_name, storage_file_path)
