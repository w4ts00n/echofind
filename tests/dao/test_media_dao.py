import tempfile
import pytest
from moto import mock_aws
import boto3
from core.dao.media_dao import MediaDAO
from core.secrets import aws_bucket_name
import os


@pytest.fixture
def s3_setup():
    with mock_aws():
        s3_client = boto3.client('s3')
        s3_client.create_bucket(Bucket=aws_bucket_name)
        yield s3_client


def test_get_media(s3_setup):
    s3_client = s3_setup
    file_key = "video.mp4"
    mock_file_content = b"mock_video content"

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(mock_file_content)

    s3_client.upload_file(temp_file.name, aws_bucket_name, file_key)

    file_content = MediaDAO.get(file_key)

    assert file_content == mock_file_content
    os.remove(temp_file.name)


def test_put_media(s3_setup):
    s3_client = s3_setup

    file_key = "video.mp4"
    mock_file_content = b"mock_video content"

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(mock_file_content)

    MediaDAO.put(temp_file.name, file_key)

    file = s3_client.get_object(Bucket=aws_bucket_name, Key=file_key)
    file_body_content = file['Body'].read()

    assert file_body_content == mock_file_content
    os.remove(temp_file.name)


def test_list_media(s3_setup):
    s3_client = s3_setup

    prefix = "videos"
    mock_files = [
        f"{prefix}/video1.mp4",
        f"{prefix}/video2.mp4",
        f"{prefix}/image1.jpg",
        "video4.mp4"
    ]
    mock_file_content = b"mock_video content"

    for mock_file in mock_files:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(mock_file_content)
            s3_client.upload_file(temp_file.name, aws_bucket_name, mock_file)
        os.remove(temp_file.name)

    listed_files = MediaDAO.list(prefix)
    expected_files = [f"{prefix}/video1.mp4", f"{prefix}/video2.mp4"]

    assert listed_files == expected_files










