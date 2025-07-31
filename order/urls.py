from django.urls import path
from .views import *
from .views import TakeOrderDetails, UpdateOrderDetails, DeleteOrderDetails

urlpatterns = [
    path('take-order-details/', TakeOrderDetails.as_view(), name="take-order-details"),
    path('take-order-details/update/<int:id>/', UpdateOrderDetails.as_view(), name="update-order-details"),
    path('take-order-details/delete/<int:id>/', DeleteOrderDetails.as_view(), name="delete-order-details"),
    path('order-product-initialization/', OrderProductInitialization.as_view(), name="order-product-initialization"),
    path('view-order-details/<int:customer_id>/<int:order>/', ViewOrder.as_view(), name="view-order-details"),
    path('cancel-order-via-customer/<int:customer_id>/<str:order_number>/', CancelOrderViaCustomer.as_view(), name='cancel-order'),
    path('cancel-order-via-dealer/<int:dealer_id>/<str:order_number>/', CancelOrderViadealer.as_view(), name="cancel-order-via-dealer"),
    path('accepted-order-via-dealer/<int:dealer_id>/<str:order_number>/', AcceptedOrderViadealer.as_view(), name="accepted-order-via-dealer"),
    path('get-all-orders-customer/<int:customer_id>/', GetAllOrdersCustomer.as_view(), name="get-all-orders-customer"),
    path('get-all-orders-dealer/<int:dealer_id>/', GetAllOrdersdealer.as_view(), name="get-all-orders-dealer"),
    path('get-order-product/<int:order>/', GetOrderProducuts.as_view(), name="get-order-product"),
    path('get-all-orders-of-customer-for-dealer/<str:order_number>/', GetAllOrdersofCustomerfordealer.as_view(), name="get-all-orders-of-customer-for-dealer"),
    path('order_info/', order_info.as_view(), name="order_info"),
    path('order_info/<id>/', order_info.as_view(), name="order_info"),
    path('order_confirm/', order_confirm.as_view(), name="order_confirm"),
    path('order_confirm/<order_number>/', order_confirm.as_view(), name="order_confirm"),
    path('order_confirm/customer/<int:id>/', confirm_orders),
    path('order_confirm/dealer/<int:id>/', confirm_orders),
]
