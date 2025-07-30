from django.urls import path
from . import views

urlpatterns = [
    #path('api/', views.dealerHome, name="dealer-home"),
    path('api/dealerlist/', views.dealerList, name="dealer-list"),
    # path('api/dealerdetail/<str:pk>', views.dealerDetail, name="dealer-detail"),
    path('api/dealeradd/', views.adddealer, name="dealer-create"),
    # path('api/dealerupdate/<str:pk>', views.dealerUpdate, name="dealer-update"),
    # path('api/dealerdelete/<str:pk>', views.dealerDelete, name="dealer-delete"), 
    path('api/getdealers/<str:pincode>/', views.getdealer, name="get-dealer-by-pincode"),
    #path('api/getdealers/', views.Getdealers.as_view(), name="get-dealer-by-lon-lat"),
    path('api/requestinquiry-get/<str:email>/', views.RequestInquiryGet.as_view(), name='requestinquiry-get'),
    path('api/requestinquiry-post/', views.RequestInquiryPost.as_view(), name='requestinquiry-post'),
    
]
