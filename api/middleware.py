import jwt
from datetime import datetime, timezone
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser, User
from django.http import JsonResponse
from .utils import (
    get_token_of_request,
    decode_jwt,
)
from users.helpers import get_user_by_id


class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = get_token_of_request(request)

        if not token:
            request.user = AnonymousUser()
            return None

        try:
            payload = decode_jwt(token)
        except jwt.ExpiredSignatureError:
            return JsonResponse({'detail': 'Token expired'}, status=401)
        except jwt.InvalifdTokenError:
            return JsonResponse({'detail': 'Invalid token'}, status=401)

        user_id = payload.get('user_id')
        if not user_id:
            return JsonResponse({'detail': 'Invalid token payload'}, status=401)

        try:
            user = get_user_by_id(user_id)
        except User.DoesNotExist:
            return JsonResponse({'detail': 'User not found'}, status=401)

        if not user.is_active:
            return JsonResponse({'detail': 'User inactive'}, status=401)

        # Check UserToken
        from users.models import UserToken
        token_qs =  UserToken.objects.filter(user=user, token=token, expires_at__gt=datetime.now(tz=timezone.utc))
        if not token_qs.exists():
            return JsonResponse({'detail': 'Invalid token'}, status=401)

        request.user = user
        request.jwt_payload = payload

        return None
