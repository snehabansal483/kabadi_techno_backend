from django.urls import path
from .views import *

urlpatterns = [
    path('post-dgkt/', PostDGKT.as_view(), name="post-dgkt"),
    path('check-aadhar-otp/', CheckAadharOtp.as_view(), name="check-aadhar-otp"),
    path('get-dgkt/<id>/', GetDGKT.as_view(), name="get-dgkt"),
    path('update-dgkt/', UpdateDGKT.as_view(), name="update-dgkt"),
    path('delete-dgkt/<id>/', DeleteDGKT.as_view(), name="delete-dgkt"),
    path('post-dgdetails/', PostDGDetails.as_view(), name="post-dgdetails"),
    path('dgkt-verification/', DGKTVerification.as_view(), name="dgkt-verification"),
    path('generate-dg-qr/<id>/', GenerateDGQRCode.as_view(), name="generate-dg-qr"),
    path('update-docs/', UpdateDocs.as_view(), name="update-docs"),
]

