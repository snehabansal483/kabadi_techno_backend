import datetime
from rest_framework.views import APIView
from rest_framework import generics, status, views, permissions 
from rest_framework.response import Response
from rest_framework.decorators import api_view
from carts.models import Cart_Order
from .serializers import *
from django.core.exceptions import ObjectDoesNotExist
###
# Create your views here.
class TakeOrderDetails(APIView):
    serializer_class = TakeOrderDetailsSerializer
    def post(self, request):
        serializer = TakeOrderDetailsSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            # Get customer_id from the validated data
            customer_id = serializer.validated_data.get('customer_id')
            
            if not customer_id:
                return Response({'error': 'Customer ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Find active cart items for this customer grouped by dealer
            cart_items = CartItem.objects.filter(customer_id=customer_id, is_active=True)
            
            if not cart_items.exists():
                return Response({'error': 'No active cart items found for this customer'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Group cart items by dealer_id
            dealers_items = {}
            for item in cart_items:
                dealer_id = item.dealer_id
                if dealer_id not in dealers_items:
                    dealers_items[dealer_id] = []
                dealers_items[dealer_id].append(item)
            
            created_orders = []
            
            # Create separate orders for each dealer
            for dealer_id, dealer_items in dealers_items.items():
                # Create order for this dealer
                order_data = serializer.validated_data.copy()
                order_data['dealer_id'] = dealer_id
                
                # Create the order instance
                Order = serializer.create(order_data)
                Order.ip = request.META.get('REMOTE_ADDR')
                Order.dealer_id = dealer_id
                
                # Generate order number
                yr = int(datetime.date.today().strftime('%Y'))
                dt = int(datetime.date.today().strftime('%d'))
                mt = int(datetime.date.today().strftime('%m'))
                d = datetime.date(yr, mt, dt)
                current_date = d.strftime("%Y%m%d")
                order_id = str(Order.id)
                if len(order_id) == 1:
                    order_number = current_date + 'KT00000' + str(order_id)
                elif len(order_id) == 2:
                    order_number = current_date + 'KT0000' + str(order_id)
                elif len(order_id) == 3:
                    order_number = current_date + 'KT000' + str(order_id)
                elif len(order_id) == 4:
                    order_number = current_date + 'KT00' + str(order_id)
                elif len(order_id) == 5:
                    order_number = current_date + 'KT0' + str(order_id)
                elif len(order_id) == 6:
                    order_number = current_date + 'KT' + str(order_id)
                
                Order.order_number = order_number
                Order.save()
                
                created_orders.append({
                    'order_id': Order.id,
                    'order_number': order_number,
                    'dealer_id': dealer_id,
                    'items_count': len(dealer_items)
                })
            
            return Response({
                'msg': f'Created {len(created_orders)} orders for {len(dealers_items)} dealers',
                'orders': created_orders
            })
class UpdateOrderDetails(APIView):
    def patch(self, request, id):
        try:
            order = Order.objects.get(id=id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TakeOrderDetailsSerializer(order, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"msg": "Order updated successfully", "order_id": id})

class DeleteOrderDetails(APIView):
    def delete(self, request, id):
        try:
            order = Order.objects.get(id=id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        order.delete()
        return Response({"msg": "Order deleted successfully", "order_id": id})

class OrderProductInitialization(APIView):
    serializer_class = OrderProductInitializationSerializer

    def post(self, request):
        serializer = OrderProductInitializationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                order_id = request.data['order']
                order_number = request.data['order_number']

                # Fetch the order instance
                order = Order.objects.get(id=order_id, is_ordered=False, order_number=order_number)
                customer = order.customer_id  # This is a CustomerProfile instance
                dealer_id = order.dealer_id   # Get the specific dealer for this order
                
                # Filter cart items by both customer and dealer for this specific order
                cart_items = CartItem.objects.filter(
                    customer_id=customer, 
                    dealer_id=dealer_id,  # Only items from this specific dealer
                    is_active=True
                )

                if not cart_items.exists():
                    return Response({'error': f'No active cart items found for this customer and dealer {dealer_id}'}, status=status.HTTP_404_NOT_FOUND)

                for cart_item in cart_items:
                    if not OrderProduct.objects.filter(order=order, cart_item=cart_item).exists():
                        order_product = OrderProduct.objects.create(
                            order=order,
                            cart_item=cart_item,
                            is_ordered=True,
                            status='Pending'
                        )
                        # The custom save() method will populate all fields from cart_item
                        # Ensure dealer_id is set correctly
                        if not order_product.dealer_id:
                            order_product.dealer_id = cart_item.dealer_id
                            order_product.save()

                # Mark only the cart items for this dealer as inactive
                cart_items.update(is_active=False)

                # ✅ Mark the main order as ordered
                order.is_ordered = True
                order.save()

                return Response({
                    'msg': 'Order initialized successfully',
                    'order_id': order.id,
                    'order_number': order.order_number,
                    'dealer_id': dealer_id,
                    'items_processed': cart_items.count()
                })

            except Order.DoesNotExist:
                return Response({'error': 'Order Not Found'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ViewOrder(APIView):
    def get(self, request, customer_id, order):
        try:
            # Get order instance
            ordeR = Order.objects.get(id=order, customer_id=customer_id)

            # Fetch order products related to this order and exclude cancelled ones
            order_products = OrderProduct.objects.filter(
                order=ordeR,
                is_ordered=True
            ).exclude(status__in=['Cancelled by Customer', 'Cancelled by dealer'])

            if not order_products.exists():
                return Response({'Empty': 'The Order Is Empty'}, status=status.HTTP_204_NO_CONTENT)

            total = 0
            tax = 0
            quantity = 0
            percentage_amt = 0

            for order_product in order_products:
                subtotal = order_product.price * order_product.quantity
                gst_amount = subtotal * (order_product.GST / 100)
                percentage_amount = subtotal * (order_product.percentage / 100)

                total += subtotal
                tax += gst_amount
                quantity += order_product.quantity
                percentage_amt += percentage_amount

            order_total = round(total + tax + percentage_amt, 2)

            # Update order totals
            ordeR.tax = round(tax, 2)
            ordeR.order_total = order_total
            ordeR.save()

            context = {
                'order_number': ordeR.order_number,
                'full_name': ordeR.full_name(),
                'phone': ordeR.phone,
                'email': ordeR.email,
                'full_address': ordeR.full_address(),
                'city': ordeR.city,
                'state': ordeR.state,
                'country': ordeR.country,
                'order_note': ordeR.order_note,
                'total': round(total, 2),
                'tax': round(tax, 2),
                'percentage_amt': round(percentage_amt, 2),
                'order_total': ordeR.order_total,
                'pickup_date': ordeR.pickup_date,
                'pickup_time': ordeR.pickup_time,
                'ip': ordeR.ip,
                'order_status': ordeR.status
            }

            # Include item-level status in serializer (update if needed)
            serializer = ViewOrderSerializer(order_products, many=True)
            new_serializer_data = list(serializer.data)
            new_serializer_data.append(context)

            return Response(new_serializer_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({'Empty': 'The Order Is Empty'}, status=status.HTTP_204_NO_CONTENT)

class CancelOrderViaCustomer(APIView):
    def get(self, request, customer_id, order_number):
        # Find all ordered products matching customer and order number
        order_products = OrderProduct.objects.filter(
            customer_id=customer_id,
            order_number=order_number,
            is_ordered=True
        )

        if order_products.exists():
            # Update status for all items in this order
            order_products.update(status='Cancelled by Customer')
            
            # Optionally, update the Order model as well (if status is stored there)
            try:
                order = Order.objects.get(customer_id=customer_id, order_number=order_number)
                order.status = 'Cancelled by Customer'
                order.save()
            except Order.DoesNotExist:
                pass  # skip if not present, or log warning
            
            return Response({'Cancelled': 'The Order is Cancelled by the Customer'}, status=status.HTTP_202_ACCEPTED)

        return Response({'Unsuccessful': 'There are no active orders with this order ID and customer ID'}, status=status.HTTP_202_ACCEPTED)
class CancelOrderViadealer(APIView):
    def get(self, request, dealer_id, order_number):
        # Look for order products that can be cancelled (not already cancelled)
        order_products = OrderProduct.objects.filter(
            dealer_id=dealer_id, 
            order_number=order_number, 
            is_ordered=True
        ).exclude(status__in=['Cancelled by dealer', 'Cancelled by Customer'])
        
        if order_products.exists():
            order_products.update(status='Cancelled by dealer')
            try:
                order = Order.objects.get(order_number=order_number)
                order.status = 'Cancelled'
                order.save()
            except Order.DoesNotExist:
                pass
            return Response({'Cancelled': 'The Order Is Cancelled by the dealer'}, status=status.HTTP_202_ACCEPTED)
        
        # Debug information to help identify the issue
        all_order_products = OrderProduct.objects.filter(order_number=order_number)
        if all_order_products.exists():
            dealer_ids = list(all_order_products.values_list('dealer_id', flat=True).distinct())
            statuses = list(all_order_products.values_list('status', flat=True).distinct())
            return Response({
                'Unsuccessful': 'There are no orders with this order Id and dealer id',
                'debug_info': {
                    'order_number': order_number,
                    'requested_dealer_id': dealer_id,
                    'available_dealer_ids': dealer_ids,
                    'available_statuses': statuses,
                    'total_products_with_order_number': all_order_products.count(),
                    'is_ordered_count': all_order_products.filter(is_ordered=True).count()
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'Unsuccessful': 'There are no orders with this order Id and dealer id'}, status=status.HTTP_404_NOT_FOUND)

class AcceptedOrderViadealer(APIView):
    def get(self, request, dealer_id, order_number):
        order_products = OrderProduct.objects.filter(
            dealer_id=dealer_id, 
            order_number=order_number, 
            is_ordered=True
        )
        
        if order_products.exists():
            order_products.update(status='Accepted')
            try:
                order = Order.objects.get(order_number=order_number)
                order.status = 'Confirmed'
                order.save()
            except Order.DoesNotExist:
                pass
            return Response({'Accepted': 'The Order Is Accepted by the dealer'}, status=status.HTTP_202_ACCEPTED)
        
        # Debug information to help identify the issue
        all_order_products = OrderProduct.objects.filter(order_number=order_number)
        if all_order_products.exists():
            dealer_ids = list(all_order_products.values_list('dealer_id', flat=True).distinct())
            return Response({
                'Unsuccessful': 'There are no orders with this order Id and dealer id',
                'debug_info': {
                    'order_number': order_number,
                    'requested_dealer_id': dealer_id,
                    'available_dealer_ids': dealer_ids,
                    'total_products_with_order_number': all_order_products.count()
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'Unsuccessful': 'There are no orders with this order Id and dealer id'}, status=status.HTTP_404_NOT_FOUND)

class GetAllOrdersCustomer(APIView):
    def get(self, request, customer_id):
        customer_id = customer_id
        order = Order.objects.filter(customer_id=customer_id)
        serializer = GetAllOrdersCustomerSerializer(order, many = True)
        return Response(serializer.data)

class GetAllOrdersdealer(APIView):
    def get(self, request, dealer_id):
        dealer_id = dealer_id
        order = OrderProduct.objects.filter(dealer_id=dealer_id)
        serializer = GetAllOrdersdealerSerializer(order, many = True)
        return Response(serializer.data)

class GetOrderProducuts(APIView):
    def get(self, request, order):
        order = order
        orderproduct = OrderProduct.objects.filter(order=order)
        serializer = GetOrderProducutsSerializer(orderproduct, many = True)
        return Response(serializer.data)

class GetAllOrdersofCustomerfordealer(APIView):
    def get(self, request, order_number):
        order_number = order_number
        order = Order.objects.filter(order_number=order_number)
        serializer = GetAllOrdersofCustomerfordealerSerializer(order, many = True)
        return Response(serializer.data)


#frontend
class order_info(APIView):
    serializer_class = TakeOrderDetailsSerializer
    def get(self, request,id=None,format=None):
        if id is not None:
            object = Order.objects.get(id=id)
            serializer = TakeOrderDetailsSerializer(object)
            return Response(serializer.data)
        else:
            objects=Order.objects.all()
            serializer = TakeOrderDetailsSerializer(objects,many=True)
            return Response(serializer.data)
        
    def post(self, request):
        serializer = TakeOrderDetailsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            cart_order_id = serializer.validated_data["cart_order_id"]
            customer_id = serializer.validated_data["customer_id"]
            first_name = serializer.validated_data["first_name"]
            last_name = serializer.validated_data["last_name"]
            phone = serializer.validated_data["phone"]
            email = serializer.validated_data["email"]
            address_line_1 = serializer.validated_data["address_line_1"]
            address_line_2 = serializer.validated_data["address_line_2"]
            city = serializer.validated_data["city"]
            state = serializer.validated_data["state"]
            country = serializer.validated_data["country"]
            pickup_date = serializer.validated_data["pickup_date"]
            pickup_time = serializer.validated_data["pickup_time"]
            order_note = serializer.validated_data["order_note"]
            ip = request.META.get("REMOTE_ADDR")

            # Get cart items grouped by dealer_id
            cart_items = CartItem.objects.filter(customer_id=customer_id, is_active=True)
            
            if not cart_items.exists():
                return Response({'error': 'No active cart items found for this customer'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Group cart items by dealer_id
            dealers_items = {}
            for item in cart_items:
                dealer_id = item.dealer_id
                if dealer_id not in dealers_items:
                    dealers_items[dealer_id] = []
                dealers_items[dealer_id].append(item)
            
            created_orders = []
            
            # Create separate orders for each dealer
            for dealer_id, dealer_items in dealers_items.items():
                save_object = Order(
                    cart_order_id=cart_order_id,
                    customer_id=customer_id,
                    dealer_id=dealer_id,  # Set specific dealer_id for this order
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    email=email,
                    address_line_1=address_line_1,
                    address_line_2=address_line_2,
                    city=city,
                    state=state,
                    country=country,
                    pickup_date=pickup_date,
                    pickup_time=pickup_time,
                    order_note=order_note,
                    ip=ip,
                )

                save_object.save()

                # Generate order_number
                import datetime
                today = datetime.date.today()
                current_date = today.strftime("%Y%m%d")
                order_id = str(save_object.id)
                padding = "KT" + "0" * (6 - len(order_id))
                order_number = f"{current_date}{padding}{order_id}"

                save_object.order_number = order_number
                save_object.save()
                
                created_orders.append({
                    'order_id': save_object.id,
                    'order_number': order_number,
                    'dealer_id': dealer_id,
                    'items_count': len(dealer_items)
                })

            return Response({
                'msg': f'Created {len(created_orders)} orders for {len(dealers_items)} dealers',
                'orders': created_orders
            })

    def patch(self, request,id,format=None):
        Order_info_object=Order.objects.get(id=id)
        serializer_object = update_order_info_serializer(Order_info_object,data=request.data,partial=True)
        if serializer_object.is_valid(raise_exception=True):
            serializer_object.save()
            return Response({'msg':'Order details updated','id':id})
        
    def delete(self, request,id,format=None):
        Order_info_object=Order.objects.get(id=id)
        customer_id=Order_info_object.customer_id
        dealer_id=Order_info_object.dealer_id  # Now we have dealer_id populated
        cart_order_id = Order_info_object.cart_order_id
        #Order_info_object.delete()
        Cart_Order.objects.filter(id=cart_order_id).delete()
        # Use both customer_id and dealer_id for more precise deletion
        if dealer_id:
            CartItem.objects.filter(customer_id=customer_id,dealer_id=dealer_id,status='False').delete()
        else:
            CartItem.objects.filter(customer_id=customer_id,status='False').delete()
        return Response({'msg':'all data related to order has been deleted','id':id})
    
class order_confirm(APIView):
    serializer_class = order_confirm_serializer

    def get(self, request,order_number=None,format=None):
        if order_number is not None:
            object = OrderProduct.objects.get(order_number=order_number)
            serializer = order_confirm_serializer(object)
            return Response(serializer.data)
        else:
            objects=OrderProduct.objects.all()
            serializer = order_confirm_serializer(objects,many=True)
            return Response(serializer.data)
        
    def post(self, request):
        serializer = order_confirm_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            order_id = serializer.validated_data["order"]
            customer_id = serializer.validated_data["customer_id"]
            dealer_id = serializer.validated_data["dealer_id"]

            # Get related cart items
            cart_items = CartItem.objects.filter(
                customer_id=customer_id,
                dealer_id=dealer_id,
                is_active=True
            )

            if not cart_items.exists():
                return Response({"error": "No active cart items found for this customer and dealer."})

            total_cart_items = cart_items.count()
            total_amount = sum([item.quantity * item.price for item in cart_items])

            # Generate base order number
            today = datetime.date.today()
            current_date = today.strftime("%Y%m%d")

            order_number_prefix = current_date + "KT"

            created_products = []
            for item in cart_items:
                # Create OrderProduct from each CartItem
                order_product = OrderProduct(
                    order_id=order_id,
                    cart_item=item
                )
                order_product.save()  # This will populate all fields via your custom save()

                # Generate order_number using ID
                op_id = order_product.id
                padded_id = str(op_id).rjust(6, "0")  # e.g., 12 => 000012
                full_order_number = order_number_prefix + padded_id

                order_product.order_number = full_order_number
                order_product.save()

                created_products.append({
                    "id": op_id,
                    "order_number": full_order_number,
                    "subcategory_name": order_product.subcategory_name,
                    "quantity": order_product.quantity
                })

                # Deactivate the cart item
                item.is_active = False
                item.save()

            return Response({
                "msg": "Order has been confirmed",
                "total_items": total_cart_items,
                "total_amount": total_amount,
                "orders": created_products
            })
@api_view(['GET'])
def confirm_orders(request, id):
    path = request.path.lower()
    
    if 'customer' in path:
        orders = OrderProduct.objects.filter(customer_id=id)
    elif 'dealer' in path:
        orders = OrderProduct.objects.filter(dealer_id=id)
    else:
        return Response({"msg": "Please specify 'customer' or 'dealer' in the URL."})

    if not orders.exists():
        return Response({"msg": "No orders found for the given ID."})

    serializer = order_confirm_serializer(orders, many=True)
    return Response(serializer.data)
