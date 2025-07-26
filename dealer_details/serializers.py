from rest_framework import serializers
from .models import PriceList, GetPincodes, add_category, documents

class PriceListGetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    class Meta:
        model = PriceList
        fields = '__all__'

class PriceListPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceList
        fields = ('subcategory', 'dealer', 'pincode', 'price')

class UpdatePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceList
        fields = ('subcategory', 'dealer', 'pincode', 'price')

class DeletePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceList
        fields = ('subcategory', 'dealer', 'pincode')

class AddCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = add_category
        exclude = ('id', 'status')

class RequestAddCategoryGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = add_category
        fields = '__all__'

class DocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = documents
        fields = '__all__'

class GetDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = documents
        fields = '__all__'

class AddPincodesSerializer(serializers.ModelSerializer):
    # pincodes = serializers.ListField(child=serializers.CharField(max_length=6), allow_empty=True, max_length=5)

    class Meta:
        model = GetPincodes
        fields = ('dealer_id', 'pincode1', 'pincode2', 'pincode3', 'pincode4', 'pincode5')

class RequesttoAddPincodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GetPincodes
        fields = ('dealer_id', 'addrequest')

class GetallPincodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GetPincodes
        fields = '__all__'

class No_of_pincodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GetPincodes
        fields = '__all__'

class UpdatePincodesSerializer(serializers.ModelSerializer):

    class Meta:
        model = GetPincodes
        fields = ('dealer_id', 'pincode1', 'pincode2', 'pincode3', 'pincode4', 'pincode5', 'pincode6', 'pincode7', 'pincode8', 'pincode9', 'pincode10')

class SearchSubcategoryByPincodeSerializer(serializers.ModelSerializer):
    kt_id = serializers.SerializerMethodField(read_only=True)

    def get_kt_id(self, obj):
        return obj.dealer.kt_id
        
    class Meta:
        model = PriceList
        fields = '__all__'
        read_only_fields = ['category', 'subcategory']
