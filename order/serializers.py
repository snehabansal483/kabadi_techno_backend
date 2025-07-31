from rest_framework import serializers
from .models import *

from rest_framework import serializers
  # Make sure to import your model

class TakeOrderDetailsSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        exclude = ('status', 'is_ordered', 'created_at', 'updated_at', 'order_total', 'tax', 'ip')

class OrderProductInitializationSerializer(serializers.ModelSerializer):
    # order_number = serializers.CharField(source = 'Order.order_number')
    # customer_id = serializers.CharField(source = 'Order.customer_id')
    
    class Meta:
        model = OrderProduct
        fields = ('order', 'order_number')

class ViewOrderSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField(read_only=True)
    taxes = serializers.SerializerMethodField(read_only=True)
    percentage = serializers.SerializerMethodField(read_only=True)

    def get_subtotal(self, obj):
        return obj.quantity * obj.price

    def get_taxes(self, obj):
        return obj.quantity * obj.GST * obj.price / 100
    
    def get_percentage(self, obj):
        return obj.quantity * obj.percentage * obj.price / 100
    
    class Meta:
        model = OrderProduct
        fields = ('order', 'subcategory_name', 'unit', 'quantity', 'price', 'subtotal', 'taxes', 'percentage','status')

class CancelOrderViaCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class CancelOrderViadealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class AcceptedOrderViadealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class GetAllOrdersCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class GetAllOrdersdealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = '__all__'

class GetOrderProducutsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = '__all__'

class GetAllOrdersofCustomerfordealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
class update_order_info_serializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ('customer_id','dealer_id','cart_order_id','status','ip','created_at', 'updated_at')

class order_confirm_serializer(serializers.ModelSerializer):
    subcategory_name = serializers.CharField(required=False)
    unit = serializers.CharField(required=False)
    quantity = serializers.IntegerField(required=False)
    price = serializers.FloatField(required=False)
    order = serializers.CharField(required=False)  # or appropriate field type

    
    class Meta:
        model = OrderProduct
        fields = '__all__'
