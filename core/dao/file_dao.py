from .s3_client import s3_client
from .es_client import es_client
from core.secrets import aws_bucket_name
from io import BytesIO


class FileDAO:
    @staticmethod
    def get_file(file_key: str):
        connection_with_storage = s3_client
        file = connection_with_storage.get_object(Bucket=aws_bucket_name, Key=file_key)
        file_body_content = file["Body"].read()

        return file_body_content

    @staticmethod
    def get_files_list(owner_id: str):
        connection_with_storage = s3_client
        prefix = f"{owner_id}/"
        s3_files = connection_with_storage.list_objects_v2(Bucket=aws_bucket_name, Prefix=prefix)
        files_list = [obj["Key"] for obj in s3_files.get("Contents", []) if obj["Key"].endswith(".mp4")]
        return files_list

    @staticmethod
    def upload_file(file_name: str, storage_file_path: str):
        connection_with_storage = s3_client
        connection_with_storage.upload_file(file_name, aws_bucket_name, storage_file_path)

    @staticmethod
    def upload_thumbnail(thumbnail_file_io: BytesIO, thumbnail_file_path: str):
        connection_with_storage = s3_client
        connection_with_storage.upload_fileobj(thumbnail_file_io, aws_bucket_name, thumbnail_file_path)

    @staticmethod
    def index_transcription(file_name: str, transcription: str, owner_id: str):
        es_client.index(
            index="my_index",
            body={
                "mp4name": file_name,
                "text": transcription,
                "owner_id": owner_id,
            },
        )
