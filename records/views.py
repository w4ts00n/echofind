from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.shortcuts import render
from elasticsearch import Elasticsearch
from .credentials import (
    aws_access_key,
    aws_secret_access_key,
    bucket_name,
    es_hosts,
    es_api_key,
)
import whisper
import boto3
import tempfile
import mimetypes


def get_connection_with_storage():
    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_access_key,
        use_ssl=False,
    )
    return s3


def get_connection_with_database():
    es = Elasticsearch(es_hosts, api_key=es_api_key)
    return es


def handle_upload(request):
    if request.method == "POST" and request.FILES["mp4file"]:
        mp4file = request.FILES["mp4file"]

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
            with open(temp_file_path, "wb") as file:
                file.write(mp4file.read())

            model = whisper.load_model("base")
            result = model.transcribe(temp_file_path)

            es = get_connection_with_database()
            es.index(
                index="my_index",
                body={
                    "mp4name": mp4file.name,
                    "text": result["text"],
                },
            )

            connection_with_storage = get_connection_with_storage()
            connection_with_storage.upload_file(temp_file_path, bucket_name, mp4file.name)

    return HttpResponseRedirect("/")


def get_files_list():
    connection_with_storage = get_connection_with_storage()
    s3_files = connection_with_storage.list_objects_v2(Bucket=bucket_name)
    files_list = [obj["Key"] for obj in s3_files.get("Contents", [])]
    return files_list


def generate_file_response(file_body_content, content_type, file_name):
    response = HttpResponse(file_body_content, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{file_name}"'
    return response


def download_file(request, file_name):
    connection_with_storage = get_connection_with_storage()
    file = connection_with_storage.get_object(Bucket=bucket_name, Key=file_name)
    file_body_content = file["Body"].read()
    content_type = mimetypes.guess_type(file_name)[0]

    response = generate_file_response(file_body_content, content_type, file_name)

    return response


def search_files(request):
    keyword = request.GET.get("keyword", "")

    es = get_connection_with_database()

    search_query = {"query": {"match": {"text": keyword}}}
    hits = es.search(index="my_index", body=search_query).get("hits", {}).get("hits", [])

    response_data = [
        {
            "mp4name": hit["_source"].get("mp4name", ""),
            "text": hit["_source"].get("text", ""),
            "url": reverse("download_file", kwargs={"file_name": hit["_source"].get("mp4name")}),
        }
        for hit in hits
    ]

    return JsonResponse({"results": response_data})


def render_main_page(request):
    files_list = get_files_list()
    return render(request, "echofind.html", {"files_list": files_list})
