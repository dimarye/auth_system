from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSetMixin
from .utils import has_permission
from config.roles import BusinessElement
from .models import Order
from .manager_serializers import OrderSerializer, OrderStatusUpdateSerializer, OrderCreateBulkSerializer


class OrderListView(APIView, ViewSetMixin):
    @has_permission(BusinessElement.ORDERS.value, 'read')
    def get(self, request):
        orders = Order.objects.all().order_by('-created_at')
        if not orders.exists():
            return Response(
                {'message': 'No orders found', 'results': []},
                status=status.HTTP_200_OK
            )
        serializer = OrderSerializer(orders, many=True)
        return Response({
            'message': 'Orders retrieved successfully',
            'count': len(serializer.data),
            'results': serializer.data
        }, status=status.HTTP_200_OK)

    @has_permission(BusinessElement.ORDERS.value, 'create')
    def post(self, request):
        if isinstance(request.data, list):
            return self._bulk_create(request)
        else:
            return self._single_create(request)
            
    @has_permission(BusinessElement.ORDERS.value, 'delete')
    def delete(self, request):
        if 'ids' in request.data and isinstance(request.data['ids'], list):
            return self._bulk_delete(request)
        return Response(
            {'error': 'No order IDs provided for bulk delete. Use {"ids": [1, 2, 3]} format'},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    def _bulk_delete(self, request):
        order_ids = request.data['ids']
        if not order_ids:
            return Response(
                {'error': 'No order IDs provided for deletion'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        existing_orders = Order.objects.filter(id__in=order_ids)
        existing_ids = set(existing_orders.values_list('id', flat=True))
        non_existing_ids = set(order_ids) - existing_ids
        
        if non_existing_ids:
            return Response(
                {
                    'error': 'Some orders not found',
                    'non_existing_ids': list(non_existing_ids)
                },
                status=status.HTTP_404_NOT_FOUND
            )
            
        with transaction.atomic():
            deleted_count, _ = existing_orders.delete()
            
        return Response(
            {
                'message': f'Successfully deleted {deleted_count} orders',
                'deleted_ids': order_ids
            },
            status=status.HTTP_200_OK
        )
    
    def _single_create(self, request):
        data = request.data.copy()
        data['created_by'] = request.user.id
        
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _bulk_create(self, request):
        orders_data = []
        for order_data in request.data:
            order_data = order_data.copy()
            order_data['created_by'] = request.user.id
            orders_data.append(order_data)
        
        serializer = OrderCreateBulkSerializer(data=orders_data, many=True)
        if serializer.is_valid():
            orders = serializer.save()
            return Response(
                {
                    'message': f'Successfully created {len(orders)} orders',
                    'results': OrderSerializer(orders, many=True).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(APIView):
    def get_order(self, order_id):
        return get_object_or_404(Order, id=order_id)

    @has_permission(BusinessElement.ORDERS.value, 'read')
    def get(self, request, order_id):
        order = self.get_order(order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @has_permission(BusinessElement.ORDERS.value, 'delete')
    def delete(self, request, order_id):
        try:
            order = self.get_order(order_id)
            order.delete()
            return Response(
                {'success': True, 'message': 'Order deleted successfully'},
                status=status.HTTP_200_OK
            )
        except Http404:
            return Response(
                {'success': False, 'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @has_permission(BusinessElement.ORDERS.value, 'update')
    def patch(self, request, order_id):
        order = self.get_order(order_id)
        
        if 'status' in request.data:
            serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        else:
            serializer = OrderSerializer(order, data=request.data, partial=True)
            
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)