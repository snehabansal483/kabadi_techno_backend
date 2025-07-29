from urllib import response
from rest_framework.views import APIView
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from .serializers import *
from .models import PriceList
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.
class GetPrice(APIView):
    def get(self, request, dealer_id):
        dealer_id = dealer_id
        price = PriceList.objects.filter(dealer_id=dealer_id)
        serializer = PriceListGetSerializer(price, many = True)
        return Response(serializer.data)

class GetPrice(APIView):
    def get(self, request, dealer_id):
        dealer_id = dealer_id
        price = PriceList.objects.filter(dealer_id=dealer_id)
        serializer = PriceListGetSerializer(price, many = True)
        return Response(serializer.data)
        
class AddPrice(APIView):
    serializer_class = PriceListPostSerializer
    def post(self, request):
        serializer = PriceListPostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            subcategory = request.data['subcategory']
            dealer = request.data['dealer']
            pincode = request.data['pincode']
            price = request.data['price']
            if PriceList.objects.filter(subcategory = subcategory, dealer = dealer, pincode = pincode).exists():
                return Response({'unsuccessful': 'You can only set price once for a single pincode'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                serializer.save()
                return Response(serializer.data)

class UpdatePrice(APIView):
    serializer_class = UpdatePriceSerializer
    def post(self, request):
        serializer = UpdatePriceSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            subcategory = request.data['subcategory']
            dealer = request.data['dealer']
            price = request.data['price']
            pincode = request.data['pincode']
            if PriceList.objects.filter(subcategory = subcategory, dealer = dealer, pincode = pincode).exists():
                subcat = PriceList.objects.get(subcategory = subcategory, dealer = dealer, pincode = pincode)
                subcat.price = price
                subcat.save()
                context = {
                    'dealer' : subcat.dealer.auth_id.full_name,
                    'category_name' : subcat.category_name,
                    'subcategory_name' : subcat.subcategory_name,
                    'price' : subcat.price,
                    'unit' : subcat.unit,
                    'pincode' : subcat.pincode,}
                return Response(context)
            else:
                return Response({'unsuccessful': 'The dealer has not added the price for this product or for this pincode'}, status=status.HTTP_404_NOT_FOUND)

class DeletePrice(APIView):
    serializer_class = DeletePriceSerializer
    def post(self, request):
        serializer = DeletePriceSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            subcategory = request.data['subcategory']
            dealer = request.data['dealer']
            pincode = request.data['pincode']
            if PriceList.objects.filter(subcategory = subcategory, dealer = dealer, pincode = pincode).exists():
                subcat = PriceList.objects.get(subcategory = subcategory, dealer = dealer, pincode = pincode)
                subcat.delete()
                return Response({'successful': 'The subcategory price added by the dealer for this pincode has been successfully removed'}, status=status.HTTP_200_OK)
            else:
                return Response({'unsuccessful': 'The dealer has not added the price for this product or for this pincode'}, status=status.HTTP_404_NOT_FOUND)


class RequestAddCategory(APIView):
    serializer_class = AddCategorySerializer
    def post(self, request):
        serializer = AddCategorySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

class GetRequestAddCategory(APIView):
    def get(self, request, dealer_id):
        dealer_id = dealer_id
        req = add_category.objects.filter(dealer_id=dealer_id)
        serializer = RequestAddCategoryGetSerializer(req, many = True)
        return Response(serializer.data)

class AddDocuments(APIView):
    serializer_class = DocumentsSerializer
    def post(self, request):
        serializer = DocumentsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

class GetDocuments(APIView):
    def get(self, request, dealer_id):
        req = documents.objects.filter(dealer_id=dealer_id)
        serializer = GetDocumentsSerializer(req, many=True)
        return Response(serializer.data)


class AddPincodes(APIView):
    serializer_class = AddPincodesSerializer
    def post(self, request):
        serializer = AddPincodesSerializer(data = request.data)
        dealer_id = request.data['dealer_id']
        if serializer.is_valid(raise_exception=True):
            if GetPincodes.objects.filter(dealer_id = dealer_id).exists():
                return Response({'unsuccessful': 'This dealer already has a Pincode table created'}, status=status.HTTP_306_RESERVED)
            serializer.save()
            return Response(serializer.data)

class RequestToAddPincodes(APIView):
    serializer_class = RequesttoAddPincodesSerializer
    def post(self, request):
        serializer = RequesttoAddPincodesSerializer(data = request.data)
        dealer_id = request.data['dealer_id']
        addrequest = request.data['addrequest']
        if serializer.is_valid(raise_exception = True):
            if GetPincodes.objects.filter(dealer_id = dealer_id).exists():
                pins = GetPincodes.objects.get(dealer_id=dealer_id)
                if pins.addrequest is None:
                    pins.addrequest = addrequest
                    pins.save()
                    return Response(serializer.data)
                else:
                    return Response({'Not Acceptable': 'You have already submitted a request. Please Retry After the previous request is processed'})
            else:
                return Response({'unsuccessful': 'The dealer is not registered in pincodes table'})

class GetallPincodes(APIView):
    def get(self, request, dealer_id):
        dealer_id = dealer_id
        try:
            pins = GetPincodes.objects.get(dealer_id=dealer_id)
            kt_id = pins.dealer_id.kt_id
            serializer = GetallPincodesSerializer(pins, many = True)
            context = {
                'dealer_id': kt_id,
            }
            if pins.pincode1:
                context.update({'Pincode 1': pins.pincode1})
            if pins.pincode2:
                context.update({'Pincode 2': pins.pincode2})
            if pins.pincode3:
                context.update({'Pincode 3': pins.pincode3})
            if pins.pincode4:
                context.update({'Pincode 4': pins.pincode4})
            if pins.pincode5:
                context.update({'Pincode 5': pins.pincode5})
            if pins.pincode6:
                context.update({'Pincode 6': pins.pincode6})
            if pins.pincode7:
                context.update({'Pincode 7': pins.pincode7})
            if pins.pincode8:
                context.update({'Pincode 8': pins.pincode8})
            if pins.pincode9:
                context.update({'Pincode 9': pins.pincode9})
            if pins.pincode10:
                context.update({'Pincode 10': pins.pincode10})
            if pins.pincode11:
                context.update({'Pincode 11': pins.pincode11})
            return Response(context)
        except ObjectDoesNotExist:
            return Response({'Not Found': 'There is no such dealer id that has pincodes registered'}, status=status.HTTP_404_NOT_FOUND)

class No_of_pincodes(APIView):
    def get(self, request, dealer_id):
        try:
            pins = GetPincodes.objects.get(dealer_id=dealer_id)
            serializer = No_of_pincodesSerializer(pins)
            pin_nos = 0
            if pins.pincode1:
                pin_nos += 1
            if pins.pincode2:
                pin_nos += 1
            if pins.pincode3:
                pin_nos += 1
            if pins.pincode4:
                pin_nos += 1
            if pins.pincode5:
                pin_nos += 1
            if pins.pincode6:
                pin_nos += 1
            if pins.pincode7:
                pin_nos += 1
            if pins.pincode8:
                pin_nos += 1
            if pins.pincode9:
                pin_nos += 1
            if pins.pincode10:
                pin_nos += 1
            if pins.pincode11:
                pin_nos += 1

            pins.no_of_pincodes = pin_nos
            pins.save()
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({'Not Found': 'There is no such dealer id that has pincodes registered'}, status=status.HTTP_404_NOT_FOUND)



class UpdatePincodes(APIView):
    serializer_class = UpdatePincodesSerializer

    def post(self, request):
        serializer = UpdatePincodesSerializer(data=request.data)
        dealer_id = request.data.get('dealer_id')
        pincode1 = request.data.get('pincode1')
        pincode2 = request.data.get('pincode2')
        pincode3 = request.data.get('pincode3')
        pincode4 = request.data.get('pincode4')
        pincode5 = request.data.get('pincode5')
        pincode6 = request.data.get('pincode6')
        pincode7 = request.data.get('pincode7')
        pincode8 = request.data.get('pincode8')
        pincode9 = request.data.get('pincode9')
        pincode10 = request.data.get('pincode10')
        pincode11 = request.data.get('pincode11')  # Will be None if not present

        if serializer.is_valid(raise_exception=True):
            if GetPincodes.objects.filter(dealer_id=dealer_id).exists():
                pins = GetPincodes.objects.get(dealer_id=dealer_id)
                pins.pincode1 = pincode1
                pins.pincode2 = pincode2
                pins.pincode3 = pincode3
                pins.pincode4 = pincode4
                pins.pincode5 = pincode5
                pins.pincode6 = pincode6
                pins.pincode7 = pincode7
                pins.pincode8 = pincode8
                pins.pincode9 = pincode9
                pins.pincode10 = pincode10
                pins.pincode11 = pincode11  # Will be None if not sent

                pins.save()
                return Response(serializer.data)
            else:
                return Response({'unsuccessful': 'The dealer is not registered in pincodes table yet'})
class SearchSubcategoryByPincode(APIView):
    def get(self, request, pincode):
        try:
            # if keyword:
            subcategory_nms = PriceList.objects.filter(pincode = pincode)
            # subcategory_nms = PriceList.objects.order_by('-created_date').filter(Q(subcategory_name__icontains=keyword) | Q(category_name__icontains=keyword))

            subcategory_count = subcategory_nms.count()
            context = {
            # 'subcategory': subcategory_nms,
            
            'subcategory_count': subcategory_count,
            }
            serializer = SearchSubcategoryByPincodeSerializer(subcategory_nms, many = True)
            new_serializer_data = list(serializer.data)
            new_serializer_data.append(context)
            return Response(new_serializer_data, status=status.HTTP_302_FOUND)
        except ObjectDoesNotExist:
            return Response({'Not Found': 'There are no subcategories available on this pincode'}, status=status.HTTP_404_NOT_FOUND)
