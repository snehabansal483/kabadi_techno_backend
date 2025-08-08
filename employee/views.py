import os
from django.shortcuts import render
from rest_framework import generics, status, views, permissions
#from .serializers import Customer_RegisterSerializer, Customer_RegenerateVerificationEmailSerializer, Customer_EmailVerificationSerializer,LoginSerializer, Customer_RequestPasswordResetEmailSerializer, Customer_SetNewPassSerializer, Customer_Database_Checker, Customer_UpdateProfilePicSerializer, Employee_RegisterSerializer, Employee_RegenerateVerificationEmailSerializer, Employee_EmailVerificationSerializer, Employee_RequestPasswordResetEmailSerializer, Employee_SetNewPassSerializer, Employee_Database_Checker, Employee_UpdateProfilePicSerializer,profile_view_serializer#, Employee_LoginSerializer, Employee_LogOutSerializer,Customer_LogOutSerializer,, EmployeeRegistrationSerializer
from .serializers import *
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from accounts.models import CustomerProfile
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken,BlacklistedToken
#from .models import Account
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
import uuid
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ObjectDoesNotExist

current_site_frontend = '127.0.0.1:8000'


from PIL import Image
import qrcode,datetime

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
def convert_text_to_qrcode_employee(text, filename, request):
    # Path to logo
    logo_path = os.path.join(settings.MEDIA_ROOT, 'cvm_qrcodes', 'logo.png')
    logo = Image.open(logo_path)

    # Resize logo
    basewidth = 100
    wpercent = (basewidth / float(logo.size[0]))
    hsize = int((float(logo.size[1]) * float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.Resampling.LANCZOS)

    # Generate QR code
    QRcode1 = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    QRcode1.add_data(text)
    QRcode1.make()
    QRimg1 = QRcode1.make_image(fill_color='Black', back_color='white').convert('RGB')

    # Paste logo
    pos = ((QRimg1.size[0] - logo.size[0]) // 2, (QRimg1.size[1] - logo.size[1]) // 2)
    QRimg1.paste(logo, pos)

    # Ensure directory exists
    qr_folder_path = os.path.join(settings.MEDIA_ROOT, 'accounts', 'employee', 'QRs')
    os.makedirs(qr_folder_path, exist_ok=True)

    # Save QR code image
    qr_code_path = os.path.join(qr_folder_path, f'{filename}.jpg')
    QRimg1.save(qr_code_path)

    # Generate URL
    domain = get_current_site(request).domain
    qr_code_image_path = f"/accounts/employee/QRs/{filename}.jpg"
    qr_code_url = f"{domain}/media{qr_code_image_path}"

    return qr_code_image_path, qr_code_url
        

# creating Runtime database - stores only available logged in users with their refresh token
token_dict = {}

class Employee_RegisterView(generics.GenericAPIView):
    serializer_class = Employee_RegisterSerializer

    def post(self, request):
        serializer = Employee_RegisterSerializer(data=request.data)
        from .models import Employee as E
        got_email_1 = request.data["email"].lower()

        # Check if Employee with this email already exists
        check = E.objects.filter(email=got_email_1).exists()
        if not check:
            if serializer.is_valid(raise_exception=True):
                dealer_email = serializer.validated_data["dealer_email"].lower()

                if DealerProfile.objects.filter(auth_id__email=dealer_email).exists():
                    dealer_object = DealerProfile.objects.get(auth_id__email=dealer_email)

                    got_email = request.data["email"].lower()

                    # ✅ Corrected: check via Employee model, not Account
                    check_email = E.objects.filter(auth_id__email=got_email, kt_id="KTGU").exists()

                    if check_email:
                        E.objects.filter(auth_id__email=got_email).update(kt_id="KTDE")
                        Account.objects.filter(email=got_email).update(is_active=True)
                        last_user = E.objects.get(auth_id__email=got_email, kt_id="KTDE").auth_id
                    else:
                        # ✅ Save Account object if not already present
                       got_email = serializer.validated_data["email"].lower()

                    # Check if Account exists already
                    account_exists = Account.objects.filter(email=got_email).first()

                    if account_exists:
                        last_user = account_exists
                    else:
                        save_object = Account(email=got_email)
                        save_object.save()
                        last_user = save_object


                    # Save new Employee
                    employee = serializer.save(auth_id=last_user, dealer_id=dealer_object)
                    Ekt_id = f"KTDE{employee.id}"
                    employee.kt_id = Ekt_id
                    employee.save()

                    # Generate QR code
                    qr_code_image_path, qr_code_url = convert_text_to_qrcode_employee(
                        f"{Ekt_id}-{employee.username}", Ekt_id, request
                    )

                    # Check if account is active
                    if last_user.is_active:
                        employee.qrCode = qr_code_image_path
                        employee.is_active = True
                        employee.is_verified = True
                        employee.save(update_fields=['qrCode', 'is_active', 'is_verified'])

                        context = {
                            'KT_ID': employee.kt_id,
                            'email': employee.email,
                            'username': employee.username,
                            'mobile_number': employee.mobile_number,
                            'account_type': employee.account_type,
                        }
                        return Response(context, status=status.HTTP_201_CREATED)
                    else:
                        employee.qrCode = qr_code_image_path
                        employee.save(update_fields=['qrCode'])

                        # Send verification email
                        token = RefreshToken.for_user(employee.auth_id).access_token
                        current_site = get_current_site(request).domain
                        relativeLink = reverse('employee-email-verify')
                        image_logo = 'http://' + current_site + '/static/images/logo.png'
                        image_bg = 'http://' + current_site + '/static/images/email-bg.png'
                        absurl = 'http://' + current_site + relativeLink + "?token=" + str(token)
                        mail_url = 'http://' + current_site_frontend + relativeLink + 'Frontend/' + "?token=" + str(token)

                        content = (
                            'Hello Employee! KT Id: ' + str(employee.kt_id) +
                            ', Name: ' + employee.username +
                            ', User Type: Employee. Use the link below to verify your Account.\n'
                        )

                        html_content = render_to_string("verify_email.html", {
                            'title': 'Verify Your Email',
                            'content': content,
                            'site': mail_url,
                            'img': image_logo,
                            'background': image_bg
                        })
                        text_content = strip_tags(html_content)

                        email = EmailMultiAlternatives(
                            "Verify your email",
                            text_content,
                            settings.EMAIL_HOST_USER,
                            [employee.email]
                        )
                        email.attach_alternative(html_content, "text/html")
                        email.send()

                        context = {
                            'KT_ID': employee.kt_id,
                            'email': employee.email,
                            'username': employee.username,
                            'mobile_number': employee.mobile_number,
                        }
                        return Response(context, status=status.HTTP_201_CREATED)
                else:
                    return Response({'msg': 'Dealer Does Not Exist'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Employee already exists
            existing = E.objects.get(email=got_email_1)
            if existing.is_verified:
                return Response({'msg': 'Your verified account already exists!'}, status=status.HTTP_409_CONFLICT)
            else:
                return Response({'msg': 'Your unverified account already exists!'}, status=status.HTTP_409_CONFLICT)

class Employee_RegenerateVerificationEmail(generics.GenericAPIView):
    """This API regenerates the verification email in case the user forgot to verify and wants to verify again

    Args:
        generics (APIVIEW): Takes email as the input(For the details about input, please refer to the serializer tab)

    Returns:
        Response: Gives Response According to the User Input whether the User is already verified. If not verified, then sends a verification email to the user
    """
    serializer_class=Employee_RegenerateVerificationEmailSerializer
    def post(self, request):
        serializer = self.serializer_class(data = request.data)
        email = request.data['email']
        if Employee.objects.filter(email=email).exists():
            try:
                user = Employee.objects.get(email=email)
                if user.is_verified:
                    return Response({'already_done':'You have already verified your email'}, status=status.HTTP_208_ALREADY_REPORTED)
                elif not user.is_verified:
                    user_id = user.is_admin
                    token = RefreshToken.for_user(user.auth_id).access_token
                    current_site = get_current_site(request).domain
                    relativeLink = reverse('employee-email-verify')
                    absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
                    mail_url='http://'+current_site_frontend+relativeLink + "?token="+str(token)
                    image_logo = 'http://' + current_site + '/static/images/logo.png'
                    image_bg = 'http://' + current_site + '/static/images/email-bg.png'

                    content = 'Hello Employee! User Id: KT'+ str(user.kt_id)+', Name: '+user.username+', User Type: Employee '+'\nForgot to verify your email?\nWorry not\nUse the link below to verify your Account:  \n'+absurl
                    # data = {'email_body': email_body, 'to_email': user.email, 'email_subject': 'Verify your email'}
                    # Util.send_email(data)
                    html_content = render_to_string("verify_email.html", {'title':'Verify your email', 'content':content, 'site':mail_url, 'img':image_logo, 'background': image_bg})
                    text_content = strip_tags(html_content)

                    email = EmailMultiAlternatives(
                        "Verify your email", 
                        text_content, 
                        settings.EMAIL_HOST_USER,
                        [user.email]
                    )
                    email.attach_alternative(html_content, "text/html")
                    email.send()
                    return Response({'success':'Successfully Sent'}, status=status.HTTP_202_ACCEPTED)
            except:
                return Response({'unsuccessful':'The User is Not Registered Yet'}, status=status.HTTP_404_NOT_FOUND)


class Employee_VerifyEmail(views.APIView):
    """As the name suggests, This API verifies the user by the email sent to the user.
    The Email Contains Token which then be expired after verification
    The token is for checking purposes for verification

    Args:
        views (APIVIEW): takes TOKEN and USER_ID as an input

    Returns:
        Response: Gives Response According to the User Input whether the User was verified or not, or if the user is already verified
    """
    
    serializer_class=Employee_EmailVerificationSerializer

    # token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    # @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = Employee.objects.get(auth_id = payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            if not user.is_active:
                user.is_active = True
                user.save()
            return Response({'email': 'Successfully acivated'}, status=status.HTTP_200_OK) 
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST) 
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST) 

# creating id _card function
#import pandas as pd
from PIL import Image, ImageDraw, ImageFont
def create_id_card(Profile_Pic,kt_id,username,mobile_number,request):
    font_path = os.path.join(settings.BASE_DIR, 'static', 'font', 'OpenSans-Semibold.ttf')
    
    # Try to load custom font, fallback to system fonts, then default
    font = None
    font_size = 16
    try:
        font = ImageFont.truetype(font_path, size=font_size)
    except OSError:
        try:
            # Try Windows system fonts
            font = ImageFont.truetype("arial.ttf", size=font_size)
        except OSError:
            try:
                font = ImageFont.truetype("calibri.ttf", size=font_size)
            except OSError:
                # Final fallback to default PIL font
                font = ImageFont.load_default()
                print(f"Warning: Could not load any custom fonts. Using default font.")
    
    template_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'template.png')
    try:
        template = Image.open(template_path)
    except FileNotFoundError:
        # Create a basic template if template.png is missing
        template = Image.new('RGB', (500, 300), color='white')
        print(f"Warning: Could not load template at {template_path}. Using default template.")
    
    try:
        profile_picture = Image.open(Profile_Pic).resize((170, 195), Image.LANCZOS)
    except Exception as e:
        # Create a placeholder if profile picture fails to load
        profile_picture = Image.new('RGB', (170, 195), color='#bdc3c7')
        # Add a simple person icon placeholder
        draw_placeholder = ImageDraw.Draw(profile_picture)
        draw_placeholder.ellipse([60, 40, 110, 90], fill='#95a5a6')  # head
        draw_placeholder.ellipse([50, 120, 120, 180], fill='#95a5a6')  # body
        print(f"Warning: Could not load profile picture. Using placeholder. Error: {e}")
    
    # Paste profile picture in the designated area (with proper positioning for new template)
    template.paste(profile_picture, (22, 72))
    
    draw = ImageDraw.Draw(template)
    
    # Position text values next to labels in the new template
    # Adjusted coordinates to match the professional template layout
    draw.text((315, 80), kt_id, font=font, fill='#2c3e50')
    draw.text((260, 125), username, font=font, fill='#2c3e50')
    draw.text((270, 170), "Verified", font=font, fill='#27ae60')  # Green for verified status
    draw.text((265, 215), mobile_number, font=font, fill='#2c3e50')

    '''template.save(f"{settings.MEDIA_ROOT}/accounts/employee/id_cards/{kt_id}.jpg")
    domain = get_current_site(request).domain

    template_image_path = f"/accounts/employee/id_cards/{kt_id}.jpg"
    template_url = f"{domain}/media/accounts/employee/id_cards/{kt_id}.jpg"'''
    return template


class Employee_LoginAPIView(APIView):
    """Sign in Process for the Employee.

    ### Still in Testing Phase ###
    {Works properly but still deciding what the output should be}

    SUGGESTION: Redirect it from Employee_Database_CheckerAPIView so that the user is first checked for verification and then log in

    Args:
        generics (GenericAPIView): Takes email and password as input(For the details about input, please refer to the serializer tab)

    Returns:
        Response: Enlists all the user details except password
    """
    serializer_class = LoginSerializer
    def post(self, request):
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email'].lower()
            password= serializer.initial_data["password"]
            is_email_exists = Employee.objects.filter(email=email).exists()
            if is_email_exists:
                user = Employee.objects.get(email=email)
                if user.is_verified:
                    valid_password = user.check_password(password)
                    if valid_password:
                        account_user = Account.objects.get(id = user.auth_id.id)
                        account_user.is_active = True
                        account_user.save()

                        if user.id_card == None or user.id_card == "":
                            id_card = create_id_card(user.ProfilePic,user.kt_id,user.username,user.mobile_number,request)
                            try:
                                # Ensure the directory exists before saving
                                id_card_dir = os.path.join(settings.MEDIA_ROOT, 'accounts', 'employee', 'id_cards')
                                os.makedirs(id_card_dir, exist_ok=True)
                                id_card_path = f"{settings.MEDIA_ROOT}/accounts/employee/id_cards/{user.kt_id}.jpg"
                                id_card.save(id_card_path)
                                user.id_card = f'/accounts/employee/id_cards/{user.kt_id}.jpg'
                                user.save()
                            except Exception as e:
                                print(f"Error saving ID card: {e}")
                                # Set a placeholder path if save fails
                                user.id_card = '/static/images/placeholder_id.jpg'
                                user.save()

                        global token_dict
                        all_present_ids = set(Employee.objects.all().values_list('id', flat=True))
                        {token_dict.pop(k)  for k in set(token_dict) - all_present_ids}
                        
                        if account_user.id in token_dict.keys():
                            old_token = RefreshToken(token_dict[account_user.id])
                            old_token.blacklist()

                        OutstandingToken.objects.filter(user_id = account_user.id).delete()
                        BlacklistedToken.objects.filter(token__expires_at__lt = datetime.datetime.now()).delete()
                        OutstandingToken.objects.filter(expires_at__lt = datetime.datetime.now()).delete()
                        Employee.objects.filter(email=email).update(online=True)
    
                        try:
                            cus_object = CustomerProfile.objects.get(email = user.email)
                            cus_object.online=False
                            account_cus_object_id = cus_object.auth_id.id
                            old_token_2 = RefreshToken(OutstandingToken.objects.get(user_id=account_cus_object_id).token)
                            old_token_2.blacklist()
                            token_dict.pop(account_cus_object_id,None)
                            OutstandingToken.objects.filter(user_id = account_cus_object_id).delete()
                            cus_object.save()
                            #Account.objects.filter(email = user.email).update(online=False)
                        except:
                            pass

                        try:
                            dlr_object = DealerProfile.objects.get(email = user.email)
                            dlr_object.online=False
                            account_dlr_object_id = dlr_object.auth_id.id
                            old_token_2 = RefreshToken(OutstandingToken.objects.get(user_id=account_dlr_object_id).token)
                            old_token_2.blacklist()
                            token_dict.pop(account_dlr_object_id,None)
                            OutstandingToken.objects.filter(user_id = account_dlr_object_id).delete()
                            dlr_object.save()
                            #Account.objects.filter(email = user.email).update(online=False)
                        except:
                            pass

                        OutstandingToken.objects.filter(user = None).delete()
                            
                        ## Generating New Tokens for user
                        tokens = get_tokens_for_user(account_user)

                        ## updating our Runtime database with logged in user and its refresh token
                        token_dict.update({account_user.id : tokens['refresh']})
                        user_logged_in.send(sender=type(user), request=request, user=user)
                        return Response({'msg':f"Employee, {user.username} you are logged in successfully !",'tokens':tokens},status=status.HTTP_200_OK)
                    else:
                        return Response({'msg':'Incorrect password'}) 
                else:
                    return Response({'msg':'Your account is not verified yet. Plz verify it first.'}) 
            else:
                return Response({'msg':'Account Does Not Exist.'}) 
        else:
            return Response(serializer.errors,status = status.HTTP_400_BAD_REQUEST)

class Employee_UpdateProfilePic(APIView):
    serializer_class = Employee_UpdateProfilePicSerializer
    def post(self, request, id):
       serializer = Employee_UpdateProfilePicSerializer(data = request.data)
       ProfilePic = request.data['ProfilePic']
       if serializer.is_valid(raise_exception = True):

        if Employee.objects.filter(id=id).exists():
            user = Employee.objects.get(id=id)
            user.ProfilePic = ProfilePic
            user.save()
            return Response({'successful': 'Profile Picture updated successfully'})
        return Response({'NOT successful': 'No Employee with this email present'})
       
class Employee_Updateaadhar_card(APIView):
    serializer_class = Employee_Updateaadhar_cardSerializer
    def post(self, request, id):
       serializer = Employee_Updateaadhar_cardSerializer(data = request.data)
       aadhar_card = request.data['aadhar_card']
       if serializer.is_valid(raise_exception = True):

        if Employee.objects.filter(id=id).exists():
            user = Employee.objects.get(id=id)
            user.aadhar_card = aadhar_card
            user.save()
            return Response({'successful': 'aadhar card updated successfully'})
        return Response({'NOT successful': 'No Employee with this email present'})

class Employee_UpdateAtrrs(APIView):
    serializer_class = Employee_UpdateAtrrsSerializer
    def post(self, request):
        serializer = Employee_UpdateAtrrsSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            Eid = request.data['Eid']
            mobile_number = request.data['mobile_number']
            dealer_email = request.data['dealer_email'].lower()

            try:
                Deal = Employee.objects.get(id = Eid)
                Deal.mobile_number = mobile_number
                Deal.dealer_id = Deal.dealer_id = DealerProfile.objects.get(auth_id__email=dealer_email)
                Deal.save()
                return Response(serializer.data) 
            except ObjectDoesNotExist:
                return Response({'unsuccesful': 'no such id'}, status=status.HTTP_204_NO_CONTENT)


class Employee_LogoutAPIView(APIView):
    """A Logout API for the Employee
    For now it blacklists the RefreshToken
    ### Still in Testing Phase ###
    {Will make it completely after the frontend work gets completed}

    Args:
        generics (GenericAPIView): Takes Refresh Token as an input

    Returns:
        Response: NO CONTENT
    """
    def post(self,request,format=None,token=None):
        if token != None and token != "":
            try:
                decoded_token= jwt.decode(token,settings.SECRET_KEY,algorithms="HS256")
                print(decoded_token)
            except:
                raise AuthenticationFailed('Invalid token')
            account_id_2 = decoded_token['user_id']
            global token_dict
            check = Employee.objects.get(auth_id=decoded_token['user_id'])
            if check.online:
                try:
                    token = RefreshToken(OutstandingToken.objects.get(user_id = decoded_token['user_id']).token)
                except:
                    raise AuthenticationFailed('Unauthenticated. Login again !')
                token.blacklist()
                token_dict.pop(account_id_2,None)
                Employee.objects.filter(auth_id=decoded_token['user_id']).update(online = False)
                OutstandingToken.objects.filter(user_id = account_id_2).delete()

                return Response(f"Employee, logout success. refresh token blacklisted")
            else:
                raise AuthenticationFailed('Unauthenticated. Login again !')
        else:
            raise AuthenticationFailed('Unauthenticated')
        


class Employee_Database_CheckerAPIView(generics.GenericAPIView):
    """The preceeding step of Employee_LoginAPIView and Employee_RequestPasswordResetEmail API.
    It checks the user database for the user verification and gives response according to it

    SUGGESTION: If the User is not verified, Send the user to Regenerate the Verification Email

    Args:
        generics (GenericAPIView): Takes user email as input

    Returns:
        Response: Gives response according to the status of the user. If the user is verified then, SUCCESS. If not then, PLEASE VERIFY. ELSE IF the user doesn't exist then, Invalid USer
    """
    #permission_classes = (AllowAny,)
    serializer_class = Employee_Database_Checker
    # email = openapi.Parameter('email', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    # @swagger_auto_schema(manual_parameters=[email])
    def get(self, request, email):
        try:
            email = email
            user_obj = Employee.objects.get(email=email)
            if not user_obj.is_verified:
                status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
                response = {
                    'status code': status_code,
                    'message': 'Please firstly verify your email. Mail sent to your email!!',
                }
                return Response(response, status=status_code) 
            if Employee.objects.filter(email=email).exists():
                user_obj = Employee.objects.get(email=email)
                return Response({'success':'User Exists in the Database'}, status=status.HTTP_302_FOUND)
        except:
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            response = {
                'status code': status_code,
                'message': 'Invalid User',
            }
            return Response(response, status=status_code)


class Employee_RequestPasswordResetEmail(generics.GenericAPIView):
    """This API requires Employee's email address to send the email to the user. It checks first if the user exists in the database or not then sends the Request password email
    !!!MUST BE REDIRECTED FROM DATABASE CHECKER API!!!

    Args:
        generics (GenericAPIView): Takes Employee's email as an input

    Returns:
        Response: Gives Response whether the email was sent succesfully or not. If not, then states that the user does not exists.{The Email Exists of User Id and TOKEN}
    """

    serializer_class = Employee_RequestPasswordResetEmailSerializer
    def post(self, request):
        # data = {'request': request, 'data': request.data}
        serializer = self.serializer_class(data=request.data)
        # serializer.is_valid(raise_exception=True)
        email = request.data['email']
        if Employee.objects.filter(email=email).exists():
            user = Employee.objects.get(email=email)
            user_id = Employee.objects.get(email=email).id
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request = request).domain
            relativeLink = reverse('employee-password-reset-confirm', kwargs={'user_id': user_id, 'token': token})
            absurl='http://'+current_site+relativeLink
            mail_url='http://'+current_site_frontend+relativeLink
            image_logo = 'http://' + current_site + '/static/images/logo.png'
            image_bg = 'http://' + current_site + '/static/images/email-bg.png'
            content = 'Hello Employee! User Id: KTDE'+ str(user_id)+' Name: '+user.username+ ' User Type: Employee '+'Forgot your Password? \n Use the link below to reset your password  \n'+absurl
            # data = {'email_body': email_body, 'to_email': user.email, 'email_subject': 'Reset your Password'}
            # Util.send_email(data)
            html_content = render_to_string("forget_password.html", {'title':'Reset Your Password', 'content':content, 'site':mail_url, 'img':image_logo, 'background': image_bg})
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                "Reset Your Password", 
                text_content, 
                settings.EMAIL_HOST_USER,
                [user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            return Response({'success':'The Link To Reset Your Password has been sent to your Email'}, status=status.HTTP_200_OK)
        
        
        else:
            return Response({'unsuccessful':'The User is Not Registered Yet'})
        
class Dealer_Employee_RequestPasswordResetEmail(generics.GenericAPIView):
    """This API requires Employee's email address to send the email to the user. It checks first if the user exists in the database or not then sends the Request password email
    !!!MUST BE REDIRECTED FROM DATABASE CHECKER API!!!

    Args:
        generics (GenericAPIView): Takes Employee's email as an input

    Returns:
        Response: Gives Response whether the email was sent succesfully or not. If not, then states that the user does not exists.{The Email Exists of User Id and TOKEN}
    """

    serializer_class = Dealer_Employee_RequestPasswordResetEmailSerializer
    def post(self, request):
        # data = {'request': request, 'data': request.data}
        serializer = self.serializer_class(data=request.data)
        # serializer.is_valid(raise_exception=True)
        dealer_email = request.data['dealer_email'].lower()
        employee_email = request.data['employee_email'].lower()
        
        if DealerProfile.objects.filter(auth_id__email=dealer_email).exists():
            dealer_object = DealerProfile.objects.get(auth_id__email=dealer_email)
            if Employee.objects.filter(email=employee_email).exists():
                user = Employee.objects.get(email=employee_email)
                if user.dealer_id == dealer_object:
                    user = Employee.objects.get(email=employee_email)
                    user_id = Employee.objects.get(email=employee_email).id
                    token = PasswordResetTokenGenerator().make_token(user)
                    current_site = get_current_site(request = request).domain
                    relativeLink = reverse('employee-password-reset-confirm', kwargs={'user_id': user_id, 'token': token})
                    absurl='http://'+current_site+relativeLink
                    mail_url='http://'+current_site_frontend+relativeLink
                    image_logo = 'http://' + current_site + '/static/images/logo.png'
                    image_bg = 'http://' + current_site + '/static/images/email-bg.png'
                    content = 'Hello Dealer! the Employee\'s User Id: KTDE'+ str(user_id)+' Name: '+user.username+ ' \n Use the link below to reset your employee password  \n'+absurl
                    # data = {'email_body': email_body, 'to_email': user.email, 'email_subject': 'Reset your Password'}
                    # Util.send_email(data)
                    html_content = render_to_string("forget_password.html", {'title':'Reset Your Password', 'content':content, 'site':mail_url, 'img':image_logo, 'background': image_bg})
                    text_content = strip_tags(html_content)

                    email = EmailMultiAlternatives(
                        "Reset Your Password", 
                        text_content, 
                        settings.EMAIL_HOST_USER,
                        [dealer_email]
                    )
                    email.attach_alternative(html_content, "text/html")
                    email.send()
                    return Response({'success':'The Link To Reset Your employee Password has been sent to your Email'}, status=status.HTTP_200_OK)
        
                else:
                    return Response({'unsuccessful':'This Employee is Not connected with the Entered Dealer'})
            else:
                return Response({'unsuccessful':'The Employee is Not Registered Yet'})
        else:
            return Response({'unsuccessful':'The Dealer is Not Registered Yet'})
            

        
class Employee_PasswordTokenCheckAPI(views.APIView):
    """Checks whether the Token and User ID provided in the email is valid or not.
    Unnecessary step. Just made it as a Precautionary Measure
    MUST BE REDIRECTED AFTER Employee_RequestPasswordResetEmail API

    Args:
        views (APIView): Takes USER ID and TOKEN as input

    Returns:
        Response: Credentials Validated if True, Else: Error
    """
    def get(self, request, user_id, token):
        try:
            user_id = user_id
            user = Employee.objects.get(id = user_id)

            
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'The Token is not Valid, Please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({'success': True, 'message': 'Credentials Validated', 'user_id': user_id, 'token': token}, status=status.HTTP_200_OK)


        except DjangoUnicodeDecodeError as identifier:
            if not PasswordResetTokenGenerator().check_token(user):
                return Response({'error': 'The Token is not Valid, Please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)

class Employee_SetNewPassAPIView(generics.GenericAPIView):
    """The Final Step for Forget Password Process.
    Sets the new password after validating the Token and User Id sent in email.
    MUST BE REDIRECTED AFTER Employee_PasswordTokenCheckAPI


    Args:
        generics (GenericAPIView): Takes Token , User ID and NEW PASSWORD as input

    Returns:
        Response: Sets the new password
    """
    serializer_class = Employee_SetNewPassSerializer
    def patch(self, request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)

class Employee_ProfileAPIView(APIView):
    def get(self,request,format=None,token=None):
        if token != None and token != "":
            try:
                decoded_token= jwt.decode(token,settings.SECRET_KEY,algorithms="HS256")
            except:
                raise AuthenticationFailed('Invalid token')
            user =Employee.objects.get(auth_id=decoded_token['user_id'])
            serializer_object = Employee_profile_view_serializer(user)
            if user.online :
                if ("KTDE" in serializer_object.data['kt_id'] and "employee" in request.path):
                    # Returning validated user's data
                    return Response(serializer_object.data,status=status.HTTP_200_OK,)
                else:
                    raise AuthenticationFailed('Invalid Request')
            else:
                return Response({'message':f'Employee, you have been forcefully Logged out by KT Team or your connection broke up '})
        else:
            raise AuthenticationFailed('Unauthenticated')
