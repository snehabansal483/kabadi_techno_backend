from django.urls import path
from .views import encode_digipin_view, decode_digipin_view

urlpatterns = [
    path("encode-digipin/", encode_digipin_view),
    path("decode-digipin/", decode_digipin_view),
]
