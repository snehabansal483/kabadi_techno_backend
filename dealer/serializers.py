# from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import dealer, RequestInquiry
from rest_framework import serializers

class dealerSerializer(serializers.ModelSerializer): #Returns Type Feature 
    class Meta:
        model = dealer
        # geo_field = "geom" #Geo Field.
        fields = "__all__"

class RequestInquiryGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequestInquiry
        exclude = ('id',)

class RequestInquiryPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestInquiry
        fields = '__all__'

# class dealerSerializer(GeoFeatureModelSerializer,serializers.HyperlinkedModelSerializer): #Returns Type Feature 
#     class Meta:
#         model = dealer
#         geo_field = "geom" #Geo Field.
#         fields = "__all__"

# from rest_framework_gis.serializers import GeoFeatureModelSerializer
# from .models import dealer

# class dealerSerializer(GeoFeatureModelSerializer): #Returns Type Feature
#     class Meta:
#         model = dealer
#         geo_field = "geom" #Geo Field.
#         fields = "__all__"
