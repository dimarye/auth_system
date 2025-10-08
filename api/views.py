from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils import (
    User,
    USERS as _USERS,
    hash_password, 
    check_password,
    create_jwt, 
    decode_jwt, 
    get_user_by_email, 
    get_authenticated_user,
    get_token_of_request,
)

# Response schemas
error_response = openapi.Response(
    description='Error response',
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'error': openapi.Schema(type=openapi.TYPE_STRING)
        }
    )
)

success_response = openapi.Response(
    description='Success response',
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING)
        }
    )
)

token_response = openapi.Response(
    description='Authentication token',
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING)
        }
    )
)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user account",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format='password')
            },
        ),
        responses={
            201: success_response,
            400: error_response
        }
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if get_user_by_email(email):
            return Response(
                {"error": "Email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        _USERS.append(User.from_dict({
            "email": email,
            "password": hash_password(password),
            "is_active": True,
        }))
        
        return Response(
            {"message": "User created successfully"},
            status=status.HTTP_201_CREATED
        )

class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Authenticate user and get JWT token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format='password')
            },
        ),
        responses={
            200: token_response,
            400: error_response,
            401: error_response,
            403: error_response
        }
    )
    def post(self, request):
        data = request.data
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_user_by_email(email)
        if not user or not check_password(user.password, password):
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"error": "Account is deactivated"},
                status=status.HTTP_403_FORBIDDEN
            )

        token = create_jwt(email)
        
        user.add_token(token)
            
        return Response({"token": token})

class LogoutView(APIView):
    def post(self, request):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith(('Bearer ', 'Token ')):
            return Response(
                {"error": "No token provided"},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        token = get_token_of_request(request)
        payload = decode_jwt(token)
        
        if not payload:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        user = get_user_by_email(payload.get('email'))
        if not user:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        user.revoke_token(token)

        return Response(
            {"message": "Successfully logged out"},
            status=status.HTTP_200_OK
        )


class DeleteAccountView(APIView):
    @swagger_auto_schema(
        operation_description="Delete the authenticated user's account",
        responses={
            200: openapi.Response(
                description="Account deleted successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: error_response,
            400: error_response,
        },
        security=[{"Bearer": []}]
    )
    def delete(self, request):
        """
        Delete the authenticated user's account.
        Requires a valid JWT token in the Authorization header.
        """
        user = get_authenticated_user(request)
        if not user:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        _USERS[:] = [u for u in _USERS if u.email != user.email]
        
        return Response(
            {"message": "Account deleted successfully"},
            status=status.HTTP_200_OK
        )