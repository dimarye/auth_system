from django.db import migrations
from config.roles import (Role, BusinessElement)

def create_roles_and_rules(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    BusinessElement = apps.get_model('users', 'BusinessElement')
    AccessRoleRule = apps.get_model('users', 'AccessRoleRule')

    admin_role = Role.objects.create(name=Role.ADMIN.value)
    manager_role = Role.objects.create(name=Role.MANAGER.value)
    user_role = Role.objects.create(name=Role.USER.value)

    
    users_element = BusinessElement.objects.create(name=BusinessElement.USERS.value)
    orders_element = BusinessElement.objects.create(name=BusinessElement.ORDERS.value)
    products_element = BusinessElement.objects.create(name=BusinessElement.PRODUCTS.value)

    for element in [users_element, orders_element, products_element]:
        AccessRoleRule.objects.create(
            role=admin_role, element=element,
            read_permission=True, read_all_permission=True,
            create_permission=True,
            update_permission=True, update_all_permission=True,
            delete_permission=True, delete_all_permission=True
        )

    AccessRoleRule.objects.create(
        role=manager_role, element=orders_element,
        read_permission=True, read_all_permission=True,
        update_permission=True, update_all_permission=True
    )
    AccessRoleRule.objects.create(
        role=manager_role, element=products_element,
        read_permission=True, read_all_permission=True
    )

    AccessRoleRule.objects.create(
        role=user_role, element=users_element,
        read_permission=True
    )

def reverse_func(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    BusinessElement = apps.get_model('users', 'BusinessElement')
    AccessRoleRule = apps.get_model('users', 'AccessRoleRule')
    AccessRoleRule.objects.all().delete()
    BusinessElement.objects.all().delete()
    Role.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_businesselement_role_accessrolerule_user_role'),
    ]

    operations = [
        migrations.RunPython(create_roles_and_rules, reverse_func),
    ]
