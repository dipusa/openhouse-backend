from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import Token
from rest_framework import status
from rest_framework.response import Response
from .forms import LoginForm

User = get_user_model()


class LoginView(APIView):
    def post(self, request, format=None):
        form = LoginForm(request.data)
        if form.is_valid():
            tokens_and_user_detail = Token.generate_auth_token(form.user)
            # tokens_and_user_detail['user_id'] = str(form.user.id)
            tokens_and_user_detail['username'] = form.user.username
            tokens_and_user_detail['user_type'] = form.user.user_type
            return Response(tokens_and_user_detail)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)