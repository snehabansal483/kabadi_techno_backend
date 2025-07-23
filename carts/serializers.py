from rest_framework import serializers
from .models import CartItem, Cart_Order


# ------------------ Cart Item Serializers ------------------
class add_cart_item_serializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True)

    class Meta:

        model = CartItem
        fields = '__all__'

    def create(self, validated_data):
        price_list = validated_data.get('price_list')

        if price_list:
            # Autofill fields from price_list
            validated_data['subcategory_name'] = price_list.subcategory_name
            validated_data['subcategory_image'] = price_list.subcategory_image
            validated_data['GST'] = price_list.GST
            validated_data['unit'] = price_list.unit
            validated_data['percentage'] = price_list.percentage
            validated_data['price'] = price_list.price
            validated_data['dealer'] = price_list.dealer

        # customer_name (from customer.auth_id.username)
        customer = validated_data.get('customer')
        if customer and hasattr(customer, 'auth_id'):
            validated_data['customer_name'] = customer.auth_id.username

        return super().create(validated_data)

class update_cart_item_serializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        exclude = ('customer', 'dealer_id')  # corrected field


class AddToCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('customer', 'price_list')


class DecreaseQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('customer', 'price_list')


class AddQuantitySerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ('customer', 'price_list', 'quantity')


class RemoveItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('customer', 'price_list')


class ViewCartSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()
    taxes = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()
    pincode = serializers.SerializerMethodField()
    kt_id = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            'id',
            'subcategory_name',
            'dealer_id',
            'kt_id',
            'price_list',
            'subcategory_image',
            'unit',
            'quantity',
            'price',
            'pincode',
            'subtotal',
            'taxes',
            'percentage'
        )

    def get_subtotal(self, obj):
        return round(obj.quantity * obj.price, 2)

    def get_taxes(self, obj):
        return round(obj.quantity * obj.GST * obj.price / 100, 2)

    def get_percentage(self, obj):
        return round(obj.quantity * obj.percentage * obj.price / 100, 2)

    def get_pincode(self, obj):
        return getattr(obj.price_list, 'pincode', None)

    def get_kt_id(self, obj):
        return getattr(getattr(obj.price_list, 'dealer', None), 'kt_id', None)


# ------------------ Cart Order Serializers ------------------

# Used to add order with just customer & dealer info
class add_order_serializer(serializers.ModelSerializer):
    class Meta:
        model = Cart_Order
        fields = ['customer_id', 'dealer_id']


# Full nested view of Cart_Order with cart items populated
class get_order_serializer(serializers.ModelSerializer):
    cart_item_1 = add_cart_item_serializer()
    cart_item_2 = add_cart_item_serializer()
    cart_item_3 = add_cart_item_serializer()
    cart_item_4 = add_cart_item_serializer()
    cart_item_5 = add_cart_item_serializer()
    cart_item_6 = add_cart_item_serializer()
    cart_item_7 = add_cart_item_serializer()
    cart_item_8 = add_cart_item_serializer()
    cart_item_9 = add_cart_item_serializer()
    cart_item_10 = add_cart_item_serializer()

    class Meta:
        model = Cart_Order
        fields = '__all__'
