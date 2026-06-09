import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from ninja.security import HttpBearer
from ninja.errors import HttpError


User = get_user_model()


class JWTAuth(HttpBearer):
    def authenticate(self, request, token: str):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload.get("user_id"))
            return user
        except (jwt.ExpiredSignatureError, jwt.DecodeError, User.DoesNotExist):
            raise HttpError(401, "Недійсний або прострочений токен")


jwt_auth = JWTAuth()
