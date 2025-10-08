import jwt
import datetime
import hashlib
from django.conf import settings
from datetime import timezone

class User:
    def __init__(self, email, password, is_active=True, tokens=None):
        self.email = email
        self.password = password
        self.is_active = is_active
        self.tokens = tokens if tokens else []

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        return cls(
            email=data['email'],
            password=data['password'],
            is_active=data.get('is_active', True),
            tokens=data.get('tokens', [])
        )

    def add_token(self, token):
        self.tokens.append(token)

    def revoke_token(self, token):
        if token in self.get_tokens():
            self.tokens.remove(token)

    def get_tokens(self) -> list[str]:
        return self.tokens

    def __str__(self):
        return self.email

USERS = []

def hash_password(password) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), settings.SALT.encode('utf-8'), 100000).hex()

def check_password(stored_password: str, provided_password: str) -> bool:
    if not stored_password or not provided_password:
        return False

    return stored_password == hash_password(provided_password)

def create_jwt(email):
    """Create a JWT token for the given email."""
    payload = {
        'email': email,
        'exp': datetime.datetime.now(timezone.utc) + datetime.timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME),
        'iat': datetime.datetime.now(timezone.utc)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_jwt(token):
    """Decode and verify a JWT token."""

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_user_by_email(email):
    """Get user by email from the in-memory storage."""
    for user in USERS:
        if user.email == email:
            return user
    return None

def get_token_of_request(request):
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith(('Bearer ', 'Token ')):
        return auth_header.split(' ')[1]
    return None

def get_authenticated_user(request):
    """Get authenticated user from request headers."""

    token = get_token_of_request(request)
    if not token:
        return None
        
    payload = decode_jwt(token)
    if not payload:
        return None
        
    user = get_user_by_email(payload.get('email'))
    if not user or not user.is_active:
        return None
        
    if token not in user.tokens:
        return None
        
    return user