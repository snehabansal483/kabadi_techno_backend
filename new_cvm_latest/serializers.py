from rest_framework import serializers
from .models import *

# from cvm.models.cvm_registration import CvmRegistration


class CvmRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = CvmRegistration
        #geo_field = "geom" #Geo Field.
        fields = '__all__'
        read_only_fields = ['uid',]
        # read_only_fields = ('uid',)

class CvmDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = CvmDetails
        fields = '__all__'
        read_only_fields = ['cvm_id', 'cvm_uid', 'date', 'time']
        
class CvmWeightUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CvmRegistration
        fields = ['weight','volume',]
        




class QRcodeSerializer(serializers.ModelSerializer):
    user_role = serializers.CharField(source='user.role', read_only=True)
    machine = serializers.CharField(source='cvm.uid', read_only=True)
    # qr_code_image_url = serializers.SerializerMethodField()

    class Meta:
        model = QRCode
        fields = '__all__'

class GetCVMVolumeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CvmRegistration
        #geo_field = "geom" #Geo Field.
        fields = '__all__'
        # read_only_fields = ('uid',)

class PostUnlodScrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnloadScrap
        fields = '__all__'
        read_only_fields = ['active',]

class GetUnloadScrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnloadScrap
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = cart
        fields = '__all__'
        

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = order
        fields = '__all__'