#from django.contrib.gis.geos import Point
#from django.contrib.gis.measure import D
#from django.contrib.gis.db.models.functions import Distance
from django.http import BadHeaderError, HttpResponse
# from django_filters.rest_framework import DjangoFilterBackend
#from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from urllib3 import Retry

from Kabadi_Techno import settings
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
import json
from .models import dealer
import requests
import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
import requests
import json
from requests.adapters import HTTPAdapter


current_site_frontend = 'http://localhost:5173'

logger = logging.getLogger(__name__) 
status_200=status.HTTP_200_OK
status_400=status.HTTP_400_BAD_REQUEST

def dealerHome(request):
    html = "<html><head><title>Kabadi Techno API</title></head><body><center><b><p>Kabadi Techno API</p> </center></body></html>"
    return HttpResponse(html)

# Helper function to fetch pincode info with retry
def fetch_pincode_info(pincode):
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)

    india_post_url = f"https://api.postalpincode.in/pincode/{pincode}"

    try:
        res = session.get(india_post_url, timeout=5)
        res.raise_for_status()
        data = res.json()
        if data and data[0]["PostOffice"] is not None:
            return {
                "source": "India Post",
                "data": data[0]["PostOffice"][0]
            }
    except Exception:
        pass  # silently fall back

    # ✅ Fallback: Zippopotam API (supports India as IN)
    try:
        zip_url = f"https://api.zippopotam.us/IN/{pincode}"
        zip_res = session.get(zip_url, timeout=5)
        zip_res.raise_for_status()
        zip_data = zip_res.json()

        return {
            "source": "Zippopotam",
            "data": {
                "Country": zip_data.get("country"),
                "State": zip_data["places"][0].get("state"),
                "PlaceName": zip_data["places"][0].get("place name"),
                "Latitude": zip_data["places"][0].get("latitude"),
                "Longitude": zip_data["places"][0].get("longitude")
            }
        }
    except Exception as e:
        raise Exception(f"Both APIs failed: {str(e)}")


@api_view(['GET'])
def getdealer(request, pincode):
    try:
        queryset = dealer.objects.filter(pincode__icontains=pincode)
        
        try:
            pincode_info = fetch_pincode_info(pincode)
        except Exception as e:
            pincode_info = None
            pincode_error = str(e)


        li = []
        for i in queryset:
            abcd = {
                "id": i.id,
                "name": i.name,
                "email":i.email,
                "mobile": i.mobile,
                "dealing_in": i.dealing,
                "min_qty": i.min_qty,
                "qty": i.max_qty,
                "other-pincodes": i.pincode,
                "pincode_data": pincode_info.get("data") if pincode_info else None,
                "source": pincode_info.get("source") if pincode_info else None,
            }
            li.append(abcd)

        if pincode_info is None:
            if not li:
                return Response({
                    'data': {
                        'status': 404,
                        'message': f'No dealers found and pincode info unavailable: {pincode_error}'
                    }
                }, status=404)
            else:
                return Response({
                    'data': {
                        'status': 206,
                        'message': f'Pincode info unavailable: {pincode_error}',
                        'dealers': li
                    }
                }, status=206)


        return Response({
            'data': {
                'status': 200,
                'dealers': li
            }
        })

    except Exception as e:
        return Response({
            'data': {
                'status': 500,
                'message': f'Internal server error: {str(e)}'
            }
        }, status=500)


@api_view(['GET'])
def dealerList(request): #View Function for Listing dealers.
    dealers = dealer.objects.all()
    serializer = dealerSerializer(dealers, many=True)
 
    return Response({ 
            'data': {
                'status': status_200,
                'dealers': serializer.data
                }
            })  

# @api_view(['GET'])
# def dealerDetail(request, pk): #View Function for getting dealers by passing id.
#     dealer_obj = dealer.objects.get(id=pk)
#     serializer = dealerSerializer(dealer_obj, many=False)
#     return Response({ 
#         'data': {
#         'status': status_200,
#         'dealers':serializer.data
#             },
#         })

@api_view(['POST'])
def adddealer(request):
    try:
        name = request.data['name']
        email = request.data['email']
        mobile = request.data['mobile']
        dealing = request.data['dealing']
        min_qty = int(request.data['min_qty'])
        max_qty = int(request.data['max_qty'])
        pincode = request.data['pincode']
        timing = request.data.get('timing', '')
        live_location = request.data.get('live_location', '')

        if min_qty < 1 or max_qty < 2:
            return Response({'error': 'Validation failed: quantity values are not valid'}, status=400)

        obj = dealer(
            name=name,
            email=email,
            mobile=mobile,
            dealing=dealing,
            min_qty=min_qty,
            max_qty=max_qty,
            pincode=pincode,
            timing=timing,
            live_location=live_location
        )
        obj.save()

        return Response({
            "status": "success",
            "message": "Dealer Created Successfully",
            "dealer_id": obj.id
        })

    except Exception as e:
        return Response({
            'data': {
                'error': str(e)  # ✅ FIXED: convert to string
            }
        }, status=500)

# @api_view(['PUT'])
# def dealerUpdate(request,pk): #View Function for Updating dealers.
#     try:
#         deals = dealer.objects.get(id=pk)
#         serializer = dealerSerializer(instance=deals, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#         return Response(serializer.data)
#     except:
#         return Response({           
#                 'data': {
#                     'error': "Incorrect Data"
#                     },
#                 })

# @api_view(['DELETE'])
# def dealerDelete(request,pk): #View Function for Deleting dealers.
#     try:
#         deals = dealer.objects.get(id=pk)
#         deals.delete()
#         return Response('dealer Successfully Deleted')
#     except:
#         return Response({           
#             'data': {
#                 'error': "Incorrect Data"
#                 },
#             })


# class RequestInquiryGet(APIView):
#     def get(self, request, dealer_id):
#         dealer_id = dealer_id
#         item = RequestInquiry.objects.filter(dealer_id=dealer_id)
#         serializer = RequestInquiryGetSerializer(item, many = True)
#         return Response(serializer.data)

class RequestInquiryGet(APIView):
    def get(self, request, email):
        try:
            dealer_instance = dealer.objects.get(email=email)
            item = RequestInquiry.objects.filter(dealer_id=dealer_instance)
            serializer = RequestInquiryGetSerializer(item, many=True)
            return Response(serializer.data)
        except dealer.DoesNotExist:
            return Response({"error": "Dealer not found"}, status=404)

class RequestInquiryPost(APIView):
    serializer_class = RequestInquiryPostSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            inquiry = serializer.save()

            dealer_id = request.data.get("dealer_id")
            try:
                dealer_obj = dealer.objects.get(id=dealer_id)
                dealer_email = dealer_obj.email
            except dealer.DoesNotExist:
                return Response({"error": "Dealer not found"}, status=404)

            # Email content
            subject = "New Request Inquiry"

            context = {
                "dealer_name": dealer_obj.name,
                "customer_name": inquiry.customer_name,  # Replace with your actual logo URL
                "site": f"{current_site_frontend}"    # Replace with your actual dashboard URL
            }

            html_content = render_to_string("emails/request_inquiry.html", context)

            text_content = (
                f"Dear {dealer_obj.name},\n\n"
                f"You have received a new inquiry:\n\n"
                f"Customer Name: {inquiry.customer_name}\n"
                f"Phone: {inquiry.phone}\n"
                f"Email: {inquiry.email}\n"
                f"Item: {inquiry.itemName}\n"
                f"Quantity: {inquiry.quantity}\n"
                f"Description: {inquiry.description}\n\n"
                "Please log in to your dashboard to respond."
            )

            try:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[dealer_email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send()

                logger.info(f"HTML email sent to {dealer_email}")
            except BadHeaderError:
                return Response({"error": "Invalid header found."}, status=400)
            except Exception as e:
                logger.error(f"Email sending failed: {e}")
                return Response({"error": f"Failed to send email: {str(e)}"}, status=500)

            return Response(serializer.data)        
# class Getdealers(generics.ListAPIView): #View Function for getting dealers by Longitude & Latitude.
#     queryset = dealer.objects.all()
#     serializer_class = dealerSerializer
#     filter_backends = (DjangoFilterBackend,)
#     def get(self, request):
#         """Get dealers that are at least 10km or less from a users location"""
#         longitude = request.GET.get("lon", None)
#         latitude = request.GET.get("lat", None)
#         user_distance = request.GET.get("distance", None)
#         # user_distance = 1

#         try:
#             if any((longitude, latitude , user_distance)):
#             # if longitude and latitude:
#                 user_location = Point(float(longitude), float(latitude), srid=4326)           
#                 closest_dealers = dealer.objects.filter(
#                     # geom__distance_lte=(user_location, D(km=10))
#                     geom__distance_lte=(user_location, D(km=user_distance))
#                 ).order_by('id') #filtering dealers within 10 KM Radius.
                
#                 li=[]
#                 for dealer in closest_dealers.annotate(geom__distance_lte=Distance('geom', user_location)): #Getting Distance from Current Location of Customer to dealers location.
#                     pqr=dealer.geom__distance_lte.km 
#                     dis = str("{:.2f}".format(pqr)) + " KM"
#                     abcd = {
#                         "id":dealer.id,
#                         "name":dealer.name,
#                         "mobile": dealer.mobile,
#                         "old":dealer.old    ,          
#                         "new":dealer.new ,
#                         "other":dealer.other ,
#                         "min_qty":dealer.min_qty ,
#                         "max_qty":dealer.max_qty,
#                         "pincode":dealer.pincode,
#                         "distance":dis,
#                     }

#                     li.append(abcd)
#                 return Response({           
#                     'data': {
#                         'status': status_200,
#                         'dealers': li
#                         },
#                     })     
#         except:
#             return Response({           
#                     'data': {
#                         'status': status_400,
#                         'error': "Incorrect URL"
#                         },
#                     })
