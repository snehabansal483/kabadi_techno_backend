from rest_framework import serializers
from .models import Category,SubCategory


# serialzers for categoary and subcategory
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AllSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    sub_name = serializers.StringRelatedField()
    class Meta:
        model = SubCategory
        fields = '__all__'

