from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from core.services.media_service import MediaService
from core.services.search_service import SearchService
from core.services.auth_service import AuthService


class FileView(APIView):
    def get(self, request):
        file_name = request.GET.get("file_name")
        owner_id = request.session.get('localId')

        response = MediaService.get_media(file_name, owner_id)
        return response

    def post(self, request):
        if not request.FILES["mp4file"]:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES["mp4file"]
        owner_id = request.session.get("localId")

        MediaService.upload_video_and_transcription(file, owner_id)
        return HttpResponseRedirect("/")


class SearchView(APIView):
    def get(self, request):
        keyword = request.GET.get("keyword", "")
        owner_id = request.session.get("localId")

        search_results = SearchService.search_files(keyword, owner_id)

        if not search_results:
            return JsonResponse({"message": "No results"}, status=404)

        return JsonResponse({"results": search_results}, status=200)


class RegisterView(APIView):
    def post(self, request):
        email = request.POST["email"]
        password = request.POST["password"]

        response = AuthService.register_user(email, password)

        if response.status_code == 200:
            user_data = response.json()
            request.session["localId"] = user_data["localId"]
            request.session["email"] = user_data["email"]

            idToken = user_data.get("idToken")

            email_verification_response = AuthService.send_verification_email(idToken)

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


class LoginView(APIView):
    def post(self, request):
        email = request.POST["email"]
        password = request.POST["password"]

        response = AuthService.authenticate_user(email, password)

        if response.status_code == 200:
            user_data = response.json()
            id_token = user_data["idToken"]

            if not AuthService.check_email_verified(id_token):
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


class LogoutView(APIView):
    def post(self, request):
        localId = request.session.get('localId')
        idToken = request.session.get('idToken')

        AuthService.logout_user(localId, idToken)

        request.session.flush()
        return HttpResponseRedirect("/")


def render_main_page(request):
    if not request.session.get("idToken"):
        return render(request, "login.html")

    owner_id = request.session.get("localId")

    files_names = MediaService.get_media_list(owner_id)
    return render(request, "echofind.html", {"files_list": files_names})
