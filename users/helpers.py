from .models import (
    User,
    UserToken,
)

def get_user_by_token(token: str):
    user_token =  UserToken.objects.filter(token=token).first()

    if not user_token:
        return None

    return user_token.user 

def get_user_by_id(user_id: int):
    return User.objects.first(id=user_id)