from django.urls import path
from .views import *

urlpatterns = [
    path('add_to_cart/', AddToCart.as_view()),
    path('decrease_quantity/', DecreaseQuantity.as_view()),
    path('add_quantity/', AddQuantity.as_view()),
    path('remove_from_cart/', RemoveItem.as_view()),
    path('viewCart/<customer_id>/', ViewCart.as_view()),
    path('add_item/', add_item.as_view(),name="add_item"),
    path('add_item/<id>/', add_item.as_view(),name="add_item"),
    path('delete_cart_item/<int:id>/', DeleteCartItem.as_view(), name='delete_cart_item_by_id'),
    path('delete_cart_item/<int:customer_id>/<int:dealer_id>/', add_item.as_view(), name='delete_cart_item'),
    path('add_order/', add_order.as_view(),name="add_order"),
    path('add_order/<id>/', add_order.as_view(),name="add_order"),

]
