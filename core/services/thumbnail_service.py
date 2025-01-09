from core.dao.thumbnail_dao import ThumbnailDAO
from io import BytesIO
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image


class ThumbnailService:
    @staticmethod
    def create_and_upload_thumbnail(video_path: str, output_thumbnail_path: str, time_at_seconds=5):
        video_clip = VideoFileClip(video_path)
        try:
            thumbnail_frame = video_clip.get_frame(time_at_seconds)

            thumbnail_image = Image.fromarray(thumbnail_frame)
            thumbnail_file_io = BytesIO()
            thumbnail_image.save(thumbnail_file_io, format='JPEG')
            thumbnail_file_io.seek(0)

            ThumbnailDAO.put(thumbnail_file_io, output_thumbnail_path)
        finally:
            video_clip.close()
