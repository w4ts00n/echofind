import whisper
from core.dao.transcription_dao import TranscriptionDAO


class TranscriptionService:
    @staticmethod
    def create_transcription(file_path: str):
        whisper_instance = whisper.load_model("base")
        video_transcription = whisper_instance.transcribe(file_path)
        return video_transcription["text"]

    @staticmethod
    def index_transcription(file_name: str, transcription: str, owner_id: str):
        TranscriptionDAO.put(file_name, transcription, owner_id)
