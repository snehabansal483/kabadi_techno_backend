from django.urls import path
# from cvm.viewsets import get_user_detail_for_cvm, cvm_details, cvm_registration, check_qrcode_is_valid, \
#     generate_qr_code, check_cvm_volume, cvm_find, unload_scrap
from .views import *

urlpatterns = [

    # Updated REgistration and Sign in apis by HARSHIT ------------

    path('crud_cvm_register/', CvmRegistrationApi.as_view({'post': 'create','get':'list'})),
    
    path('update_cvm/<uid>/',UpdateCVM.as_view()),
    path('sign_cvm/',send_otp,), # post
    path('enter_otp/',otp_checker), # post
    path('cvm_list/',CvmList.as_view()), # GET
    path('update_cvm_weights/<uid>/',CvmWeightApi.as_view()), # get put


    path('get_cvm_cart/<cvm_uid>/',get_carts_in_cvm), 
    path('post_cvm_cart/',post_cart_in_cvm), # accpet cart details by post request

    path('get_cvm_order/<cvm_uid>/',get_orders_in_cvm), # accpet dealer_email by get request
    path('post_cvm_order/',OrderPostView.as_view()), # accpet order details by post request
    
    
    path('crud_orders/<order_id>/',orderapi.as_view()), # get,patch,delete

    path('get_details/<id>/',get_details), # Order Cart
    #          -------------------------------------------------------------------

    path('cvm_nearby/<pincode>/', GetCvms.as_view()),

    path('generate_qrcode/<str:machine_id>/', GenerateQRCode.as_view()),

    path('check_qr_code/', CheckQRCodeIsValid.as_view()),

    # path('check_qr_code_customer/', check_qrcode_is_valid.CheckQRCodeIsValidCustomer.as_view()),
    path('check_pass_code/', CheckDealerPassCode.as_view()),

    path('get_user_detail/<int:qrcode_id>/', GetUserDetailForCVM.as_view()),

    # path('get_user_detail_customer/<int:qrcode_id>/', get_user_detail_for_cvm.GetUserDetailForCVMCustomer.as_view()),
    path('update_cvm_details/', CVMDetails.as_view()),

    path('check_volume/<uid>/', CheckCvmVolume.as_view()),

    path('get_spatial_cvm/', GetCvmVolume.as_view()),

    path('post_unload_scrap/', PostUnlodScrap.as_view()),
    
    path('get_unload_scrap/', GetUnloadScrap.as_view()),

    # path('scrap/unload_scrap/', unload_scrap.UnloadScrapCvmApi.as_view({'post': 'create'}))
]
 