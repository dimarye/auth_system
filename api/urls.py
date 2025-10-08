from django.urls import path
from .views import RegisterView, LoginView, LogoutView, DeleteAccountView

urlpatterns = [
    path('public/register/', RegisterView.as_view(), name='register'),
    path('public/login/', LoginView.as_view(), name='login'),
    path('client/logout/', LogoutView.as_view(), name='logout'),
    path('client/me/delete/', DeleteAccountView.as_view(), name='delete-account'),
]