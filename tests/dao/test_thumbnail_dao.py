from io import BytesIO
import pytest
from moto import mock_aws
import boto3
from core.dao.thumbnail_dao import ThumbnailDAO
from core.secrets import aws_bucket_name


@pytest.fixture
def s3_setup():
    with mock_aws():
        s3_client = boto3.client('s3')
        s3_client.create_bucket(Bucket=aws_bucket_name)
        yield s3_client


def test_put_thumbnail(s3_setup):
    s3_client = s3_setup

    mock_file_content = b"mock_video content"
    output_thumbnail_path = "thumbnail/test_thumbnail.jpg"
    thumbnail_file_io = BytesIO(mock_file_content)

    ThumbnailDAO.put(thumbnail_file_io, output_thumbnail_path)

    file = s3_client.get_object(Bucket=aws_bucket_name, Key=output_thumbnail_path)
    file_body_content = file['Body'].read()

    assert file_body_content == mock_file_content
