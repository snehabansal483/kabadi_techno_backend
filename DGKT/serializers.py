from rest_framework import serializers
from .models import *

class PostDGKTSerializer(serializers.ModelSerializer):
    class Meta:
        model = DGKabadiTechno
        fields = '__all__'
        read_only_fields = ['status', 'aadhar_status', 'otp']

class CheckAadharOtpSerializer(serializers.ModelSerializer):
    dgktid = serializers.IntegerField()
    class Meta:
        model = DGKabadiTechno
        fields = ['dgktid', 'otp']

class GetDGKTSerializer(serializers.ModelSerializer):
    class Meta:
        model = DGKabadiTechno
        exclude = ('otp', 'DGPin')

class UpdateDGKTSerializer(serializers.ModelSerializer):
    dgktid = serializers.IntegerField()
    class Meta:
        model = DGKabadiTechno
        fields = ['dgktid', 'email', 'phone_number', 'ProfilePic']
        # read_only_fields = ['kt_id', 'account_type', 'name', 'aadhar_number', 'DGLogo', 'DGLogoWoBg', 'DGPin', 'status', 'aadhar_status']

class PostDGDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DGDetails
        fields = '__all__'
        read_only_fields = ['name', 'kt_id', 'DGid', 'qr_code', 'qr_image', 'document_hash_value', 'date', 'time', 'ip']

class DGKTVerificationSerializer(serializers.ModelSerializer):
    dgktid = serializers.IntegerField()
    class Meta:
        model = DGKabadiTechno
        fields = ['dgktid', 'DGPin']
        # read_only_fields = ['status', 'aadhar_status']

class GenerateDGQRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DGDetails
        fields = '__all__'

class UpdateDocsSerializer(serializers.ModelSerializer):
    DgDTid = serializers.IntegerField()
    class Meta:
        model = DGDetails
        fields = ['DgDTid', 'document']
        read_only_fields = ['DGkt', 'name', 'kt_id', 'DGid', 'qr_code', 'qr_image', 'document_hash_value', 'date', 'time', 'ip']
