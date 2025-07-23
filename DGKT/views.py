import random
import uuid
from rest_framework.views import APIView
from rest_framework import generics, status, views, permissions, exceptions
from rest_framework.response import Response
from .helper import convert_text_to_qrcode, send_pass_code
from .serializers import *
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.

class PostDGKT(APIView):
    serializer_class = PostDGKTSerializer
    def post(self, request):
        serializer = PostDGKTSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            dg = serializer.save()
            pass_code = random.randint(111111, 999999)
            send_pass_code(dg.email, pass_code)
            dg.otp = pass_code
            dg.save(update_fields=['otp'])
            return Response(serializer.data)

class CheckAadharOtp(APIView):
    serializer_class = CheckAadharOtpSerializer
    def post(self, request):
        try:
            otp = int(request.data['otp'])
            dgktid = request.data['dgktid']
            dg = DGKabadiTechno.objects.get(id=dgktid)

            if not int(dg.otp) == otp:
                raise exceptions.ValidationError(detail="The OTP is not Valid !!")
            print(otp)
            print('------------------------------')
            dg.aadhar_status = 'Verified'
            dg.otp = random.randint(0000000, 9999999)
            
            dg.save(update_fields = ['otp', 'aadhar_status'])
            print(dg.otp)
            

            status_code = status.HTTP_202_ACCEPTED
            response = {
                'status code': status_code,
                'QRCode': "Valid",
            }
        except Exception as e:
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            response = {
                'status code': status_code,
                'Qr Code': 'Invalid',
                'message': str(e)
            }
        return Response(response, status=status_code)

class GetDGKT(APIView):
    def get(self,request, id):
        try:
            dg = DGKabadiTechno.objects.get(id = id)
            serializer = GetDGKTSerializer(dg)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'unsuccesful': 'no such id'}, status=status.HTTP_204_NO_CONTENT)

class UpdateDGKT(APIView):
    serializer_class = UpdateDGKTSerializer
    def post(self, request):
        serializer = UpdateDGKTSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            dgktid = request.data['dgktid']
            email = request.data['email']
            phone_number = request.data['phone_number']
            ProfilePic = request.data['ProfilePic']
            try:
                dg = DGKabadiTechno.objects.get(id = dgktid)
                dg.email = email
                dg.phone_number = phone_number
                dg.ProfilePic = ProfilePic
                dg.save()
                return Response(serializer.data) 
            except ObjectDoesNotExist:
                return Response({'unsuccesful': 'no such id'}, status=status.HTTP_204_NO_CONTENT)


class DeleteDGKT(APIView):
    def get(self,request, id):
        try:
            dg = DGKabadiTechno.objects.get(id = id)
            dg.delete()
            return Response({'successful': 'DGKT id successfully Deleted'}, status=status.HTTP_202_ACCEPTED)
        except ObjectDoesNotExist:
            return Response({'unsuccesful': 'no such id'}, status=status.HTTP_204_NO_CONTENT)

# class SendAadharVeriOTP(APIView):
#     serializer_class = SendAadharVeriOTPSerializer
#     def post(self, request):
#         serializer = SendAadharVeriOTPSerializer(data = request.data)
#         if serializer.is_valid(raise_exception = True):
#             id = request.data['id']
#             email = request.data['email']
#             try:
#                 dg = DGKabadiTechno.objects.get(id = id)
#                 serializer = GetDGKTSerializer(dg)
#                 return Response(serializer.data)
#             except ObjectDoesNotExist:
#                 return Response({'unsuccesful': 'no such id'}, status=status.HTTP_204_NO_CONTENT)



class PostDGDetails(APIView):
    serializer_class = PostDGDetailsSerializer
    def post(self, request):
        serializer = PostDGDetailsSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            dg = serializer.save()
            ip_add = request.META.get('REMOTE_ADDR')
            dg.ip = ip_add
            dg.save()
            return Response(serializer.data)

class DGKTVerification(APIView):
    serializer_class = DGKTVerificationSerializer
    def post(self, request):
        serializer = DGKTVerificationSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            dgktid = request.data['dgktid']
            DGPin = request.data['DGPin']
            try:
                dg = DGKabadiTechno.objects.get(id = dgktid)
                if str(dg.DGPin) == str(DGPin):
                    return Response({'Verified': 'Your password matches '}, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({'Wrong Password': 'Your password is wrong '}, status=status.HTTP_406_NOT_ACCEPTABLE)
            
            except ObjectDoesNotExist:
                return Response({'Not Found': 'There is no such DG Kabadi Techno ID registered'}, status=status.HTTP_404_NOT_FOUND)

class GenerateDGQRCode(APIView):
    # permission_classes = (AllowAny,)

    def get(self, request, id):
        try:
        # current_date_time = datetime.datetime.now()
            token = str(uuid.uuid4())
        # qrcode_details = f"{machine_id}.{current_date_time}{token}"
            qrcode_instance = DGDetails.objects.get(id = id)
            qrcode_instance.qr_code = f"{qrcode_instance.DGid}.{token}"

            qr_code_image_path, qr_code_url = convert_text_to_qrcode(f"{qrcode_instance.DGid}.{token}", f"{qrcode_instance.kt_id}", request )

            qrcode_instance.qr_image = qr_code_image_path
            qrcode_instance.save(update_fields=['qr_code', 'qr_image'])
            
            qr_code_serializer = GenerateDGQRCodeSerializer(qrcode_instance).data
            qr_code_serializer['qrcode_image_url'] = qr_code_url

            status_code = status.HTTP_201_CREATED
            response = {
                'status code': status_code,
                'qrcode_details': qr_code_serializer
            }

        except Exception as e:
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            response = {
                'status code': status_code,
                'message': str(e),
            }
        return Response(response, status=status_code)

class UpdateDocs(APIView):
    serializer_class = UpdateDocsSerializer
    def post(self, request):
        serializer = UpdateDocsSerializer(data = request.data)
        if serializer.is_valid(raise_exception = True):
            dgktid = request.data['DgDTid']
            document = request.data['document']
            try:
                dg = DGDetails.objects.get(id = dgktid)
                dg.document = document
                dg.save()
                return Response(serializer.data) 
            except ObjectDoesNotExist:
                return Response({'unsuccesful': 'no such id'}, status=status.HTTP_204_NO_CONTENT)
