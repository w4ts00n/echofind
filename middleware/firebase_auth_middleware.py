from django.http import JsonResponse
from firebase_admin import auth
import re


class FirebaseUser:
    def __init__(self, decoded_token):
        self.uid = decoded_token.get('uid')
        self.email = decoded_token.get('email')
        self.is_active = True


class FirebaseAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [
            re.compile('^/login/$'),
            re.compile('^/register/$'),
            re.compile('^/$'),
        ]

    def __call__(self, request):
        if any(url.match(request.path) for url in self.exempt_urls):
            return self.get_response(request)

        auth_header = request.META.get('HTTP_AUTHORIZATION', None)

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split('Bearer ')[1]
            try:
                decoded_token = auth.verify_id_token(token)
                user = FirebaseUser(decoded_token)

                request.user = user
            except Exception as e:
                return JsonResponse({'message': 'Invalid token!'}, status=401)
        else:
            return JsonResponse({'message': 'Token is missing or invalid!'}, status=401)

        response = self.get_response(request)
        return response
