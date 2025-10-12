from rest_framework import serializers
from .models import Order
from rest_framework.serializers import ListSerializer

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'title', 'amount', 'status', 
            'order_date', 'customer_email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_date', 'created_at', 'updated_at']

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
        
    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError("Invalid status")
        return value


class BulkOrderSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        orders = [Order(**item) for item in validated_data]
        return Order.objects.bulk_create(orders)
    
    def to_representation(self, data):
        return OrderSerializer(data, many=True).data


class OrderCreateBulkSerializer(OrderSerializer):
    class Meta(OrderSerializer.Meta):
        list_serializer_class = BulkOrderSerializer
