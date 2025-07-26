
from django.urls import path
from .views import *

urlpatterns = [
    # path('', store, name = 'store'),
    path('add-price/', AddPrice.as_view(), name='add-price'),
    path('get-price/<dealer_id>/', GetPrice.as_view(), name='get-price'),
    path('update-price/', UpdatePrice.as_view(), name='update-price'),
    path('delete-price/', DeletePrice.as_view(), name='delete-price'),
    # path('category/<slug:category_slug>', store, name = 'products_by_category'),
    # path('category/<slug:category_slug>/<slug:product_slug>/', product_detail, name = 'product_detail'),
    # path('search/', search, name='search'),
    # path('submit_review/<int:product_id>/', submit_review, name='submit_review' )
    path('add_category_request/', RequestAddCategory.as_view(),name="add_category_request"),
    path('get_category_request/<dealer_id>/', GetRequestAddCategory.as_view(),name="get_category_request"),
    path('add_documents/', AddDocuments.as_view(),name="add_documents"),
    path('get_documents/<dealer_id>/', GetDocuments.as_view(),name="get_documents"),
    path('add_pincodes/', AddPincodes.as_view(),name="add_pincodes"),
    path('update_pincodes/', UpdatePincodes.as_view(),name="update_pincodes"),
    path('no_of_pincodes/<dealer_id>/', No_of_pincodes.as_view(),name="no_of_pincodes"),
    path('request_to_add_pincodes/', RequestToAddPincodes.as_view(),name="request_to_add_pincodes"),
    path('get_all_pincodes/<dealer_id>/', GetallPincodes.as_view(),name="get_all_pincodes"),
    path('search-subcategory/<pincode>/', SearchSubcategoryByPincode.as_view(), name="search-subcategory"),

]
