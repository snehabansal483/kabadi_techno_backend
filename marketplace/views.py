from rest_framework.views import APIView
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from datetime import date
from .serializers import *
from .models import Marketplace
from accounts.models import DealerProfile
# Create your views here.

from PIL import Image
import qrcode
def convert_text_to_qrcode(text, filename, request):

    # taking image which we wants in the QR code center
    Logo_link = f"{settings.MEDIA_ROOT}/marketplace/QRs/logo.png"

    logo = Image.open(Logo_link)

    # taking base width
    basewidth = 100

    # adjust image size
    wpercent = (basewidth / float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.Resampling.LANCZOS
)
    QRcode1 = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )

    # taking url or text
    data = text

    # adding URL or text to QRcode
    QRcode1.add_data(data)

    # generating QR code
    QRcode1.make()

    # taking color name from user
    QRcolor = 'Black'

    # adding color to QR code
    QRimg1 = QRcode1.make_image(
        fill_color=QRcolor, back_color="white").convert('RGB')

    # set size of QR code
    pos = ((QRimg1.size[0] - logo.size[0]) // 2,
            (QRimg1.size[1] - logo.size[1]) // 2)
    QRimg1.paste(logo, pos)

    # save the QR code generated
    QRimg1.save(f"{settings.MEDIA_ROOT}/marketplace/QRs/{filename}.jpg")
    domain = get_current_site(request).domain

    qr_code_image_path = f"/marketplace/QRs/{filename}.jpg"
    qr_code_url = f"{domain}/media/marketplace/QRs/{filename}.jpg"

    return qr_code_image_path, qr_code_url

class CreateMarketplace(APIView):
    serializer_class = CreateMarketplaceSerializer
    def post(self, request):
        serializer = CreateMarketplaceSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            dealer_id = request.data['dealer_id']
            end_duration = request.data['end_duration']
            if Marketplace.objects.filter(dealer_id = dealer_id).exists():
                return Response({'unsuccessful': 'This dealer already has a Marketplace created'}, status=status.HTTP_306_RESERVED)
            else:
                marketplace = Marketplace.objects.create(dealer_id_id = dealer_id, end_duration = end_duration)
                marketplace.save()
                Dkt_id = marketplace.kt_id
                print(Dkt_id)
                domain = get_current_site(request).domain
                qr_url = f"http://{domain}/marketplace/{Dkt_id}"
                qr_code_image_path, qr_code_url = convert_text_to_qrcode(qr_url, Dkt_id, request)
                # qr_code_url = f"{domain}/marketplace/get-marketplace/{dealer_id}"
                marketplace.qrCode = qr_code_image_path
                marketplace.url = qr_code_url
                # today = date.today()
                # print(today)
                # end_duration = marketplace.end_duration
                # print(end_duration)
                # duration_active = end_duration - today
                # marketplace.duration_active = duration_active.days
                marketplace.status = 'active'
                marketplace.save()
                # context = {
                #     'dealer_id': marketplace.dealer_id.kt_id,
                #     'url': marketplace.url,
                #     'qrCode': marketplace.qrCode,
                #     'end_duration': marketplace.end_duration,
                #     'duration_active': marketplace.duration_active,
                #     'status': marketplace.status,
                # }
                return Response({'success':'Successfully Sent'}, status=status.HTTP_202_ACCEPTED)

class GetMarketplace(APIView):
    def get(self, request, kt_id):
        kt_id = kt_id
        marketplace = Marketplace.objects.filter(kt_id=kt_id)
        serializer = GetMarketplaceSerializer(marketplace, many = True)
        return Response(serializer.data)
