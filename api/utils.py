import jwt
import datetime
from django.conf import settings
from users.helpers import get_user_by_token


def create_user_jwt(user):
    """Create a JWT token for the given email."""
    expires_at = datetime.datetime.now() + datetime.timedelta(days=7)
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': expires_at,
        'iat': datetime.datetime.now(),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM), expires_at


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
