"""
URL configuration for Kabadi_Techno project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Category/', include('Category.urls')),
    path('dealer/', include('dealer.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('dealer_details/', include('dealer_details.urls')),
    path('carts/', include('carts.urls')),
    path('accounts/', include('accounts.urls')),
    path('order/', include('order.urls')),
    path('dealer_marketplace/', include('dealer_marketplace.urls')),
    path('DGKT/', include('DGKT.urls')),
    path('voting_system/', include('voting_system.urls')),
    path('WebsiteContent/', include('WebsiteContent.urls')),
    path('homepage/', include('homepage.urls')),
    path('invoice/', include('invoice.urls')),
   

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


