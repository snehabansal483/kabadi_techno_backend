from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import Category,SubCategory
from rest_framework import generics, status, views, permissions
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
# Create your views here

#########
class CategoryList(APIView):
    
    def get(self,request):
        cat = Category.objects.all()
        serializer = CategorySerializer(cat,many = True)
        return Response(serializer.data)

    def post(self):
        pass

class AllSubCategoryList(APIView):
    
    def get(self, request):
        allsubcat = SubCategory.objects.all()
        serializer = AllSubCategorySerializer(allsubcat,many = True)
        return Response(serializer.data)

    def post(self):
        pass

class SubCategoryList(APIView):
    
    # def get(self, request, category):
    #     subcat = SubCategory.objects.filter(category=category)
    #     serializer = SubCategorySerializer(subcat,many = True)
    #     return Response(serializer.data)

    def get(self, request, keyword):
        try:
            # if keyword:
            subcategory_nms = SubCategory.objects.filter(Q(category__name__icontains=keyword))
            subcategory_count = subcategory_nms.count()
            context = {
            # 'subcategory': subcategory_nms,
            'subcategory_count': subcategory_count,
            }
            serializer = SubCategorySerializer(subcategory_nms, many = True)
            new_serializer_data = list(serializer.data)
            new_serializer_data.append(context)
            return Response(new_serializer_data, status=status.HTTP_302_FOUND)
        except ObjectDoesNotExist:
            return Response({'Not Found': 'There are no subcategories with this keyword in its name'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self):
        pass
