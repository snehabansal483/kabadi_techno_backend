from django.urls import path
#from .views import Customer_RegisterView, Customer_VerifyEmail, Customer_LoginAPIView, Customer_UpdateProfilePic ,Customer_RegenerateVerificationEmail, Customer_PasswordTokenCheckAPI, Customer_RequestPasswordResetEmail, Customer_SetNewPassAPIView, Customer_LogoutAPIView, Customer_Database_CheckerAPIView, Employee_RegisterView, Employee_RegenerateVerificationEmail, Employee_VerifyEmail, Employee_LoginAPIView, Employee_UpdateProfilePic, Employee_PasswordTokenCheckAPI, Employee_RequestPasswordResetEmail, Employee_SetNewPassAPIView, Employee_LogoutAPIView, Employee_Database_CheckerAPIView#, DealerRegistrationView
from .views import *
from .views import Employee_LogoutAPIView
from rest_framework_simplejwt.views import (TokenRefreshView,)

urlpatterns = [
    #####-----------------employee------------------######
    path('registration/employee/', Employee_RegisterView.as_view(), name = "employee-registration"),
    
    path('sign_in/employee/', Employee_LoginAPIView.as_view(), name = "employee-sign_in"),
    
    path('email-verify/employee/', Employee_VerifyEmail.as_view(), name = "employee-email-verify"),
    
    path('regenerate-verification-email/employee/', Employee_RegenerateVerificationEmail.as_view(), name = "employee-regenerate-verification-email"),
    
    path('update-profilepic/employee/<id>/', Employee_UpdateProfilePic.as_view(), name = "update-profilepic"),

    path('update-aadhar_card/employee/<id>/', Employee_Updateaadhar_card.as_view(), name = "update-aadhar_card"),
    
    path('update-attrs/employee/', Employee_UpdateAtrrs.as_view(), name = "update-attrs"),
    
    path('logout/employee/<token>', Employee_LogoutAPIView.as_view(), name = "employee-logout"),
    
    path('request-password-reset-email/employee/', Employee_RequestPasswordResetEmail.as_view(), name="employee-request-password-reset-email"),

    path('request-password-reset-email/employee/dealer/', Dealer_Employee_RequestPasswordResetEmail.as_view(), name="dealer_employee-request-password-reset-email"),
    
    path('password-reset-confirm/employee/<user_id>/<token>/', Employee_PasswordTokenCheckAPI.as_view(), name = "employee-password-reset-confirm"),
    
    path('password-reset-completion/employee/', Employee_SetNewPassAPIView.as_view(), name="employee-password-reset-completion"),
    
    path('database-checker/employee/<email>/', Employee_Database_CheckerAPIView.as_view(), name="employee-database-checker"),
    
    path('view-profile/employee/<token>', Employee_ProfileAPIView.as_view(), name="employee-database-checker"),

    #####-----------------EXTRAS------------------######
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    # path('dealers/register/', DealerRegistrationView.as_view(), name='dregister'),
]
