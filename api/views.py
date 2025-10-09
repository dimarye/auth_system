from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import authenticate

from drf_yasg import openapi
from .utils import (
    create_user_jwt, 
    get_authenticated_user,
    get_token_of_request,
)
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
)
from users.models import (
    User,
    UserToken,
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
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        operation_description="Register a new user account",
        request_body=RegisterSerializer,
        responses={
            201: success_response,
            400: error_response
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = serializer.save()
            
            return Response({
                'message': 'User registered successfully',
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer


    @swagger_auto_schema(
        operation_description="Authenticate user and get JWT token",
        request_body=LoginSerializer,
        responses={
            200: token_response,
            400: error_response,
            401: error_response,
            403: error_response
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {'detail': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'detail': 'User account is disabled'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, expires_at = create_user_jwt(user)
        
        # Store token in UserToken model
        UserToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

        return Response({
            'token': token,
            'expires_at': expires_at,
            'user': UserSerializer(user).data
        })

class LogoutView(APIView):
    def post(self, request):
        token = get_token_of_request(request)

        if not token:
            return Response(
                {'detail': 'Invalid token'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            UserToken.objects.filter(token=token).delete()

            return Response({'detail': 'Successfully logged out'})
        except Exception as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        if not request.user or request.user.is_anonymous:
            return Response(
                {'detail': 'Authentication credentials were not provided.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)

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
        
        user.deactivate()
        
        return Response(
            {"message": "Account deleted successfully"},
            status=status.HTTP_200_OK
        )