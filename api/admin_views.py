from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import AccessRoleRule, Role, User
from .admin_serializers import RoleSerializer, UserRoleUpdateSerializer, AccessRuleUpdateSerializer
from .utils import has_permission
from config.roles import BusinessElement

class AdminRoleView(APIView):
    """
    API endpoint that allows admin to view all roles.
    Requires admin permissions.
    """
    @has_permission(BusinessElement.ROLES.value, 'read')
    def get(self, request):
        roles = Role.objects.all().order_by('id')
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class AdminRuleView(APIView):
    @has_permission(BusinessElement.RULES.value, 'read')
    def get(self, request):
        rules = AccessRoleRule.objects.all().order_by('id')
        serializer = AccessRuleUpdateSerializer(rules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @has_permission(BusinessElement.RULES.value, 'update')
    def patch(self, request, rule_id):
        try:
            rule = AccessRoleRule.objects.select_related('role', 'element').get(id=rule_id)
        except AccessRoleRule.DoesNotExist:
            return Response(
                {'detail': 'Access rule not found'}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = AccessRuleUpdateSerializer(
            rule,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AdminUserRoleView(APIView):
    @has_permission(BusinessElement.USERS.value, 'update')
    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        serializer = UserRoleUpdateSerializer(
            user, 
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    

        
