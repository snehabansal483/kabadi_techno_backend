from venv import create
from sympy import im
from rest_framework.views import APIView
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response

from dealer_details.models import PriceList
from .serializers import *
from accounts.models import CustomerProfile as Customer, DealerProfile
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
def cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        request.session.create()
        cart_id = request.session.session_key
    return cart_id

# class Session_Manager(APIView):
#     def get(self, request, session_id):
#         cart =      

class AddToCart(APIView):
    serializer_class = AddToCartSerializer

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            price_list_id = request.data['price_list']
            customer_id = request.data['customer']

            customer = Customer.objects.get(id=customer_id)
            price_list = PriceList.objects.get(id=price_list_id)

            # Get or create the cart item (filter to avoid MultipleObjectsReturned)
            cart_item_qs = CartItem.objects.filter(price_list=price_list, customer=customer)

            if cart_item_qs.exists():
                cart_item = cart_item_qs.first()
                cart_item.quantity += 1
                cart_item.save()
                msg = "Quantity updated"
            else:
                cart_item = CartItem.objects.create(
                    price_list=price_list,
                    customer=customer,
                    quantity=1,
                    price=price_list.price  # Assuming `PriceList` has a `price` field
                )
                msg = "Item added to cart"

            return Response({
                'msg': msg,
                'quantity': cart_item.quantity
            }, status=status.HTTP_200_OK)


class DecreaseQuantity(APIView):
    serializer_class = DecreaseQuantitySerializer
    def post(self, request):
        serializer = DecreaseQuantitySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            price_list_id = request.data['price_list']
            customer_id = request.data['customer']
            customer = Customer.objects.get(id = customer_id)
            price_list = PriceList.objects.get(id = price_list_id)
            # is_cart_item_exists = CartItem.objects.filter(price_list = price_list, customer = customer).exists()
            if CartItem.objects.filter(price_list = price_list, customer = customer).exists():
                cart_item = CartItem.objects.get(price_list = price_list, customer = customer)
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                    return Response(serializer.data)
                else:
                    cart_item.delete()
                    return Response({'successful': 'Item Removed From Your Cart'}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({'unsuccessful': 'Cart Item Not Found'}, status=status.HTTP_404_NOT_FOUND)
        
class AddQuantity(APIView):
    serializer_class = AddQuantitySerializer

    def post(self, request):
        serializer = AddQuantitySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            price_list_id = request.data['price_list']
            customer_id = request.data['customer']
            addquantity = int(request.data['quantity'])

            customer = Customer.objects.get(id=customer_id)
            price_list = PriceList.objects.get(id=price_list_id)

            if CartItem.objects.filter(price_list=price_list, customer=customer).exists():
                cart_item = CartItem.objects.get(price_list=price_list, customer=customer)
                cart_item.quantity += addquantity
                cart_item.save()
            else:
                # Autofill CartItem fields from PriceList
                cart_item = CartItem.objects.create(
                    price_list=price_list,
                    quantity=addquantity,
                    customer=customer,
                    customer_name=customer.auth_id.username,
                    dealer_id=price_list.dealer.id,
                    subcategory_name=price_list.subcategory.sub_name,
                    subcategory_image=price_list.subcategory.sub_image,
                    GST=price_list.GST,
                    percentage=price_list.percentage,
                    unit=price_list.unit,
                    price=price_list.price,
                )
                cart_item.save()

            return Response({'msg': 'Quantity added/updated successfully', 'cart_item_id': cart_item.id})

class RemoveItem(APIView):
    serializer_class = RemoveItemSerializer
    def post(self, request):
        serializer = RemoveItemSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            price_list_id = request.data['price_list']
            customer_id = request.data['customer']
            customer = Customer.objects.get(id = customer_id)
            price_list = PriceList.objects.get(id = price_list_id)
            # is_cart_item_exists = CartItem.objects.filter(price_list = price_list, customer = customer).exists()
            if CartItem.objects.filter(price_list = price_list, customer = customer).exists():
                cart_item = CartItem.objects.get(price_list = price_list, customer = customer)
                cart_item.delete()
            else:
                return Response({'unsuccessful': 'Cart Item Not Found'} )
        return Response({'successful': 'Item Removed From Your Cart'}, status=status.HTTP_202_ACCEPTED)

class ViewCart(APIView):
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(id = customer_id)
            total = 0
            quantity = 0
            tax =  0
            grand_total = 0
            percentage_amt = 0

            try:
                cart_items = CartItem.objects.filter(customer = customer, is_active = True)
                for cart_item in cart_items:
                    total += (cart_item.price * cart_item.quantity)
                    tax += (cart_item.price * cart_item.quantity * cart_item.GST / 100)
                    percentage_amt += (cart_item.price * cart_item.quantity * cart_item.percentage / 100)
                    quantity += cart_item.quantity
                grand_total = total + tax + percentage_amt
                grand_total = round(grand_total, 2)
                context = {
                'total': total,
                'quantity': quantity,
                'tax': tax,
                'percentage_amt': percentage_amt,
                'grand_total': grand_total
                }
                serializer = ViewCartSerializer(cart_items, many = True)
                new_serializer_data = list(serializer.data)
                new_serializer_data.append(context)
                return Response(new_serializer_data)
            except ObjectDoesNotExist:
                return Response({'Empty': 'The Cart Is Empty'}, status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({'Not Found': 'There is no user with such id'}, status=status.HTTP_404_NOT_FOUND)


#frontend
class add_item(APIView):
    serializer_class = add_cart_item_serializer

    def get(self, request, id=None, format=None):
        if id is not None:
            try:
                obj = CartItem.objects.get(id=id)
                serializer = self.serializer_class(obj)
                return Response(serializer.data)
            except CartItem.DoesNotExist:
                return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            all_items = CartItem.objects.all()
            serializer = self.serializer_class(all_items, many=True)
            return Response(serializer.data)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                instance = serializer.save()
                return Response({'msg': 'Item has been added', 'item_id': instance.id}, status=201)
            except Exception as e:
                return Response({'error': str(e)}, status=500)
        return Response(serializer.errors, status=400)


    def patch(self, request, id, format=None):
        try:
            item = CartItem.objects.get(id=id)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = update_cart_item_serializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg': 'Cart item updated', 'id': id})
        return Response(serializer.errors, status=400)

  
    def delete(self, request, customer_id, dealer_id, format=None):
        try:
            items = CartItem.objects.filter(customer_id=customer_id, dealer_id=dealer_id)

            if not items.exists():
                return Response({'error': 'No cart items found for this customer and dealer'}, status=status.HTTP_404_NOT_FOUND)

            deleted_count = items.delete()[0]
            return Response({'msg': f'{deleted_count} cart item(s) deleted', 'customer_id': customer_id, 'dealer_id': dealer_id})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#patch request for item 
#delete request for item
#delete request for all items of customer and dealer jodi
class DeleteCartItem(APIView):
    def delete(self, request, id, format=None):
        try:
            item = CartItem.objects.get(id=id)
            item.delete()
            return Response({'msg': 'Cart item has been deleted', 'id': id})
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

class add_order(APIView):
    serializer_class = add_order_serializer

    def get(self, request, id=None, format=None):
        if id is not None:
            try:
                object = Cart_Order.objects.get(id=id)
            except Cart_Order.DoesNotExist:
                return Response({'error': 'Cart_Order with given ID not found'}, status=404)

            fields_with_null_or_blank = []
            fields_with_value = []
            cart_details = {}
            exempt = ['order_info', 'id', 'customer_id', 'dealer_id', 'status']

            for field in object._meta.get_fields():
                if field.name in exempt or not hasattr(object, field.name):
                    continue

                field_value = getattr(object, field.name)
                if field_value is None or field_value == '':
                    fields_with_null_or_blank.append(field.name)
                else:
                    try:
                        # Ensure value is a CartItem FK and valid integer
                        cart_item = CartItem.objects.get(id=field_value.id if hasattr(field_value, 'id') else field_value)
                        serializer = add_cart_item_serializer(cart_item)
                        cart_details[field.name] = [serializer.data]
                        fields_with_value.append(field.name)
                    except Exception as e:
                        print(f"Error processing field {field.name}: {e}")
                        continue

            return Response({
                "cart details": cart_details,
                "cart_order_id": object.id,
                "no_of_items": len(fields_with_value)
            })

        else:
            objects = Cart_Order.objects.all()
            serializer = get_order_serializer(objects, many=True)
            return Response(serializer.data)


    def post(self, request):
        serializer = add_order_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            customer_id = serializer.validated_data["customer_id"]
            dealer_id = serializer.validated_data["dealer_id"]

            cart_items = CartItem.objects.filter(
                customer=customer_id,
                dealer=dealer_id,
                is_active=True
            ).order_by('id')

            if not cart_items.exists():
                return Response({'msg': 'No items exist!'})

            try:
                cart_order = Cart_Order.objects.get(
                    customer_id=customer_id,
                    dealer_id=dealer_id,
                    status="False"
                )
                is_new = False
            except Cart_Order.DoesNotExist:
                cart_order = Cart_Order(
                    customer_id=customer_id,
                    dealer_id=dealer_id
                )
                is_new = True

            # Collect already assigned cart items
            existing_cart_items = set()
            for i in range(1, 11):  # Assuming max 10 slots
                item = getattr(cart_order, f'cart_item_{i}', None)
                if item:
                    existing_cart_items.add(item)

            # Find the next empty slot and assign new items
            added = 0
            for cart_item in cart_items:
                if cart_item in existing_cart_items:
                    continue  # Skip if already added

                for i in range(1, 11):
                    if getattr(cart_order, f'cart_item_{i}', None) is None:
                        setattr(cart_order, f'cart_item_{i}', cart_item)
                        added += 1
                        break  # go to next cart_item
                else:
                    # No empty slot left
                    break

            cart_order.save()

            msg = f"{added} item(s) " + ("added to cart" if is_new else "updated in cart")
            return Response({'msg': msg, 'cart_order_id': cart_order.id})
