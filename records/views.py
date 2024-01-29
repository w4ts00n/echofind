from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.shortcuts import render
from elasticsearch import Elasticsearch
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

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


class FileView(APIView):
    def get(self, request):
        file_name = request.GET.get("file_name", "")
        content_type = mimetypes.guess_type(file_name)[0]

        connection_with_storage = get_connection_with_storage()
        file = connection_with_storage.get_object(Bucket=bucket_name, Key=file_name)
        file_body_content = file["Body"].read()

        response = generate_file_response(file_body_content, content_type, file_name)
        return response

    def post(self, request):
        if not request.FILES["mp4file"]:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        with open((temp_file := tempfile.NamedTemporaryFile(delete=False)).name, "wb") as temp_file_io:
            temp_file_io.write(request.FILES["mp4file"].read())
            file_name = request.FILES["mp4file"].name

            whisper_instance = whisper.load_model("large")
            video_transcription = whisper_instance.transcribe(temp_file.name)

            connection_with_storage = get_connection_with_storage()
            index_transcription(file_name, video_transcription["text"])
            connection_with_storage.upload_file(temp_file.name, bucket_name, file_name)
        temp_file.close()

        return HttpResponseRedirect("/")


class SearchView(APIView):
    def get(self, request):
        es = get_connection_with_database()
        keyword = request.GET.get("keyword", "")
        search_query = {"query": {"match": {"text": keyword}}}

        hits = es.search(index="my_index", body=search_query).get("hits", {}).get("hits", [])

        results_details = {}
        for hit in hits:
            key = hit["_source"].get("mp4name", "")
            details_dict = {}
            details_dict["text"] = hit["_source"].get("text", "")
            details_dict["url"] = reverse("file_api") + f"?file_name={hit['_source'].get('mp4name')}"
            results_details[key] = details_dict

        if not results_details:
            return JsonResponse({"message": "No results"}, status=404)

        return JsonResponse({"results": results_details}, status=200)


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


def index_transcription(file_name: str, transcription: str):
    es = get_connection_with_database()
    es.index(
        index="my_index",
        body={
            "mp4name": file_name,
            "text": transcription,
        },
    )


def get_files_list():
    connection_with_storage = get_connection_with_storage()
    s3_files = connection_with_storage.list_objects_v2(Bucket=bucket_name)
    files_list = [obj["Key"] for obj in s3_files.get("Contents", [])]
    return files_list


def generate_file_response(file_body_content, content_type, file_name):
    response = HttpResponse(file_body_content, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{file_name}"'
    return response


def render_main_page(request):
    files_list = get_files_list()
    return render(request, "echofind.html", {"files_list": files_list})
