from core.services.transcription_service import TranscriptionService


def test_index_transcription(mocker):
    file_name = "video1.mp4"
    transcription = "Test transcription"
    owner_id = "owner123"

    mock_es_client = mocker.patch('core.dao.transcription_dao.es_client')

    TranscriptionService.index_transcription(file_name, transcription, owner_id)

    mock_es_client.index.assert_called_once_with(
        index="my_index",
        body={"mp4name": file_name,
              "text": transcription,
              "owner_id": owner_id}
    )


def test_create_transcription(mocker):
    mock_transcription = {"text": "Test transcription"}
    file_path = "video1.mp4"
    mock_model = mocker.patch("core.services.transcription_service.whisper.load_model", return_value=mocker.Mock())
    mock_model().transcribe.return_value = mock_transcription

    result = TranscriptionService.create_transcription(file_path)

    assert result == "Test transcription"





