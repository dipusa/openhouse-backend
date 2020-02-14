from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import jwt

USER_TYPE_CHOICE = (
    (1, 'Student'),
    (2, 'Teacher')
)

SECRET_KEY = settings.SECRET_KEY


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=252)
    user_type = models.IntegerField(choices=USER_TYPE_CHOICE, default=1)


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    access_token = models.BinaryField()
    is_valid = models.BooleanField(default=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_auth_token(Klass, user):
        token_key = {}
        token_id = uuid.uuid4()
        access_token = jwt.encode({
            'user_id': str(user.id),
            'email': user.email,
            'token_id': str(token_id),
            'user_type': user.user_type,
        }, SECRET_KEY, algorithm='HS256')

        token_key["access_token"] = access_token

        Klass.objects.create(
            id=token_id,
            user=user,
            access_token=access_token,
        )
        return token_key

    @classmethod
    def validate_token(Klass, access_token):
        try:
            user_info = jwt.decode(
                access_token,
                SECRET_KEY,
                algorithms=['HS256']
            )
        except jwt.ExpiredSignatureError:
            return(False, {})
        except jwt.InvalidTokenError:
            return(False, {})
        try:
            token = Klass.objects.get(id=user_info["token_id"])
        except ObjectDoesNotExist:
            return(False, {})
        if token.is_valid:
            return(True, user_info)
        else:
            return(False, {})
