from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProfileView

urlpatterns = [
    path('public/register/', RegisterView.as_view(), name='register'),
    path('public/login/', LoginView.as_view(), name='login'),
    path('client/logout/', LogoutView.as_view(), name='logout'),
    path('client/profile/', ProfileView.as_view(), name='profile'),
]