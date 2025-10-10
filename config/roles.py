from enum import Enum

class Role(str, Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    USER = 'user'

class BusinessElement(str, Enum):
    USERS = 'users'
    ORDERS = 'orders'
    PRODUCTS = 'products'