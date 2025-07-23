from PIL import Image
import qrcode
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

# domain = settings.DOMAIN_URL


def convert_text_to_qrcode(text, filename, request):

    # taking image which we wants in the QR code center
    Logo_link = f"{settings.MEDIA_ROOT}/cvm_qrcodes/logo.png"

    logo = Image.open(Logo_link)

    # taking base width
    basewidth = 100

    # adjust image size
    wpercent = (basewidth / float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
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
    QRimg1.save(f"{settings.MEDIA_ROOT}/DGKT/DGKT_qrcodes/{filename}.jpg")
    domain = get_current_site(request).domain

    qr_code_image_path = f"/DGKT/DGKT_qrcodes/{filename}.jpg"
    qr_code_url = f"{domain}/media/DGKT/DGKT_qrcodes/{filename}.jpg"

    return qr_code_image_path, qr_code_url


def send_pass_code(email, code):
    subject = 'AADHAR VERIFICATION OTP for Kabadi Techno'
    message = f'Hi, Your pass code is {code}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True
