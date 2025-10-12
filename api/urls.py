from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProfileView
from .admin_views import AdminRoleView, AdminUserRoleView, AdminRuleView
from .manager_views import OrderListView, OrderDetailView

urlpatterns = [
    path('public/register/', RegisterView.as_view(), name='register'),
    path('public/login/', LoginView.as_view(), name='login'),
    path('client/logout/', LogoutView.as_view(), name='logout'),
    path('client/profile/', ProfileView.as_view(), name='profile'),
    path('admin/roles/', AdminRoleView.as_view(), name='role-list'),
    path('admin/rules/', AdminRuleView.as_view(), name='access-rule-list'),
    path('admin/rules/<int:rule_id>/', AdminRuleView.as_view(), name='access-rule-update'),
    path('admin/users/<int:user_id>/', AdminUserRoleView.as_view(), name='user-role-update'),
    path('manager/orders/', OrderListView.as_view(), name='order-list'),
    path('manager/orders/<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
]