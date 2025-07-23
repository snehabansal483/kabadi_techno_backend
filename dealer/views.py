#from django.contrib.gis.geos import Point
#from django.contrib.gis.measure import D
#from django.contrib.gis.db.models.functions import Distance
from django.http import HttpResponse
# from django_filters.rest_framework import DjangoFilterBackend
#from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
import json
from .models import dealer
import requests

status_200=status.HTTP_200_OK
status_400=status.HTTP_400_BAD_REQUEST

def dealerHome(request):
    html = "<html><head><title>Kabadi Techno API</title></head><body><center><b><p>Kabadi Techno API</p> </center></body></html>"
    return HttpResponse(html)


import requests
import json

@api_view(['GET'])
def getdealer(request, pincode):
    try:
        queryset = dealer.objects.filter(pincode__icontains=pincode)

        ENDPOINT = "https://api.postalpincode.in/pincode/"
        response1 = requests.get(ENDPOINT + str(pincode), timeout=5)
        response1.raise_for_status()
        pincode_info = response1.json()

        # Handle invalid pincode or no results
        if not pincode_info or pincode_info[0]['PostOffice'] is None:
            return Response({
                'data': {
                    'status': 404,
                    'message': 'Invalid or unserviceable pincode'
                }
            }, status=404)

        # returnPincodeData = pincode_info[0]['PostOffice'][0]

        # district = returnPincodeData['District']
        # region = returnPincodeData['Region']
        # circle = returnPincodeData['Circle']
        # state = returnPincodeData['State']
        # country = returnPincodeData['Country']
        # pincode1 = returnPincodeData['Pincode']

        li = []
        for i in queryset:
            abcd = {
                "id": i.id,
                "name": i.name,
                "mobile": i.mobile,
                "dealing_in": i.dealing,
                "min_qty": i.min_qty,
                "qty": i.max_qty,
                "other-pincodes": i.pincode,
                "pincode_data":pincode_info
            }
            li.append(abcd)

        return Response({
            'data': {
                'status': 200,
                'dealers': li
            }
        })

    except requests.RequestException as e:
        return Response({
            'data': {
                'status': 500,
                'message': f'Error while fetching pincode info: {str(e)}'
            }
        }, status=500)

    except Exception as e:
        # Catch any other unhandled exceptions
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
def adddealer(request): #View Function for Adding dealers.
    try:
        name = request.data['name']
        mobile = request.data['mobile']
        dealing = request.data['dealing']
        min_qty = request.data['min_qty']
        max_qty = request.data['max_qty']
        pincode = request.data['pincode']
        timing = request.data['timing']
        live_location = request.data['live_location']
        if min_qty < 1 or max_qty < 2:
            return Response('Validation Occured')
        else:
            obj = dealer(name=name,mobile=mobile,dealing=dealing,min_qty=min_qty,max_qty=max_qty,pincode=pincode,timing=timing, live_location=live_location)
            # ,geom=geom)
            obj.save()

        return Response('dealer Created Successfully')
    except Exception as e:
        return Response({           
                'data': {
                    'error': e
                    },
                })
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


class RequestInquiryGet(APIView):
    def get(self, request, dealer_id):
        dealer_id = dealer_id
        item = RequestInquiry.objects.filter(dealer_id=dealer_id)
        serializer = RequestInquiryGetSerializer(item, many = True)
        return Response(serializer.data)

class RequestInquiryPost(APIView):
    serializer_class = RequestInquiryPostSerializer
    def post(self, request):
        serializer = RequestInquiryPostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
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
