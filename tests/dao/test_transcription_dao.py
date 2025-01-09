from core.dao.transcription_dao import TranscriptionDAO
from pytest_elasticsearch import factories
from core.dao.es_client import es_client


def test_put_transcription(mocker):
    file_name = "file2.txt"
    transcription = "Transcription test text"
    owner_id = "user1234"

    mock_es_client = mocker.patch('core.dao.transcription_dao.es_client')

    TranscriptionDAO.put(file_name, transcription, owner_id)

    mock_es_client.index.assert_called_once_with(
        index="my_index",
        body={
            "mp4name": file_name,
            "text": transcription,
            "owner_id": owner_id
        }
    )


