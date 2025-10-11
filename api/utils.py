import jwt
import datetime
from django.conf import settings
from functools import wraps
from django.http import JsonResponse
from users.helpers import get_user_by_token
from users.models import AccessRoleRule, BusinessElement


def create_user_jwt(user):
    """Create a JWT token for the given email."""
    expires_at = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME)
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': expires_at,
        'iat': datetime.datetime.now(tz=datetime.timezone.utc),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM), expires_at


def decode_jwt(token):
    """Decode and verify a JWT token."""

    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def get_token_of_request(request):
    auth = request.headers.get('Authorization', '')

    if not auth:
        return None
    
    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
        
    return parts[1]

def get_authenticated_user(request):
    """Get authenticated user from request headers."""

    token = get_token_of_request(request)
    if not token:
        return None
    
    return get_user_by_token(token)


def has_permission(element_name, action):
    """Decorator to check RBAC permissions based on user's role.
    Usage:
        @has_permission('users', 'read')
        def view(request, ...):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            request = None
            if args:
                if hasattr(args[0], 'META'):
                    request = args[0]
                elif len(args) >= 2 and hasattr(args[1], 'META'):
                    request = args[1]
            
            if request is None:
                return JsonResponse({'detail': 'Unauthorized'}, status=401)
            user = request.user
            if not user or not getattr(user, 'is_authenticated', False):
                return JsonResponse({'detail': 'Unauthorized'}, status=401)
            if not getattr(user, 'role_id', None):
                return JsonResponse({'detail': 'Forbidden'}, status=403)
            try:
                element = BusinessElement.objects.get(name=element_name)
                rule = AccessRoleRule.objects.get(role=user.role, element=element)
            except (BusinessElement.DoesNotExist, AccessRoleRule.DoesNotExist):
                return JsonResponse({'detail': 'Forbidden'}, status=403)

            permission_field = f"{action}_permission"
            if not hasattr(rule, permission_field) or not getattr(rule, permission_field):
                return JsonResponse({'detail': 'Forbidden'}, status=403)

            return view_func(*args, **kwargs)

        return wrapper
    return decorator
