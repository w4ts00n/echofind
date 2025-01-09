import tempfile
import os
from core.services.thumbnail_service import ThumbnailService
from core.dao.s3_client import s3_client
from core.secrets import aws_bucket_name


def test_thumbnail_service(mocker):
    file_key = f"test/test_file.mp4"
    thumbnail_path = f"owner123/test_file_thumbnail.jpg"
    file = s3_client.get_object(Bucket=aws_bucket_name, Key=file_key)
    file_content = file['Body'].read()
    mock_thumbnail_put = mocker.patch('core.dao.thumbnail_dao.ThumbnailDAO.put')

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name

    ThumbnailService.create_and_upload_thumbnail(temp_file_path, thumbnail_path)

    mock_thumbnail_put.assert_called_once_with(mocker.ANY, thumbnail_path)
    os.remove(temp_file_path)






