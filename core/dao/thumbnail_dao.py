from core.dao.s3_client import s3_client
from core.secrets import aws_bucket_name
from io import BytesIO


class ThumbnailDAO:
    @staticmethod
    def put(thumbnail_file_io: BytesIO, thumbnail_file_path: str):
        connection_with_storage = s3_client
        connection_with_storage.upload_fileobj(thumbnail_file_io, aws_bucket_name, thumbnail_file_path)
