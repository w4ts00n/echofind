from .es_client import es_client


class TranscriptionDAO:
    @staticmethod
    def put(file_name: str, transcription: str, owner_id: str):
        es_client.index(
            index="my_index",
            body={
                "mp4name": file_name,
                "text": transcription,
                "owner_id": owner_id,
            },
        )
