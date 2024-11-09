import mimetypes
from django.core.files.uploadedfile import UploadedFile
from core.dao.file_dao import FileDAO
from django.http import HttpResponse
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image
from io import BytesIO
import tempfile
import whisper
from pathlib import Path


class FileService:
    @staticmethod
    def get_file(file_name: str, owner_id: str):
        content_type = mimetypes.guess_type(file_name)[0]

        file_key = f"{owner_id}/{file_name}"
        file_body_content = FileDAO.get_file(file_key)

        response = FileService.generate_file_response(file_body_content, content_type, file_name)
        return response

    @staticmethod
    def upload_video_and_transcription(file: UploadedFile, owner_id: str):
        with open((temp_file := tempfile.NamedTemporaryFile(delete=False)).name, "wb") as temp_file_io:
            temp_file_io.write(file.read())
            file_name = file.name

            video_transcription = FileService.create_transcription(temp_file.name)

            file_name_without_extension = Path(file_name).stem
            thumbnail_path = f"{owner_id}/{file_name_without_extension}_thumbnail.jpg"
            FileService.create_and_upload_thumbnail(temp_file.name, thumbnail_path)

            FileDAO.index_transcription(file_name, video_transcription, owner_id)

            storage_file_path = f"{owner_id}/{file_name}"
            FileDAO.upload_file(temp_file.name, storage_file_path)

        temp_file.close()

    @staticmethod
    def create_transcription(file_path: str):
        whisper_instance = whisper.load_model("base")
        video_transcription = whisper_instance.transcribe(file_path)
        return video_transcription["text"]

    @staticmethod
    def create_and_upload_thumbnail(video_path: str, output_thumbnail_path: str, time_at_seconds=5):
        video_clip = VideoFileClip(video_path)
        thumbnail_frame = video_clip.get_frame(time_at_seconds)

        thumbnail_image = Image.fromarray(thumbnail_frame)
        thumbnail_file_io = BytesIO()
        thumbnail_image.save(thumbnail_file_io, format='JPEG')
        thumbnail_file_io.seek(0)

        FileDAO.upload_thumbnail(thumbnail_file_io, output_thumbnail_path)

    @staticmethod
    def generate_file_response(file_body_content: bytes, content_type: str, file_name: str):
        response = HttpResponse(file_body_content, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{file_name}"'
        return response

    @staticmethod
    def get_files_list(owner_id: str):
        files_list = FileDAO.get_files_list(owner_id)
        files_names = [Path(file).name for file in files_list]

        return files_names
