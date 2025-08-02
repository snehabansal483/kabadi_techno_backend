from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from datetime import date
from .serializers import *
from .models import Marketplace
from accounts.models import DealerProfile

from PIL import Image
import qrcode
import os

def convert_text_to_qrcode(text, filename, request):
    """Generate a QR code with a central logo and return its path and URL."""

    # Load logo
    logo_path = os.path.join(settings.MEDIA_ROOT, 'marketplace/QRs/logo.png')
    logo = Image.open(logo_path)

    # Resize logo
    basewidth = 100
    wpercent = (basewidth / float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.Resampling.LANCZOS)

    # Create QR code
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(text)
    qr.make()
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Paste logo at the center
    pos = ((qr_img.size[0] - logo.size[0]) // 2,
           (qr_img.size[1] - logo.size[1]) // 2)
    qr_img.paste(logo, pos)

    # Save QR code
    qr_filename = f"{filename}.jpg"
    qr_image_path = os.path.join(settings.MEDIA_ROOT, 'marketplace/QRs', qr_filename)
    qr_img.save(qr_image_path)

    # Construct public URL
    domain = get_current_site(request).domain
    qr_code_url = f"http://{domain}/media/marketplace/QRs/{qr_filename}"
    qr_code_image_path = f"/marketplace/QRs/{qr_filename}"

    return qr_code_image_path, qr_code_url


class CreateMarketplace(APIView):
    serializer_class = CreateMarketplaceSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            dealer_id = request.data['dealer_id']
            end_duration = request.data['end_duration']

            # Check if marketplace already exists
            if Marketplace.objects.filter(dealer_id=dealer_id).exists():
                return Response({'unsuccessful': 'This dealer already has a Marketplace created'},
                                status=status.HTTP_306_RESERVED)

            # Create Marketplace
            marketplace = Marketplace.objects.create(
                dealer_id_id=dealer_id,
                end_duration=end_duration,
                status='active'  # Set status as active immediately
            )

            # Generate QR URL
            Dkt_id = marketplace.kt_id
            frontend_url = f"http://localhost:5173/marketplace/{Dkt_id}"  # frontend route
            qr_code_image_path, qr_code_url = convert_text_to_qrcode(frontend_url, Dkt_id, request)

            # Save QR code path and URL to Marketplace
            marketplace.qrCode = qr_code_image_path
            marketplace.url = qr_code_url
            marketplace.save()

            return Response({'success': 'Marketplace created and QR code generated'},
                            status=status.HTTP_202_ACCEPTED)


class GetMarketplace(APIView):
    def get(self, request, kt_id):
        marketplace = Marketplace.objects.filter(kt_id=kt_id)
        if not marketplace.exists():
            return Response({'error': 'Marketplace not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = GetMarketplaceSerializer(marketplace, many=True)
        return Response(serializer.data)
