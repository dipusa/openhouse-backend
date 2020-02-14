from rest_framework import authentication
from rest_framework import exceptions
from user_management.models import Token


class BaseJWTAuthentication(authentication.BaseAuthentication):
    def get_user_by_token(self, token, request):
        access_token = token["access_token"]

        is_valid, user_info = Token.validate_token(access_token)
        if not is_valid:
            #raise exceptions.AuthenticationFailed()
            raise exceptions.NotAuthenticated('access token expired')
        return (user_info, token)


class JWTAuthentication(BaseJWTAuthentication):
    def authenticate(self, request):
        token = {}
        access_token = request.META.get('HTTP_X_ACCESS_TOKEN', None)
        if access_token is None:
            raise exceptions.NotAuthenticated('access token not supplied')
        token = {
            'access_token': access_token,
        }

        return self.get_user_by_token(token, request)
