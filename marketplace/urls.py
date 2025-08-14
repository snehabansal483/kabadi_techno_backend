from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('create-marketplace/', CreateMarketplace.as_view(), name='create-marketplace'),
    path('get-marketplace/<kt_id>/', GetMarketplace.as_view(), name='get-marketplace'),
    path('active-marketplaces/', ListActiveMarketplaces.as_view(), name='active-marketplaces'),
    path('delete-marketplace/<kt_id>/', DeleteMarketplace.as_view(), name='delete-marketplace'),
    path('deactivate-marketplace/<kt_id>/', SoftDeleteMarketplace.as_view(), name='deactivate-marketplace'),
    path('qr-display/<kt_id>/', marketplace_qr_display, name='marketplace-qr-display'),
    path('visiting-card/<kt_id>/', marketplace_visiting_card, name='marketplace-visiting-card'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
