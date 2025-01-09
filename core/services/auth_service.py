from core.secrets import firebase_api_key
import requests
from firebase_admin import auth


class AuthService:
    register_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={firebase_api_key}"
    login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_api_key}"

    @staticmethod
    def send_request_to_firebase_auth(email: str, password: str, url: str):
        data = {"email": email,
                "password": password,
                "returnSecureToken": True}
        response = requests.post(url, data=data)
        return response

    @classmethod
    def register_user(cls, email: str, password: str):
        response = cls.send_request_to_firebase_auth(email, password, cls.register_url)
        return response

    @classmethod
    def authenticate_user(cls, email: str, password: str):
        response = cls.send_request_to_firebase_auth(email, password, cls.login_url)
        return response

    @staticmethod
    def logout_user(local_id: str, id_token: str):

        auth.revoke_refresh_tokens(local_id)

        try:
            auth.verify_id_token(id_token, check_revoked=True)
            print('Token is still valid (this should not happen)')
        except auth.RevokedIdTokenError:
            print('Token has been revoked successfully')
        except Exception as e:
            print(f'Error verifying token: {e}')

    @staticmethod
    def send_verification_email(id_token: str):
        api_key = firebase_api_key
        email_verification_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
        email_verification_data = {
            "requestType": "VERIFY_EMAIL",
            "idToken": id_token,
        }

        response = requests.post(email_verification_url, data=email_verification_data)
        return response

    @staticmethod
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
