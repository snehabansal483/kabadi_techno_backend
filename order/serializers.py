from rest_framework import serializers
from .models import *

from rest_framework import serializers
  # Make sure to import your model

class TakeOrderDetailsSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(read_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Order
        exclude = ('dealer_id', 'status', 'is_ordered', 'created_at', 'updated_at', 'order_total', 'tax', 'ip')

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
    subcategory_name = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    total_cart_items = serializers.SerializerMethodField()
    order_total = serializers.SerializerMethodField()
    
    def get_subcategory_name(self, obj):
        """Get all subcategory names from related order products"""
        order_products = OrderProduct.objects.filter(order=obj, is_ordered=True)
        return [op.subcategory_name for op in order_products]
    
    def get_price(self, obj):
        """Get all prices from related order products"""
        order_products = OrderProduct.objects.filter(order=obj, is_ordered=True)
        return [op.price for op in order_products]
    
    def get_total_cart_items(self, obj):
        """Get total cart items count from related order products"""
        order_products = OrderProduct.objects.filter(order=obj, is_ordered=True)
        return sum(op.total_cart_items for op in order_products)
    
    def get_order_total(self, obj):
        """Calculate total order amount from all order products"""
        order_products = OrderProduct.objects.filter(order=obj, is_ordered=True)
        total = 0
        for op in order_products:
            # Calculate subtotal for each product
            subtotal = op.quantity * op.price
            # Add GST
            gst_amount = subtotal * (op.GST / 100)
            # Add percentage
            percentage_amount = subtotal * (op.percentage / 100)
            # Add to total
            total += subtotal + gst_amount + percentage_amount
        return round(total, 2)
    
    class Meta:
        model = Order
        fields = '__all__'

class GetAllOrdersdealerSerializer(serializers.ModelSerializer):
    subcategory_names = serializers.SerializerMethodField()
    prices = serializers.SerializerMethodField()
    quantities = serializers.SerializerMethodField()
    total_cart_items = serializers.SerializerMethodField()
    order_total = serializers.SerializerMethodField()
    
    def get_subcategory_names(self, obj):
        """Get all subcategory names for the same order_number"""
        order_products = OrderProduct.objects.filter(
            order_number=obj.order_number, 
            dealer_id=obj.dealer_id,
            is_ordered=True
        )
        return [op.subcategory_name for op in order_products]
    
    def get_prices(self, obj):
        """Get all prices for the same order_number"""
        order_products = OrderProduct.objects.filter(
            order_number=obj.order_number, 
            dealer_id=obj.dealer_id,
            is_ordered=True
        )
        return [op.price for op in order_products]
    
    def get_quantities(self, obj):
        """Get all quantities for the same order_number"""
        order_products = OrderProduct.objects.filter(
            order_number=obj.order_number, 
            dealer_id=obj.dealer_id,
            is_ordered=True
        )
        return [op.quantity for op in order_products]
    
    def get_total_cart_items(self, obj):
        """Get total cart items count for the same order_number"""
        order_products = OrderProduct.objects.filter(
            order_number=obj.order_number, 
            dealer_id=obj.dealer_id,
            is_ordered=True
        )
        return sum(op.total_cart_items for op in order_products)
    
    def get_order_total(self, obj):
        """Calculate total order amount for the same order_number"""
        order_products = OrderProduct.objects.filter(
            order_number=obj.order_number, 
            dealer_id=obj.dealer_id,
            is_ordered=True
        )
        total = 0
        for op in order_products:
            # Calculate subtotal for each product
            subtotal = op.quantity * op.price
            # Add GST
            gst_amount = subtotal * (op.GST / 100)
            # Add percentage
            percentage_amount = subtotal * (op.percentage / 100)
            # Add to total
            total += subtotal + gst_amount + percentage_amount
        return round(total, 2)
    
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
