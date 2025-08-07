import random
from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework import status, exceptions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.generics import UpdateAPIView
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
from .helper import *
import datetime
import uuid
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from rest_framework import status
from rest_framework.exceptions import NotFound


default_sign_in_email = "snehabansal481@gmail.com"

class CvmRegistrationApi(viewsets.ModelViewSet, viewsets.GenericViewSet):
    
    permission_classes = (AllowAny,)
    queryset = CvmRegistration.objects.all()
    serializer_class = CvmRegistrationSerializer
    
    
    # Override the retrieve method to get a single object by ID
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except:
            return Response({"Massage":"Invalid Data Or Request!!!!"})

        # Override the destroy method to handle object deletion by ID
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response({'msg':'deleted'},status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"Massage":"Invalid Data Or Request!!!!"})
        
        # Override the partial_update method to handle partial updates by ID
    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except:
                return Response({"Massage":"Invalid Data Or Request!!!!"})

class UpdateCVM(APIView):
    def get_object(self, uid):
        try:
            return CvmRegistration.objects.get(uid=uid)
        except CvmRegistration.DoesNotExist:
            raise NotFound(detail="CVM does not exist")

    def get(self, request, uid):
        try:
            my_model = self.get_object(uid)
            serializer = CvmRegistrationSerializer(my_model)
            return Response(serializer.data)
        except NotFound as e:
            return Response({"Message": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, uid):
        try:
            my_model = self.get_object(uid)
            serializer = CvmRegistrationSerializer(my_model, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except NotFound as e:
            return Response({"Message": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"Message": f"Invalid Request: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, uid):
        try:
            cvm_object = self.get_object(uid)
            cvm_object.delete()
            return Response({"success": "CVM Deleted!!"}, status=status.HTTP_204_NO_CONTENT)
        except NotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)


class CvmList(APIView):
    
    def get(self,request,):
        try:
            movies = CvmRegistration.objects.all()
            serializer = CvmRegistrationSerializer(movies,many=True)
            return Response(serializer.data)
        except:
            return Response({"Massage":"Invalid Data Or Request!!!!"})



class CvmWeightApi(APIView):
    def get_object(self, uid):
        try:
            return CvmRegistration.objects.get(uid=uid)  # Replace with your model name
        except CvmRegistration.DoesNotExist:
            return Response(status=status.NOT_FOUND)

    def get(self, request, uid):
        my_model = self.get_object(uid)
        serializer = CvmWeightUpdateSerializer(my_model)  # Use your serializer
        return Response(serializer.data)

    def put(self, request, uid):
        my_model = self.get_object(uid)
        serializer = CvmWeightUpdateSerializer(my_model, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
        

otp_value = 0

@api_view(['POST'])
def send_otp(request):
    try:
        cvmid = request.data['uid']
        cvm = CvmRegistration.objects.get(uid=cvmid)

        otp = random.randint(1111, 9999)
        global otp_value
        otp_value = otp
        message = f"Your Otp for Sign into CVM is {otp}"
        to_email = default_sign_in_email
        send_email = EmailMessage("CVM Sign-in OTP", message, to=[to_email])
        send_email.send()

        return Response({
            'status': "success",
            'msg': "OTP sent to company email",
        }, status=status.HTTP_200_OK)

    except CvmRegistration.DoesNotExist:
        return Response({
            'status': "error",
            'msg': "CVM does not exist"
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            'status': 'error',
            'msg': f"Please try again: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def otp_checker(request):
    try:
        uid = request.data['uid']
        otp = request.data['otp']
        global otp_value
        if otp_value:
            if int(otp) == otp_value:
                otp_value=0
                cvm_object = CvmRegistration.objects.get(uid = uid)
                serializer_object = CvmRegistrationSerializer(cvm_object)
                return Response(serializer_object.data, status=status.HTTP_200_OK)
            else:
                return Response({"msg":"Invalid OTP"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"msg":"Regenerate OTP"}, status=status.HTTP_404_NOT_FOUND)
    except:
        return Response({"msg":"Invalid OTP or ID"})


#to get the details of all the cvms whose volume is 80 or less than 80
class GetCvmVolume(APIView):
    # permission_classes = (AllowAny,)

    def get(self, request):
        try:
            cvm_details = CvmRegistration.objects.filter(volume__lte=80)
            serializer = GetCVMVolumeSerializer(cvm_details, many=True)

            status_code = status.HTTP_202_ACCEPTED
            response = {
                'status code': status_code,
                'data': serializer.data,
            }

        except Exception as e:
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            response = {
                'status code': status_code,
                'Qr Code': 'Invalid',
                'message': str(e)
            }
        return Response(response, status=status_code)

class CheckCvmVolume(APIView):
    def get(self, request, uid):
        try:
            cvm_details = CvmRegistration.objects.get(uid = uid)
            if cvm_details.volume >= 100:
                return Response({'FULLY FILLED': 'The CVM is no longer in use. Please Contact a Dealer to empty it urgently'})
            elif cvm_details.volume > 80 and cvm_details.volume < 100:
                return Response({'ALMOST FILLED': 'Please Contact a Dealer to empty it'})
            elif cvm_details.volume < 80 and cvm_details.volume > 40:
                return Response({'MODERATELY FILLED': 'It would be best if we Contact a Dealer to empty it early'})
            elif cvm_details.volume < 40:
                return Response({'NOT FILLED': 'THE CVM is still in use'})
        except ObjectDoesNotExist:
            return Response({'Not Found': 'There is NO CVM Details with this id'})


status_200 = status.HTTP_200_OK
status_400 = status.HTTP_400_BAD_REQUEST

# tob show available cvms according to pincode
class GetCvms(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = CvmRegistration.objects.all()
    serializer_class = CvmRegistrationSerializer

    def get(self, request, pincode):
        try:
            # pincode = int(request.GET.get("pincode"))
            cvm_details = CvmRegistration.objects.filter(pincode=pincode)
            serializer = CvmRegistrationSerializer(cvm_details, many=True)
            return Response({
                'data': {
                    'status': status_200,
                    'cvm': serializer.data
                    },
                })
        except:
            return Response({
                    'data': {
                        'status': status_400,
                        'error': "Incorrect URL"
                        },
                    })

# just for updating volume and weight if it exists else save the object in cvmdetails
class CVMDetails(APIView):
    serializer_class = CvmDetailsSerializer

    def post(self, request):
        try:
            qrcode_id = request.data.get('qrcode')
            weight = request.data.get('weight')
            volume = request.data.get('volume')

            if not all([qrcode_id, weight, volume]):
                return Response(
                    {"Message": "Missing required fields: qrcode, weight, or volume"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get QRCode instance (assuming qrcode is passed as ID)
            try:
                qr_code_obj = QRCode.objects.get(id=qrcode_id)
            except QRCode.DoesNotExist:
                return Response(
                    {"Message": "QRCode not found!"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Update or create CvmDetails entry
            cvmdetails, _ = CvmDetails.objects.update_or_create(
                qrcode=qr_code_obj,
                defaults={"weight": weight, "volume": volume}
            )


            # Update related CVM if exists
            if qr_code_obj.cvm_id:  # Use 'cvm_id' if that's the field name in QRCode
                qr_code_obj.cvm_id.weight = weight
                qr_code_obj.cvm_id.volume = volume
                qr_code_obj.cvm_id.save()

            serializer = CvmDetailsSerializer(cvmdetails)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {
                    "Message": "Invalid Data Or Request!!!!",
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class GenerateQRCode(APIView):
    # permission_classes = (AllowAny,)

    def get(self, request, machine_id):
        try:
            current_date_time = datetime.datetime.now()
            token = str(uuid.uuid4())
            qrcode_details = f"{machine_id}.{current_date_time}{token}"
            machine = CvmRegistration.objects.get(uid=machine_id)
            qrcode_instance = QRCode.objects.create(
                cvm_id=machine,
                qr_code=qrcode_details
            )
            qrcode_instance.qr_code = f"{qrcode_instance.qr_code}.{qrcode_instance.id}"

            qr_code_image_path, qr_code_url = convert_text_to_qrcode(f"{qrcode_instance.qr_code}.{qrcode_instance.id}", f"{qrcode_instance.cvm_uid}.{qrcode_instance.id}", request )

            qrcode_instance.qr_image = qr_code_image_path
            qrcode_instance.save(update_fields=['qr_code', 'qr_image'])
            
            qr_code_serializer = QRcodeSerializer(qrcode_instance).data
            qr_code_serializer['qrcode_image_url'] = qr_code_url

            status_code = status.HTTP_201_CREATED
            response = {
                'status code': status_code,
                'qrcode_details': qr_code_serializer
            }

        
            return Response(response, status=status_code)
        except Exception as e:
            return Response(
                {
                    "Message": "Invalid Data Or Request!!!!",
                    "error": str(e)  # optional: helpful for debugging
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class CheckQRCodeIsValid(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            user_type = request.data['user_type'].lower()
            # user_name = request.data['username']
            user_id = request.data['user_id']
            user_email_id = request.data['user_email_id']
            qr_code_details = request.data['qr_code_details'].split(".")
            machine_id = qr_code_details[0]
            qr_code_id = qr_code_details[-1]

            CvmRegistration.objects.get(uid=machine_id)
            qr_code = QRCode.objects.get(id=qr_code_id)
            # user_instance = Dealer.objects.get(user_id=kt_id)

            pass_code = random.randint(111111, 999999)

            if (user_type).lower() == 'dealer':
                send_pass_code(user_email_id, pass_code)
                qr_code.pass_code = pass_code
                qr_code.save(update_fields=['pass_code'])

            qr_code.user_type = user_type
            qr_code.user_id = user_id
            qr_code.user_email_id = user_email_id
            qr_code.scaned = True
            qr_code.save(update_fields=['user_type', 'user_id', 'user_email_id', 'scaned'])

            status_code = status.HTTP_202_ACCEPTED
            response = {
                'status code': status_code,
                'QRCode': "Valid",
            }

            
            return Response(response, status=status_code)
        except:
            return Response({"Massage":"Invalid Data Or Request!!!!"})

class CheckDealerPassCode(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            pass_code = int(request.data['pass_code'])
            qr_code_id = request.data['qr_code_id']
            user_instance = QRCode.objects.get(id=qr_code_id)

            if not int(user_instance.pass_code) == pass_code:
                raise exceptions.ValidationError(detail="Pass Code is not Valid !!")
            print(pass_code)
            print('------------------------------')
            user_instance.pass_code = random.randint(000000, 999999)
            
            user_instance.save(update_fields = ['pass_code'])
            print(user_instance.pass_code)
            

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

class GetUserDetailForCVM(APIView):
    permission_classes = (AllowAny,)

    def get(self, request,  qrcode_id):
        try:
            # n = 10
            status_code = status.HTTP_400_BAD_REQUEST
            # while n > 0:
            try:
                qrcode_scaned = QRCode.objects.get(id=qrcode_id, scaned=True, active=True)
            except:
                qrcode_scaned = None

            if qrcode_scaned:
                status_code = status.HTTP_200_OK
                    # break
                
                # n -= 1
                # time.sleep(2)

            qrcode_serializer = QRcodeSerializer(qrcode_scaned)
            response = {
                'status code': status_code,
                "data": qrcode_serializer.data
            }

        except Exception as e:
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            response = {
                'status code': status_code,
                'message': str(e)
            }

        return Response(response, status=status_code)

class PostUnlodScrap(APIView):
    serializer_class = PostUnlodScrapSerializer
    def post(self, request):
        try:
            serializer = PostUnlodScrapSerializer(data = request.data)
            if serializer.is_valid(raise_exception = True):
                serializer.save()
                return Response(serializer.data)
        except:
            return Response({"Massage":"Invalid Data Or Request!!!!"})

class GetUnloadScrap(APIView):
    def get(self, request):
        try:
            scrap = UnloadScrap.objects.all()
            serializer = GetUnloadScrapSerializer(scrap, many=True)
            return Response(serializer.data)
        except:
            return Response({"Massage":"Invalid Data Or Request!!!!"})
    
@api_view(["GET"])
def get_carts_in_cvm(request,cvm_uid,):
    try:
        customer_email = request.data.get('customer_email')
        if not customer_email or customer_email == "":
            all_cart_in_cvm = cart.objects.filter(cvm_uid=cvm_uid).values()
            return Response({"carts":all_cart_in_cvm})
        else:
            all_customer_cart_in_cvm = cart.objects.filter(cvm_uid=cvm_uid,customer_email=customer_email).values()
            return Response({"carts":all_customer_cart_in_cvm}) 
    except:
            return Response({"Massage":"Invalid Data Or Request!!!!"})       

@api_view(["POST"])
def post_cart_in_cvm(request,):
    try:
        customer_ktid = request.data.get('customer_ktid') 
        customer_email = request.data.get('customer_email') 
        qr_id = request.data.get('qr_id')
        cvm_uid = request.data.get('cvm_uid')
        weight = request.data.get('weight') 
        volume = request.data.get('volume') 
        image = request.data.get('image')
        approx_price = request.data.get('approx_price')
        other_comment = request.data.get('other_comment') 

        carts_in_machine = cart.objects.filter(cvm_uid=cvm_uid,status="in_machine")
        no_of_carts = carts_in_machine.count()
        if no_of_carts<=100:
            cart_object = cart(cvm_uid=cvm_uid,customer_email=customer_email,customer_ktid = customer_ktid,
                                qr_id = qr_id,weight = weight,volume = volume,image = image,
                                approx_price = approx_price,other_comment = other_comment,)
            cart_object.save()
            cart.objects.filter(id=cart_object.id).update(cart_id="CART0000"+str(cart_object.id))
            return Response({"msg":"Cart added","cart_id":"CART0000"+str(cart_object.id)})
        else:
            return Response({"msg":"there's no enough space in cart now!"})
    except:
            return Response({"Massage":"Invalid Data Or Request!!!!"})
        

    


@api_view(["GET"])
def get_orders_in_cvm(request,cvm_uid,):
    try:
        dealer_email = request.data.get('dealer_email')
        if not dealer_email or dealer_email == "":
            all_order_in_cvm = order.objects.filter(cvm_uid=cvm_uid).values()
            return Response({"orders":all_order_in_cvm})
        else:
            all_dealer_order_in_cvm = order.objects.filter(cvm_uid=cvm_uid,dealer_email=dealer_email).values()
            return Response({"orders":all_dealer_order_in_cvm})
    except:
        return Response({"message":"Invalid CVM or Email Address"})
    




class OrderPostView(APIView):
    def post(self, request):
        try:
            serializer = OrderSerializer(data=request.data)

            if serializer.is_valid():
                all_cart_ids = request.data.get('all_cart_ids')
                if all_cart_ids is not None and isinstance(all_cart_ids, str) and all_cart_ids.strip():
                    cart_ids = all_cart_ids.split(',')
                    
                    # Create the order instance
                    order_instance = serializer.save()

                    for cart_id in cart_ids:
                        order_id = f"ORDER{order_instance.id + 100000}"
                        
                        # Get the Cart object and update it
                        cart.objects.filter(cart_id=cart_id).update(order_id=order_id, status='picked_up')
                    
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"Massage":"Invalid Data Or Request!!!!"})


class orderapi(APIView):
    def get(self,request,order_id):
        try:
            order_object = order.objects.get(order_id=order_id)
            all_cart_ids = (order_object.all_cart_ids).split(",")
        except:
            return Response({"error":"order not found"})
        products = {}

        for i in all_cart_ids:
            cart_object = cart.objects.get(cart_id=i)
            products[cart_object.cart_id]={"table_id":cart_object.id,
                                           "customer_ktid" : cart_object.customer_ktid, 
                                            "customer_email" : cart_object.customer_email, 
                                            "qr_id" : cart_object.qr_id, 
                                            "cvm_uid" : cart_object.cvm_uid,
                                            "weight" : cart_object.weight, 
                                            "volume" : cart_object.volume, 
                                            "image" : str(cart_object.image),
                                            "approx_price" : cart_object.approx_price,
                                            "other_comment" : cart_object.other_comment, 
                                            "status" : cart_object.status, 
                                            "order_id" :cart_object.order_id,
                                            "created_at" :cart_object.created_at,
                                            "updated_at" :cart_object.updated_at,}
            
        return Response({"table_id" : order_object.id,
                         "order_id" : order_object.order_id,
                         "dealer_ktid" : order_object.dealer_ktid,
                         "dealer_email" : order_object.dealer_email,
                         "qr_id" : order_object.qr_id,
                         "cvm_uid" : order_object.cvm_uid,
                         "total_cart_no" : order_object.total_cart_no,
                         "all_cart_ids" : order_object.all_cart_ids,
                         "weight" : order_object.weight,
                         "volume" : order_object.volume,
                         "image" : str(order_object.image),
                         "other_comment" :  order_object.other_comment,
                         "status" : order_object.status,
                         "created_at" : order_object.created_at,
                         "updated_at" : order_object.updated_at,
                         "status":order_object.status,
                         "created_at":order_object.created_at,
                         "updated_at":order_object.updated_at,
                         "cart_details":products,
                         })
    
    def patch(self,request,order_id):
        status=request.data.get('status')
        if status :
            try:
                order_object = order.objects.get(order_id=order_id)
            except:
                return Response({"error":"order not found"})
            order_object.status = status
            order_object.save()
            return Response({"success":"status updated"})
        else:
            return Response({"error":"status value not received"})
        
    def delete(self,request,order_id):

        try:
            order_object = order.objects.get(order_id=order_id)
        except:
            return Response({"error":"order not found"})
        order_object.delete()
        return Response({"success":"Deleted"})
           
@api_view(["GET"])
def get_details(request,id):
    if "CART" in id:
        try:
            object = cart.objects.filter(cart_id = id).values()
            return Response(object)
        except:
            return Response({"Error":"Cart not exist!"})
        
    elif "ORDER" in id:
        try:
            object = order.objects.filter(order_id = id).values()
            return Response(object)
        except:
            return Response({"Error":"order not exist!"})
