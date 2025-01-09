import mimetypes
import os

from django.core.files.uploadedfile import UploadedFile
from core.dao.media_dao import MediaDAO
from core.services.thumbnail_service import ThumbnailService
from core.services.transcription_service import TranscriptionService
from django.http import HttpResponse
import tempfile
from pathlib import Path


class MediaService:
    @staticmethod
    def get_media(file_name: str, owner_id: str):
        content_type = mimetypes.guess_type(file_name)[0]

        file_key = f"{owner_id}/{file_name}"
        file_body_content = MediaDAO.get(file_key)

        response = MediaService.generate_download_response(file_body_content, content_type, file_name)
        return response

    @staticmethod
    def upload_video_and_transcription(file: UploadedFile, owner_id: str):
        with open((temp_file := tempfile.NamedTemporaryFile(delete=False)).name, "wb") as temp_file_io:
            temp_file_io.write(file.read())
            file_name = file.name

            video_transcription = TranscriptionService.create_transcription(temp_file.name)

            file_name_without_extension = Path(file_name).stem
            thumbnail_path = f"{owner_id}/{file_name_without_extension}_thumbnail.jpg"
            ThumbnailService.create_and_upload_thumbnail(temp_file.name, thumbnail_path)

            TranscriptionService.index_transcription(file_name, video_transcription, owner_id)

            storage_file_path = f"{owner_id}/{file_name}"
            MediaDAO.put(temp_file.name, storage_file_path)

        temp_file.close()

    @staticmethod
    def generate_download_response(file_body_content: bytes, content_type: str, file_name: str):
        response = HttpResponse(file_body_content, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response

    @staticmethod
    def get_media_list(owner_id: str):
        prefix = f"{owner_id}/"
        files_list = MediaDAO.list(prefix)
        files_names = [Path(file).name for file in files_list]

        return files_names
