from io import BytesIO
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.shortcuts import render
from elasticsearch import Elasticsearch
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip
from pathlib import Path
from .credentials import (
    aws_access_key_id,
    aws_secret_access_key,
    aws_bucket_name,
    es_hosts,
    es_api_key,
    firebase_api_key
)
import whisper
import boto3
import tempfile
import mimetypes
import requests
from firebase_admin import auth


class FileView(APIView):
    def get(self, request):
        file_name = request.GET.get("file_name")
        content_type = mimetypes.guess_type(file_name)[0]

        connection_with_storage = get_connection_with_storage()
        owner_id = request.session.get('localId')
        file_key = f"{owner_id}/{file_name}"
        file = connection_with_storage.get_object(Bucket=aws_bucket_name, Key=file_key)
        file_body_content = file["Body"].read()

        response = generate_file_response(file_body_content, content_type, file_name)
        return response

    def post(self, request):
        if not request.FILES["mp4file"]:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        with open((temp_file := tempfile.NamedTemporaryFile(delete=False)).name, "wb") as temp_file_io:
            temp_file_io.write(request.FILES["mp4file"].read())
            file_name = request.FILES["mp4file"].name
            owner_id = request.session.get("localId")

            whisper_instance = whisper.load_model("large")
            video_transcription = whisper_instance.transcribe(temp_file.name)

            connection_with_storage = get_connection_with_storage()

            file_name_without_extension = Path(file_name).stem
            thumbnail_path = f"{owner_id}/{file_name_without_extension}_thumbnail.jpg"
            create_and_upload_thumbnail(temp_file.name, thumbnail_path)

            index_transcription(file_name, video_transcription["text"], owner_id)

            storage_file_path = f"{owner_id}/{file_name}"
            connection_with_storage.upload_file(temp_file.name, aws_bucket_name, storage_file_path)

        temp_file.close()

        return HttpResponseRedirect("/")


class SearchView(APIView):
    def get(self, request):
        es = get_connection_with_database()
        keyword = request.GET.get("keyword", "")
        owner_id = request.session.get("localId")
        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {"match_phrase": {"text": keyword}},
                        {"match": {"owner_id": owner_id}}
                    ]
                }
            },
            "highlight": {
                "fields": {
                    "text": {
                        "pre_tags": ["<em>"],
                        "post_tags": ["</em>"],
                    }
                }
            }
        }

        hits = es.search(index="my_index", body=search_query).get("hits", {}).get("hits", [])

        results = {}
        for hit in hits:
            original_json_document = hit["_source"]
            matched_mp4_filename = original_json_document.get("mp4name")

            search_result_details_dict = {}
            search_result_details_dict["text"] = hit["highlight"].get("text")
            search_result_details_dict["url"] = reverse("file_api") + f"?file_name={matched_mp4_filename}"

            thumbnail_path = f"{Path(matched_mp4_filename).stem}_thumbnail.jpg"
            search_result_details_dict["thumbnail_url"] = reverse("file_api") + f"?file_name={thumbnail_path}"
            results[matched_mp4_filename] = search_result_details_dict

        if not results:
            return JsonResponse({"message": "No results"}, status=404)

        return JsonResponse({"results": results}, status=200)


def get_connection_with_storage():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        use_ssl=False,
    )
    return s3


def get_connection_with_database():
    es = Elasticsearch(hosts=es_hosts, api_key=es_api_key)
    return es


def index_transcription(file_name: str, transcription: str, owner_id: str):
    es = get_connection_with_database()
    es.index(
        index="my_index",
        body={
            "mp4name": file_name,
            "text": transcription,
            "owner_id": owner_id,
        },
    )


def get_files_list(owner_id: str):
    connection_with_storage = get_connection_with_storage()
    prefix = f"{owner_id}/"
    s3_files = connection_with_storage.list_objects_v2(Bucket=aws_bucket_name, Prefix=prefix)
    files_list = [obj["Key"] for obj in s3_files.get("Contents", []) if obj["Key"].endswith(".mp4")]
    return files_list


def create_and_upload_thumbnail(video_path: str, output_thumbnail_path: str, time_at_seconds=5):
    video_clip = VideoFileClip(video_path)
    thumbnail_frame = video_clip.get_frame(time_at_seconds)
    connection_with_storage = get_connection_with_storage()

    thumbnail_image = Image.fromarray(thumbnail_frame)
    thumbnail_file_io = BytesIO()
    thumbnail_image.save(thumbnail_file_io, format='JPEG')
    thumbnail_file_io.seek(0)

    connection_with_storage.upload_fileobj(thumbnail_file_io, aws_bucket_name, output_thumbnail_path)


def generate_file_response(file_body_content: bytes, content_type: str, file_name: str):
    response = HttpResponse(file_body_content, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{file_name}"'
    return response


def check_email_verified(id_token: str):
    api_key = firebase_api_key
    get_user_data_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"

    data = {
        "idToken": id_token,
    }

    response = requests.post(get_user_data_url, data=data)

    if response.status_code == 200:
        user_data = response.json()
        user = user_data.get("users", [])[0] if user_data.get("users") else {}
        return user.get("emailVerified", False)
    else:
        return False


def authenticate_user(email: str, password: str, url: str):
    data = {"email": email,
            "password": password,
            "returnSecureToken": True}
    response = requests.post(url, data=data)
    return response


def register_user(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        api_key = firebase_api_key

        register_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
        response = authenticate_user(email, password, register_url)

        if response.status_code == 200:
            user_data = response.json()
            request.session["localId"] = user_data["localId"]
            request.session["email"] = user_data["email"]

            email_verification_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
            email_verification_data = {
                "requestType": "VERIFY_EMAIL",
                "idToken": user_data.get("idToken"),
            }

            email_verification_response = requests.post(email_verification_url, data=email_verification_data)

            if email_verification_response.status_code == 200:
                payload = {
                    "idToken": user_data.get("idToken"),
                    "email": user_data.get("email"),
                    "refreshToken": user_data.get("refreshToken"),
                    "expiresIn": user_data.get("expiresIn"),
                    "localId": user_data.get("localId"),
                }
                return JsonResponse(payload)
            else:
                error_message = response.json().get("error", {}).get("message", "Failed to send verification email")
                return JsonResponse({"error": error_message}, status=email_verification_response.status_code)
        else:
            error_message = response.json().get("error", {}).get("message", "Unknown error occurred")
            return JsonResponse({"error": error_message}, status=response.status_code)


def login_user(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        api_key = firebase_api_key

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        response = authenticate_user(email, password, url)

        if response.status_code == 200:
            user_data = response.json()
            id_token = user_data["idToken"]

            if not check_email_verified(id_token):
                return JsonResponse({"error": "Email not verified"}, status=400)

            request.session["idToken"] = user_data["idToken"]
            request.session["localId"] = user_data["localId"]
            request.session["email"] = user_data["email"]

            payload = {
                "idToken": user_data.get("idToken"),
                "email": user_data.get("email"),
                "refreshToken": user_data.get("refreshToken"),
                "expiresIn": user_data.get("expiresIn"),
                "localId": user_data.get("localId"),
                "registered": user_data.get("registered"),
            }
            return JsonResponse(payload)
        else:
            error_message = response.json().get("error", {}).get("message", "Unknown error occurred")
            return JsonResponse({"error": error_message}, status=response.status_code)


def logout_user(request):
    if request.method == "POST":

        localId = request.session.get('localId')
        idToken = request.session.get('idToken')

        auth.revoke_refresh_tokens(localId)

        try:
            auth.verify_id_token(idToken, check_revoked=True)
            print('Token is still valid (this should not happen)')
        except auth.RevokedIdTokenError:
            print('Token has been revoked successfully')
        except Exception as e:
            print(f'Error verifying token: {e}')

        request.session.flush()
        return HttpResponseRedirect("/")


def render_main_page(request):
    if not request.session.get("idToken"):
        return render(request, "login.html")

    owner_id = request.session.get("localId")
    files_list = get_files_list(owner_id)

    files_names = [Path(file).name for file in files_list]
    return render(request, "echofind.html", {"files_list": files_names})
