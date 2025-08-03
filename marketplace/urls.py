from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('create-marketplace/', CreateMarketplace.as_view(), name='create-marketplace'),
    path('get-marketplace/<kt_id>/', GetMarketplace.as_view(), name='get-marketplace'),
    path('active-marketplaces/', ListActiveMarketplaces.as_view(), name='active-marketplaces'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
