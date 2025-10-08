from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

# API Documentation Description
description = """
# JWT Authentication API

## API Endpoints

### Public Endpoints (No Authentication Required)
- **Register**: `POST /api/public/register/` - Create a new user account
- **Login**: `POST /api/public/login/` - Authenticate and receive a JWT token

### Protected Endpoints (Require JWT Authentication)
- **Logout**: `POST /api/client/logout/` - Invalidate the current JWT token
- **Delete Account**: `DELETE /api/client/me/delete/` - Permanently delete user account

## Authentication
This API uses JWT (JSON Web Tokens) for authentication. 

### How to Use:
1. **Register** a new user:
   ```
   POST /api/public/register/
   ```
   with JSON body:
   ```json
   {
     "email": "user@example.com",
     "password": "your_secure_password"
   }
   ```

2. **Login** to get your JWT token:
   ```
   POST /api/public/login/
   ```
   with JSON body:
   ```json
   {
     "email": "user@example.com",
     "password": "your_secure_password"
   }
   ```
   The response will include a JWT token in the `token` field.

3. **Access protected endpoints** by including the token in the `Authorization` header:
   ```
   Authorization: Bearer <your_jwt_token>
   ```

4. **Logout** to invalidate your current token:
   ```
   POST /api/client/logout/
   ```
   with the `Authorization` header.

5. **Delete your account** (requires authentication):
   ```
   DELETE /api/client/me/delete/
   ```
   with the `Authorization` header.

## Security
- Tokens expire after 1 hour
- Each token can only be used once after login
- Logging out invalidates the current token
"""

# Schema View Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="JWT Authentication API",
        default_version='v1.0.0',
        description=description,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(
            name="API Support",
            email="support@example.com",
            url="https://www.example.com/support"
        ),
        license=openapi.License(
            name="MIT License",
            url="https://opensource.org/licenses/MIT"
        ),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Swagger/OpenAPI Configuration
swagger_settings = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT token in the format: Bearer <token>'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'LOGOUT_URL': '/api/logout/',
    'DEFAULT_MODEL_RENDERING': 'example',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
