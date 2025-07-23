from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AddressSerializer
from .models import Address

class AddressCreateView(APIView):
    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyDigiPIN(APIView):
    def get(self, request, digipin):
        try:
            address_obj = Address.objects.get(digipin=digipin)
            serializer = AddressSerializer(address_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Address.DoesNotExist:
            return Response({'error': 'Invalid DigiPIN'}, status=status.HTTP_404_NOT_FOUND)