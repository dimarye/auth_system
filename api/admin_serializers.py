from rest_framework import serializers
from users.models import Role, User, AccessRoleRule

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']
        read_only_fields = ['id']

class UserRoleUpdateSerializer(serializers.ModelSerializer):
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='role',
        required=True,
        write_only=True,
    )
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'role_id']
        read_only_fields = ['id', 'username', 'role']
        extra_kwargs = {
            'role_id': {'write_only': True}
        
        }
    
    def update(self, instance, validated_data):
        instance.role = validated_data.get('role', instance.role)
        instance.save()
        return instance


class AccessRuleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRoleRule
        fields = [
            'id', 'role', 'element', 
            'read_permission', 'read_all_permission',
            'create_permission',
            'update_permission', 'update_all_permission',
            'delete_permission', 'delete_all_permission'
        ]
        read_only_fields = ['id', 'role', 'element']

    def validate(self, data):
        permission_fields = [
            'read_permission', 'read_all_permission',
            'create_permission', 'update_permission',
            'update_all_permission', 'delete_permission',
            'delete_all_permission'
        ]
        
        if not any(field in data for field in permission_fields):
            raise serializers.ValidationError('At least one permission field must be provided.')
        
        return data

    def update(self, instance, validated_data):
        for field in [
            'read_permission', 'read_all_permission',
            'create_permission', 'update_permission',
            'update_all_permission', 'delete_permission',
            'delete_all_permission'
        ]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        
        instance.save()
        return instance
            