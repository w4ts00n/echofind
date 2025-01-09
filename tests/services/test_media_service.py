import tempfile
from unittest.mock import MagicMock
import core.services.transcription_service
from core.services.media_service import MediaService
import mimetypes


def test_generate_download_response():
    file_body_content = b"Test body content"
    content_type = "video/mp4"
    file_name = "video.mp4"

    response = MediaService.generate_download_response(file_body_content, content_type, file_name)

    assert response.content == file_body_content
    assert response["Content-Type"] == content_type
    assert response["Content-Disposition"] == f'attachment; filename="{file_name}"'


def test_get_media(mocker):
    file_body_content = b"Test body content"
    file_name = "video.mp4"
    owner_id = "owner123"
    content_type = "video/mp4"

    mocker.patch('core.dao.media_dao.MediaDAO.get', return_value=file_body_content)

    mocker.patch('core.services.media_service.mimetypes.guess_type', return_value=(content_type, None))

    response = MediaService.get_media(file_name, owner_id)

    assert response.content == file_body_content
    assert response["Content-Type"] == content_type
    assert response["Content-Disposition"] == f'attachment; filename="{file_name}"'


def test_get_media_list(mocker):
    owner_id = "owner123"
    files_names = [f"{owner_id}/video1.mp4", f"{owner_id}/video2.mp4"]
    mocker.patch("core.dao.media_dao.MediaDAO.list", return_value=files_names)

    response_file_names = MediaService.get_media_list(owner_id)
    expected_files_names = ["video1.mp4", "video2.mp4"]

    assert response_file_names == expected_files_names


def test_upload_video_and_transcription(mocker):
    mock_file = mocker.Mock()
    mock_file.read.return_value = b"Test body content"
    mock_file.name = "video1.mp4"
    owner_id = "owner123"
    thumbnail_path = f"{owner_id}/video1_thumbnail.jpg"
    storage_file_path = f"{owner_id}/{mock_file.name}"

    mock_tempfile = mocker.Mock()
    mock_tempfile.name = "path/to/mocked/file.mp4"

    mocker.patch("builtins.open", mocker.mock_open())
    mocker.patch("tempfile.NamedTemporaryFile", return_value=mock_tempfile)

    mock_create_transcription = mocker.patch(
        "core.services.transcription_service.TranscriptionService.create_transcription",
        return_value="test transcription")
    mock_transcription = mock_create_transcription.return_value

    mock_create_and_upload_thumbnail = mocker.patch(
        "core.services.thumbnail_service.ThumbnailService.create_and_upload_thumbnail")
    mock_index_transcription = mocker.patch(
        "core.services.transcription_service.TranscriptionService.index_transcription")
    mock_media_put = mocker.patch("core.dao.media_dao.MediaDAO.put")

    MediaService.upload_video_and_transcription(mock_file, owner_id)

    mock_create_transcription.assert_called_once_with(mock_tempfile.name)
    mock_create_and_upload_thumbnail.assert_called_once_with(mock_tempfile.name, thumbnail_path)
    mock_index_transcription.assert_called_once_with(mock_file.name, mock_transcription, owner_id)
    mock_media_put.assert_called_once_with(mock_tempfile.name, storage_file_path)
