from django.urls import path
from .views import *

urlpatterns = [
    path('category-list/', CategoryList.as_view()),
    path('all-subcategory-list/', AllSubCategoryList.as_view()),
    # path('subcategory-list/<keyword>/', SubCategoryList.as_view()),

    
]
